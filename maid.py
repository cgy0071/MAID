import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    from backend import locate
    root = locate()
    entry = root / "apps/maid/maid.py"
    if sys.argv[1:] == ["doctor"]:
        print("AWO:", root, flush=True)
        sys.exit(subprocess.call([sys.executable, "-B", str(entry), "request", "--help"]))
    sys.exit(subprocess.call([sys.executable, "-B", str(entry), *sys.argv[1:]]))
