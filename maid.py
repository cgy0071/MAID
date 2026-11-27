import sys

from backend import run


if __name__ == "__main__":
    if sys.argv[1:2] == ["request"] and any(
            arg == "--query" or arg.startswith("--query=") for arg in sys.argv[2:]):
        from evidence_request import main
        sys.exit(main(sys.argv[2:]))
    if sys.argv[1:2] == ["study"]:
        from study import main
        sys.exit(main(sys.argv[2:]))
    if sys.argv[1:2] == ["shared"]:
        from shared_schedule import main
        sys.exit(main(sys.argv[2:]))
    if sys.argv[1:2] == ["runs"]:
        from run_index import main
        sys.exit(main(sys.argv[2:]))
    if sys.argv[1:] in ([], ["--help"], ["-h"]):
        print("MAID: study --help | doctor | request | direct | --thread DIR chat/start/status | runs --help | shared --help")
        sys.exit(0)
    sys.exit(run("maid", sys.argv[1:]))
