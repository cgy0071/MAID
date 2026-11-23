import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    entry = Path(__file__).resolve().parent / "vendor/awo/apps/maid/maid.py"
    if not entry.is_file():
        sys.exit("Backend missing: use the Windows release ZIP or git submodule update --init.")
    sys.exit(subprocess.call([sys.executable, "-B", str(entry), *sys.argv[1:]]))
