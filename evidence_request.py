"""Preview and select authorized evidence for a task draft."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

import backend


def call(target, payload):
    _, entry = backend.select("evidence-draft")
    proc = subprocess.run([sys.executable, "-B", str(entry), "evidence-draft", "--target", str(target)],
                          input=json.dumps(payload), text=True, encoding="utf-8", capture_output=True)
    if proc.returncode:
        raise ValueError(proc.stderr.strip())
    return json.loads(proc.stdout)


def numbers(value, count):
    ids = [int(n.strip()) for n in value.split(",")]
    if len(set(ids)) != len(ids) or not all(1 <= n <= count for n in ids):
        raise ValueError("Select distinct original excerpt numbers shown in the preview.")
    return ids


def draft(target, goal, refs, out=None, expected_target=None):
    payload = {"goal": goal, "selected": refs}
    if expected_target is not None:
        payload["expected_target"] = expected_target
    result = call(target, payload)
    if out:
        with Path(out).open("x", encoding="utf-8") as f:
            json.dump(result["draft"], f, ensure_ascii=False, indent=2)
    print(json.dumps(result, ensure_ascii=False), flush=True)


def main(argv):
    backend.select("evidence-draft")
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--query", required=True)
    p.add_argument("--target", required=True)
    p.add_argument("--request", help="Task objective (defaults to the query)")
    p.add_argument("--out", help="Create a new draft file containing source pointers")
    p.add_argument("--keep", help="Comma-separated preview numbers; default: interactive selection")
    a = p.parse_args(argv)
    try:
        view = call(a.target, {"query": a.query})
        print(json.dumps(view, ensure_ascii=False), flush=True)
        if not view["items"]:
            print("No authorized matches. Revise the query or explicitly start a separate request.")
            return 0
        choice = a.keep or input("Keep excerpt numbers (e.g. 1,3), all, or cancel: ").strip()
        if choice == "cancel":
            print("Cancelled.")
            return 0
        items = view["items"]
        indices = range(1, len(items)+1) if choice == "all" else numbers(choice, len(items))
        draft(a.target, a.request or a.query, [items[i-1]["ref"] for i in indices], a.out, view["target"])
        return 0
    except (ValueError, OSError, EOFError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
