import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import maid
import study


class StudyTests(unittest.TestCase):
    def setUp(self):
        from pypdf import PdfWriter
        from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.pdf = self.root / "paper.pdf"
        writer = PdfWriter()
        writer.add_blank_page(200, 200)
        for page, phrase in [(writer.pages[0], "Introduction"), (writer.add_blank_page(200, 200),
                                                               "Latency measured 13 milliseconds.")]:
            stream = DecodedStreamObject()
            stream.set_data(("BT /F1 12 Tf 10 100 Td (" + phrase + ") Tj ET").encode())
            font = DictionaryObject({NameObject("/Type"): NameObject("/Font"),
                                     NameObject("/Subtype"): NameObject("/Type1"),
                                     NameObject("/BaseFont"): NameObject("/Helvetica")})
            page[NameObject("/Resources")] = DictionaryObject({NameObject("/Font"):
                DictionaryObject({NameObject("/F1"): font})})
            page[NameObject("/Contents")] = writer._add_object(stream)
        writer.write(self.pdf)
        self.note = self.root / "methods.md"
        self.note.write_bytes(b"# Methods\r\nThroughput counts completed samples.\n")
        self.cfg = self.root / "personal-library.json"
        self.original = {path: hashlib.sha256(path.read_bytes()).hexdigest()
                         for path in (self.pdf, self.note)}
        self.grants = {p.stem: {"file": str(p), "sha256": sha} for p, sha in self.original.items()}
        self.configure()
        self.lib = study.Library(self.cfg)
        self.session = study.Study(self.lib, ["paper", "methods"], "units", "latency")

    def configure(self):
        self.cfg.write_text(json.dumps({"sources": self.grants}), encoding="utf-8")

    def tearDown(self):
        for path, sha in self.original.items():
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), sha)

    def test_read_follow_up_feedback_and_revoke(self):
        with patch("backend.run", side_effect=AssertionError("unexpected dispatch")) as run:
            report = self.session.lesson("latency")
            row = report["原文已确认结论"][0]
            self.assertEqual(row["locator"]["physical_page"], 2)
            self.assertEqual(row["pinned_revision"]["sha256"], self.original[self.pdf])
            self.assertEqual(self.session.original(1), "Latency measured 13 milliseconds.")
            self.assertIn("核对原文", self.session.answer(1, "13 milliseconds"))
            note = self.session.lesson("throughput")["原文已确认结论"][0]
            loc = note["locator"]
            self.assertEqual(self.note.read_bytes()[loc["byte_start"]:loc["byte_end"]].decode(), note["quote"])
            del self.grants["methods"]
            self.configure()
            with self.assertRaises(PermissionError):
                self.session.original(1)
            with self.assertRaises(PermissionError):
                self.session.lesson("throughput")
            run.assert_not_called()
        self.assertFalse(self.lib.notes.exists())

    def test_notes_exclude_material_and_ai_transcript(self):
        profile = "trusted-test-profile"
        self.session.tutor = profile
        def tutor(selected, root, model, prompt):
            for value in (self.session.known, self.session.goal, "Latency measured"):
                self.assertIn(value, prompt)
            return {"response": "Think of waiting for a bus."}
        with patch("secretary_adapter.reply", side_effect=tutor):
            report = self.session.lesson("latency")
        self.assertEqual(report["AI 补充解释或类比"], "Think of waiting for a bus.")
        self.assertNotIn("bus", str(report["原文已确认结论"]))
        with self.assertRaises(ValueError):
            self.session.save(self.session.original(1))
        saved = Path(self.session.save("I will compare time and rate separately."))
        self.assertEqual(saved.parent, self.lib.notes)
        raw = saved.read_text(encoding="utf-8")
        for private in ("Latency measured", "waiting for a bus", str(self.pdf)):
            self.assertNotIn(private, raw)
        self.assertEqual(json.loads(raw)["来源指针"][0][1]["locator"]["physical_page"], 2)
        self.assertEqual(self.session.lesson("xyzzy")["原文已确认结论"], "本资料未说明")

    def test_actual_cli_exit_writes_nothing(self):
        before = set(self.root.iterdir())
        run = subprocess.run([sys.executable, "-B", str(Path(maid.__file__)), "study",
                              "--library", str(self.cfg), "--source", "paper",
                              "--known", "time", "--goal", "latency"],
                             input="open 1\nanswer 1 milliseconds\nquit\n",
                             capture_output=True, encoding="utf-8",
                             env=dict(os.environ, PYTHONUTF8="1"), timeout=30)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn('"physical_page": 2', run.stdout)
        self.assertEqual(before, set(self.root.iterdir()))

    def test_published_document_uses_current_project_grant(self):
        from test_project_retrieve import ProjectRetrieveTests
        import service_access
        fixture = ProjectRetrieveTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        key = fixture.publish("Timing report\nLatency is 13 ms.")
        env = fixture.env
        token = env.f.issue("reviewer", "planner", knowledge_id=key)
        token_path = self.root / "reader.token"
        token_path.write_text(token, encoding="utf-8")
        self.cfg.write_text(json.dumps({"sources": {"published": {"doc_id": key}},
            "awo": {"state": str(env.state), "root": str(env.root), "token_file": str(token_path)}}))
        session = study.Study(self.lib, ["published"], "time", "Latency")
        hit = session.lesson("Latency")["原文已确认结论"][0]
        self.assertEqual(hit["locator"]["char_start"], len("Timing report\n"))
        who = service_access.principal(env.state, env.root, token)
        service_access.revoke_token(env.state, *env.f.f.actor, env.f.f.envelope(
            "access.revoke", {"token_id": who["token_id"], "expected_revision": 1}))
        with self.assertRaises(service_access.service.ServiceError):
            session.original(1)
