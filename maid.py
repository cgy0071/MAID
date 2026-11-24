import sys

from backend import run


if __name__ == "__main__":
    if sys.argv[1:2] == ["runs"]:
        from run_index import main
        sys.exit(main(sys.argv[2:]))
    if sys.argv[1:] in ([], ["--help"], ["-h"]):
        print("MAID: doctor | request | direct | --thread DIR chat/start/status | runs --help")
        sys.exit(0)
    sys.exit(run("maid", sys.argv[1:]))
