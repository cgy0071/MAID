"""Resolve an explicitly named project and run from an operator-owned index."""
import argparse
import json
import os
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
    p.add_argument("operation", choices=("list", "prepare", "status", "start", "recover", "session", "rework"))
    p.add_argument("--action", choices=("records", "focus", "resume"))
    p.add_argument("--confirm-execute", action="store_true")
    p.add_argument("--handoff", choices=("continue", "manual", "reassign"))
    p.add_argument("--state-version", help="observed version from read-only recover")
    p.add_argument("--recipient", help="executor or operator identity for this handoff")
    p.add_argument("--lanes", type=Path, default=os.environ.get("MAID_LANES_FILE"), help="local named lanes JSON")
    p.add_argument("--reassign-lane", help="named executor lane for recover --handoff reassign")
    p.add_argument("--draft", type=Path)
    p.add_argument("--draft-digest", help="SHA-256 shown with the reviewed evidence draft")
    p.add_argument("--evidence-route", type=Path, help="fresh recipient grants for rework")
    p.add_argument("--rework-attempt", action="store_true", help="select the linked repair attempt")
    p.add_argument("--handoff-attempt", action="store_true", help="select the verified replacement attempt")
    a = p.parse_args(argv)
    if a.reassign_lane is not None:
        if a.operation != "recover" or a.handoff != "reassign":
            p.error("--reassign-lane requires recover --handoff reassign")
        import lanes
        try:
            resolved = lanes.resolve_lane(a.lanes, a.reassign_lane, role="executor")
        except (lanes.LaneError, OSError, ValueError) as exc:
            p.error(str(exc))
        if a.recipient and a.recipient != resolved["lane"]:
            p.error("--recipient must match --reassign-lane")
        a.recipient = resolved["lane"]
    if any(x is not None for x in (a.handoff, a.state_version, a.recipient)):
        if not (a.operation == "recover" and a.confirm_execute and a.handoff
                and a.state_version and a.recipient and a.recipient.strip()):
            p.error("handoff requires recover, --handoff, --state-version, --recipient and --confirm-execute")
    if a.evidence_route and a.operation != "rework":
        p.error("--evidence-route requires rework")
    if (a.rework_attempt or a.handoff_attempt) and a.operation not in ("start", "recover", "status"):
        p.error("linked attempts require start, recover or status")
    if bool(a.action) != (a.operation == "session"):
        p.error("session requires --action records, focus or resume")
    if a.draft is not None or a.draft_digest is not None:
        if not (a.operation == "start" and a.confirm_execute and a.draft and a.draft_digest):
            p.error("Evidence requires start --confirm-execute, --draft and --draft-digest")
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
        if a.handoff:
            args.extend(["--handoff", a.handoff, "--state-version", a.state_version,
                         "--recipient", a.recipient])
            if a.reassign_lane:
                args.extend(["--lanes", str(a.lanes.resolve()), "--reassign-lane", a.reassign_lane])
        if a.rework_attempt:
            args.append("--rework-attempt")
        if a.handoff_attempt:
            args.append("--handoff-attempt")
        if a.evidence_route:
            args.extend(["--evidence-route", str(a.evidence_route.resolve())])
        if a.action:
            args.extend(["--action", a.action])
        if a.operation == "prepare":
            args.extend(["--spec", str(spec)])
        if a.confirm_execute:
            if a.operation not in ("start", "recover"):
                p.error("only start and recover take confirmation")
            args.append("--confirm-execute")
        if a.draft:
            args.extend(["--draft", str(a.draft.resolve()), "--draft-digest", a.draft_digest])
        return backend.run(a.operation, args)
    except (OSError, KeyError, ValueError, TypeError) as exc:
        p.error(f"invalid project/run index or spec: {exc}")
