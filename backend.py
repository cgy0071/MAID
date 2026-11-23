import os
from pathlib import Path


def locate():
    default = Path(__file__).resolve().parent.parent / "agent-workflow-orchestrator"
    root = Path(os.environ.get("MAID_AWO_ROOT", default)).resolve()
    for rel in ("apps/maid/maid.py", "scripts/secretary_adapter.py", "scripts/project_entry.py"):
        if not (root / rel).is_file():
            raise SystemExit(f"Incompatible AWO: {root} lacks {rel}. See README or set MAID_AWO_ROOT.")
    return root
