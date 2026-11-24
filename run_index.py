"""Resolve an explicitly named project and run from an operator-owned index."""
import argparse
import json
from pathlib import Path
import sys

import backend


def path_at(base, value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("expected a nonempty path")
    return (base / value).resolve()


def main(argv):
    p = argparse.ArgumentParser(prog="maid.py runs")
    p.add_argument("--index", type=Path, required=True, help="local project/run index JSON")
    p.add_argument("--project")
    p.add_argument("--run")
    p.add_argument("operation", choices=("list", "prepare", "status", "start", "recover"))
    p.add_argument("--confirm-execute", action="store_true")
    a = p.parse_args(argv)
    try:
        base = a.index.resolve().parent
        projects = json.loads(a.index.read_text(encoding="utf-8-sig"))["projects"]
        if a.operation == "list":
            if a.run or a.confirm_execute:
                p.error("list takes no run or confirmation")
            keys = [a.project] if a.project else sorted(projects)
            print(json.dumps({k: sorted(projects[k]["runs"]) for k in keys}))
            return 0
        if not a.project or not a.run:
            p.error("select both --project and --run")
        project = projects[a.project]
        record = project["runs"][a.run]
        repo = path_at(base, project["repository"])
        spec = path_at(base, record["spec"])
        thread = path_at(base, record["thread"])
        config = json.loads(spec.read_text(encoding="utf-8"))
        if Path(config["repository"]).resolve() != repo or Path(config["work_root"]).resolve() != thread:
            p.error("selected project/run differs from the project or thread in the spec")
        # Guard against accidentally binding another project's already prepared run.
        if (thread / "spec.json").exists() and (thread / "spec.json").read_bytes() != spec.read_bytes():
            p.error("selected spec differs from the frozen run")
        args = ["--thread", str(thread)]
        if a.operation == "prepare":
            args.extend(["--spec", str(spec)])
        if a.confirm_execute:
            if a.operation not in ("start", "recover"):
                p.error("only start and recover take confirmation")
            args.append("--confirm-execute")
        return backend.run(a.operation, args)
    except (OSError, KeyError, ValueError, TypeError) as exc:
        p.error(f"invalid project/run index or spec: {exc}")
