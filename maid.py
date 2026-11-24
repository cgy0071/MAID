import sys

from backend import run


if __name__ == "__main__":
    sys.exit(run("maid", sys.argv[1:]))
