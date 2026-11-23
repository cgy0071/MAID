"""Windows entry point for the MAID secretary."""
from pathlib import Path
import subprocess
import sys


def main():
    script = Path(__file__).resolve().parent / "vendor" / "awo" / "scripts" / "maid.py"
    if not script.is_file():
        print("Run git submodule update --init from the maid checkout.", file=sys.stderr)
        return 2
    return subprocess.call([sys.executable, "-B", str(script), *sys.argv[1:]])


if __name__ == "__main__":
    raise SystemExit(main())
