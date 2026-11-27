import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import run_index


class ConfirmCliTests(unittest.TestCase):
    def test_start_passes_viewed_digest_and_draft_only_after_confirmation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "spec.json").write_text(json.dumps(
                {"repository": str(root), "work_root": str(root / "thread")}))
            idx = root / "index.json"
            idx.write_text(json.dumps({"projects": {"p": {"repository": ".", "runs": {
                "r": {"spec": "spec.json", "thread": "thread"}}}}}))
            args = ["--index", str(idx), "--project", "p", "--run", "r", "start",
                    "--draft", str(root / "draft.json"), "--draft-digest", "a"*64]
            with patch("backend.run", return_value=0) as send:
                with self.assertRaises(SystemExit):
                    run_index.main(args)
                send.assert_not_called()
                self.assertEqual(run_index.main(args + ["--confirm-execute"]), 0)
                self.assertEqual(send.call_args.args[1][-4:], args[-4:])
