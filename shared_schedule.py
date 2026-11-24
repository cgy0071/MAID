"""Forward shared-domain commands to the AWO project CLI."""
import argparse
import json
from pathlib import Path

from backend import run
from run_index import path_at


def main(argv):
    parser = argparse.ArgumentParser(prog="maid.py shared")
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--project", required=True)
    actions = parser.add_subparsers(dest="action", required=True)
    actions.add_parser("command").add_argument("--file", type=Path, required=True)
    actions.add_parser("status").add_argument("--task", required=True)
    dispatch = actions.add_parser("dispatch")
    dispatch.add_argument("--assignment", required=True)
    dispatch.add_argument("--epoch", type=int, required=True)
    args = parser.parse_args(argv)
    try:
        base = args.index.resolve().parent
        project = json.loads(args.index.read_text(encoding="utf-8-sig"))["projects"][args.project]
        domain = project["scheduler"]
        params = ["--state", str(path_at(base, domain["state"])), "--project-root",
                  str(path_at(base, project["repository"])), "--token-file",
                  str(path_at(base, domain["token_file"])), "--expected-project-id", domain["project_id"]]
        if not isinstance(params[-1], str) or not params[-1].strip():
            raise ValueError("missing project identity")
        if args.action == "command":
            route = ["command", "--file", str(args.file.resolve())]
        elif args.action == "status":
            route = ["status", "--task", args.task]
        else:
            route = ["dispatch", "--assignment", args.assignment, "--epoch", str(args.epoch)]
        return run("schedule", [*params, *route])
    except (OSError, KeyError, TypeError, ValueError) as exc:
        parser.error(f"invalid shared scheduling configuration: {exc}")
