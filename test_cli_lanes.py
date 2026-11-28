"""Offline unit tests for MAID named CLI lanes support."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import lanes
import run_index


SAMPLE_LANES = {
    "schema_version": 1,
    "lanes": {
        "codex-default": {
            "cli": "codex",
            "executable": "C:/tools/codex.exe",
            "default_args": ["exec"],
            "allowed_roles": ["executor"],
        },
        "claude-flash": {
            "cli": "claude",
            "executable": "C:/tools/claude.exe",
            "default_args": ["--print"],
            "allowed_roles": ["executor"],
        },
        "reviewer-independent": {
            "cli": "claude",
            "executable": "C:/tools/claude.exe",
            "default_args": ["--print"],
            "allowed_roles": ["reviewer"],
        },
    },
}


class MaidCliLanesTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.lanes_file = self.root / "lanes.json"
        self.lanes_file.write_text(json.dumps(SAMPLE_LANES), encoding="utf-8")

        self.awo_root = self.root / "awo"
        entry = self.awo_root / "scripts/awo_app.py"
        entry.parent.mkdir(parents=True)
        entry.write_text(
            "import json, sys\n"
            "if sys.argv[1] == 'capabilities':\n"
            "    print(json.dumps({'protocol': 1, 'capabilities': ['profile', 'maid', 'recover']}))\n"
            "else:\n"
            "    print(json.dumps(sys.argv[1:]))\n",
            encoding="utf-8",
        )

    def _call_maid(self, *args):
        return subprocess.run(
            [sys.executable, "-B", str(ROOT / "maid.py"), *args],
            env=dict(os.environ, MAID_AWO_ROOT=str(self.awo_root)),
            capture_output=True,
            text=True,
            timeout=10,
        )

    def test_request_with_lane_resolves_and_preserves_profile_compatibility(self):
        res_lane = self._call_maid(
            "request", "--lanes", str(self.lanes_file), "--lane", "codex-default", "--thread", "t1"
        )
        self.assertEqual(res_lane.returncode, 0, res_lane.stderr)
        forwarded = json.loads(res_lane.stdout)
        self.assertEqual(forwarded, ["maid", "request", "--lanes", str(self.lanes_file), "--lane", "codex-default", "--thread", "t1"])

        res_profile = self._call_maid("request", "--profile", "p.json", "--thread", "t1")
        self.assertEqual(res_profile.returncode, 0, res_profile.stderr)
        self.assertEqual(json.loads(res_profile.stdout), ["maid", "request", "--profile", "p.json", "--thread", "t1"])

    def test_request_rejects_reviewer_only_lane_and_self_review(self):
        with self.assertRaisesRegex(lanes.LaneError, "not allowed for role"):
            lanes.resolve_lane(self.lanes_file, "reviewer-independent")
        with self.assertRaisesRegex(lanes.LaneError, "self-review"):
            lanes.resolve_lane(self.lanes_file, "codex-default", peer_lane="codex-default")

    def test_doctor_lanes_validates_file(self):
        res = self._call_maid("doctor", "--lanes", str(self.lanes_file))
        self.assertEqual(res.returncode, 0, res.stderr)
        data = json.loads(res.stdout)
        self.assertTrue(data["valid"])
        self.assertFalse(data["authorized"])
        self.assertIn("codex-default", data["lanes"])

    def test_run_index_reassign_lane(self):
        thread = self.root / "repair-thread"
        (self.root / "spec.json").write_text(
            json.dumps({"repository": str(self.root), "work_root": str(thread)}),
            encoding="utf-8",
        )
        idx = self.root / "index.json"
        idx.write_text(
            json.dumps({
                "projects": {
                    "p": {
                        "repository": ".",
                        "runs": {"r": {"spec": "spec.json", "thread": thread.name}},
                    }
                }
            }),
            encoding="utf-8",
        )
        version = "ab" * 32
        with patch("backend.run", return_value=0) as send:
            run_index.main([
                "--index", str(idx),
                "--project", "p",
                "--run", "r",
                "recover",
                "--handoff", "reassign",
                "--state-version", version,
                "--lanes", str(self.lanes_file),
                "--reassign-lane", "claude-flash",
                "--confirm-execute",
            ])
            send.assert_called_once_with(
                "recover",
                [
                    "--thread", str(thread),
                    "--handoff", "reassign",
                    "--state-version", version,
                    "--recipient", "claude-flash",
                    "--lanes", str(self.lanes_file), "--reassign-lane", "claude-flash",
                    "--confirm-execute",
                ],
            )


if __name__ == "__main__":
    unittest.main()
