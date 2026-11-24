"""Client routing exercised through actual CLI subprocesses; no model calls."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent


class Routing(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        self.entry = self.root / "scripts/awo_app.py"
        self.entry.parent.mkdir()
        self.marker = self.root / "legacy-called"
        old = self.root / "apps/maid/maid.py"
        old.parent.mkdir(parents=True)
        old.write_text(f"open({str(self.marker)!r}, 'w').close()", encoding="utf-8")
        for name in ("secretary_adapter", "project_entry"):
            (self.root / f"scripts/{name}.py").touch()

    def call(self, script, *args):
        return subprocess.run([sys.executable, "-B", str(ROOT / script), *args],
                              env=dict(os.environ, MAID_AWO_ROOT=str(self.root)),
                              capture_output=True, text=True, timeout=10)

    def test_public_preserves_argv_and_exit(self):
        self.entry.write_text(
            "import json, sys\nif sys.argv[1]=='capabilities':\n"
            " print(json.dumps(dict(protocol=1,capabilities=['profile','maid','future'])))\n"
            "else:\n print(json.dumps(sys.argv[1:]))\n sys.exit(23)\n", encoding="utf-8")
        for program, action in (("configure.py", "profile"), ("maid.py", "maid")):
            result = self.call(program, "--arg", "two words")
            self.assertEqual(result.returncode, 23)
            self.assertEqual(json.loads(result.stdout), [action, "--arg", "two words"])
        self.assertFalse(self.marker.exists())

    def test_rejects_bad_handshake_even_with_legacy_layout(self):
        cases = ["raise SystemExit(3)", "print('invalid')", "print('[]')"]
        for protocol, caps in ((True, ["profile","maid"]), (2, ["profile","maid"]),
                               (1, ["maid"]), (1, "profile maid"), (1, ["maid","profile",0])):
            cases.append(f"print({json.dumps(dict(protocol=protocol, capabilities=caps))!r})")
        for body in cases:
            with self.subTest(body=body):
                self.entry.write_text(body, encoding="utf-8")
                result = self.call("maid.py", "doctor")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("capabilities check failed", result.stderr)
                self.assertFalse(self.marker.exists())

    def test_legacy_requires_complete_layout(self):
        self.assertEqual(self.call("maid.py", "doctor").returncode, 0)
        self.assertTrue(self.marker.exists())
        (self.root / "scripts/project_entry.py").unlink()
        self.assertIn("lacks scripts/project_entry.py", self.call("maid.py", "doctor").stderr)
