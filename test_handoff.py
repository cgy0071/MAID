"""Offline operator-to-backend boundary tests for interruption recovery."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import run_index
from continuity import render


class Handoff(unittest.TestCase):
    def setUp(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        self.root = Path(td.name)
        self.thread = self.root / "repair-thread"
        (self.root / "spec.json").write_text(json.dumps({
            "repository": str(self.root), "work_root": str(self.thread)}))
        idx = self.root / "index.json"
        idx.write_text(json.dumps({"projects": {"p": {"repository": ".", "runs": {
            "r": {"spec": "spec.json", "thread": self.thread.name}}}}}))
        self.args = ["--index", str(idx), "--project", "p", "--run", "r"]

    def test_diagnosis_and_handoff_are_separate_and_preserve_target(self):
        version = "ab" * 32
        with patch("backend.run", return_value=0) as send:
            run_index.main(self.args + ["recover"])
            send.assert_called_once_with("recover", ["--thread", str(self.thread)])
            for action in ("continue", "manual", "reassign"):
                flags = ["--handoff", action, "--state-version", version, "--recipient", "operator"]
                run_index.main(self.args + ["recover", "--rework-attempt", *flags, "--confirm-execute"])
                send.assert_called_with("recover", ["--thread", str(self.thread), *flags,
                                                    "--rework-attempt", "--confirm-execute"])

    def test_incomplete_or_misplaced_action_never_invokes_backend(self):
        flags = ["--handoff", "manual", "--state-version", "ab" * 32, "--recipient", "operator"]
        with patch("backend.run") as send, contextlib.redirect_stderr(io.StringIO()):
            for cmd in (["recover", *flags], ["recover", *flags[:-2], "--confirm-execute"],
                        ["start", *flags, "--confirm-execute"], ["status", "--recipient", "x"]):
                with self.subTest(cmd=cmd), self.assertRaises(SystemExit):
                    run_index.main(self.args + cmd)
            send.assert_not_called()

    def test_unverified_writer_only_offers_inspection_despite_dirty_workspace(self):
        report = {"handoff": dict(workspace="WORK", workspace_available=True, head="REV",
                    state_version="HASH", last_receipted_step="workspace_ready",
                    writer_isolation="unverified", allowed_actions=[], session={"resume": False},
                    committed_changes=[["M", "first.md"]], uncommitted_changes=[" M second.md"])}
        text = render({"result": {"recovery": report}})
        for value in ("工作区已就绪", "WORK", "REV", "HASH", "first.md", "second.md",
                      "仅查看与核查", "未能证实已停写", "未确认可恢复"):
            self.assertIn(value, text)
        self.assertNotIn("换人重派", text)

    def test_handoff_receipt_is_not_an_acceptance(self):
        text = render({"result": {"recovery": dict(action_id="abc", action="reassign",
               recipient="replacement", thread="child", checkpoint_commit="REV", accepted=False)}})
        for value in ("换人重派", "replacement", "child", "REV", "本回执只证明交接"):
            self.assertIn(value, text)
        self.assertNotIn("审核通过", text)
