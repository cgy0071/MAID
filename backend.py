"""Select AWO's public interface or its pre-protocol compatibility adapter."""
import json
import os
from pathlib import Path
import subprocess
import sys


def select(required=None):
    default = Path(__file__).resolve().parent.parent / "agent-workflow-orchestrator"
    root = Path(os.environ.get("MAID_AWO_ROOT", default)).resolve()
    entry = root / "scripts/awo_app.py"
    if not os.path.lexists(entry):
        if required:
            raise SystemExit(f"Incompatible AWO: legacy layout does not advertise {required}.")
        for rel in ("apps/maid/maid.py", "scripts/secretary_adapter.py", "scripts/project_entry.py"):
            if not (root / rel).is_file():
                raise SystemExit(f"Incompatible AWO: {root} lacks {rel}. See README or set MAID_AWO_ROOT.")
        return root, None
    try:
        proc = subprocess.run([sys.executable, "-B", str(entry), "capabilities"],
                              capture_output=True, check=True, timeout=15)
        info = json.loads(proc.stdout.decode("utf-8"))
        if not isinstance(info, dict) or type(info.get("protocol")) is not int or info["protocol"] != 1:
            raise ValueError("expected protocol 1")
        caps = info.get("capabilities")
        if not isinstance(caps, list) or not all(isinstance(x, str) for x in caps) or not {"maid", "profile"}.issubset(caps):
            raise ValueError("expected maid and profile capabilities")
        if required and required not in caps:
            raise ValueError(f"backend does not advertise {required}")
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        raise SystemExit(f"Incompatible AWO: {entry} capabilities check failed: {exc}") from exc
    return root, entry


def run(action, argv):
    root, entry = select(None if action in ("maid", "profile") else action)
    if action == "maid" and argv == ["doctor"]:
        print("AWO:", root, "(public protocol 1)" if entry else "(legacy v1.0.0 layout)", flush=True)
        argv = ["request", "--help"]
    if entry:
        args = [str(entry), action]
    elif action == "profile":
        args = [str(Path(__file__).with_name("legacy_profile.py")), str(root)]
    else:
        args = [str(root / "apps/maid/maid.py")]
    return subprocess.call([sys.executable, "-B", *args, *argv])
