import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import backend


class EvidenceRequestTests(unittest.TestCase):
    def setUp(self):
        self.repo = Path(__file__).resolve().parent
        self.awo = Path(os.environ.get("MAID_AWO_ROOT", self.repo.parent / "agent-workflow-orchestrator"))
        sys.path.insert(0, str(self.awo / "scripts"))
        from test_evidence_draft import DraftTests
        setup = DraftTests()
        setup.setUp()
        self.addCleanup(setup.doCleanups)
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.folder = Path(tmp.name)
        self.target = self.folder / "target.json"
        self.target.write_text(json.dumps(setup.config))
        self.out = self.folder / "draft.json"
        self.config = setup.config

    def cli(self, *args, stdin="", root=None):
        return subprocess.run([sys.executable, "-B", str(self.repo / "maid.py"), *map(str,args)],
                              input=stdin, capture_output=True, encoding="utf-8", timeout=60,
                              env=dict(os.environ, PYTHONUTF8="1", MAID_AWO_ROOT=str(root or self.awo)))

    def test_query_keep_cancel_empty(self):
        args = ["request","--target",self.target,"--out",self.out]
        for query, choice in [("latency","cancel"),("xyzzy","all")]:
            p = self.cli(*args,"--query",query,"--keep",choice)
            self.assertEqual(p.returncode,0,p.stderr)
            self.assertFalse(self.out.exists())
        p = self.cli(*args,"--query","latency","--keep","2")
        self.assertEqual(p.returncode,0,p.stderr)
        draft = json.loads(self.out.read_text())
        self.assertEqual(len(draft["items"]),1)
        self.assertFalse(draft["dispatched"])

    def test_study_original_to_draft(self):
        import evidence_draft
        hit = evidence_draft.handle(self.config, {"query":"latency"})["items"][0]["ref"]
        lib = self.folder / "library.json"
        lib.write_text(json.dumps({"sources":{"paper":{"doc_id":hit["source_id"]}},
                       "awo":{"root":self.config["root"],"state":self.config["state"],
                              "token_file":self.config["doc_token_file"]}}))
        args = ["study","--library",lib,"--source","paper","--known","time","--goal","latency",
                "--target",self.target,"--draft-out",self.out]
        bad = self.cli(*args, stdin="draft AI analogy\n")
        self.assertNotEqual(bad.returncode,0)
        self.assertFalse(self.out.exists())
        p = self.cli(*args, stdin="draft 1\nquit\n")
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual(json.loads(self.out.read_text())["items"][0]["excerpt_sha256"], hit["excerpt_sha256"])

    def test_old_backend_requires_upgrade_only_for_query(self):
        old = self.folder / "old"
        (old / "scripts").mkdir(parents=True)
        entry = old / "scripts/awo_app.py"
        entry.write_text("import sys,json\nprint(json.dumps({'protocol':1,'capabilities':['maid','profile']}) "
                         "if sys.argv[1]=='capabilities' else repr(sys.argv[2:]))")
        for args in [("request","--material","a"),("request",)]:
            p = self.cli(*args, root=old)
            self.assertEqual(p.returncode,0,p.stderr)
            self.assertEqual(p.stdout.strip(), repr(list(args)))
        p = self.cli("request","--query","latency",root=old)
        self.assertNotEqual(p.returncode,0)
        self.assertIn("upgrade AWO",p.stderr)
