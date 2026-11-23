"""Create a local project profile without starting a model turn."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "vendor/awo/scripts"))
from harness_probe import binary
from project_entry import validate_spec

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--project", required=True, type=Path)
p.add_argument("--thread", required=True, type=Path)
p.add_argument("--allow", action="append", required=True)
p.add_argument("--verify-script", required=True)
p.add_argument("--profile", required=True, type=Path)
a = p.parse_args()
repo = a.project.resolve()
script = (repo / a.verify_script).resolve()
if not script.is_relative_to(repo) or not script.is_file():
    p.error("Verification script must exist inside the project.")
bridge = dict(harness="codex", executable=binary("codex"), timeout_seconds=600)
spec = dict(version=1, repository=str(repo), goal="Prepare a task", allowed_paths=a.allow,
            verify_argv=[sys.executable, "-B", str(script.relative_to(repo))], worker=bridge, reviewer=bridge,
            authorization=dict(source="Local project profile", dispatch_worker=True, allow_local_land=True),
            budget={"tokens.input":40000,"tokens.output":8000}, target_ref="refs/heads/maid-" + a.thread.name,
            work_root=str(a.thread.resolve()), change_name="project-task", max_real_turns=12, timeout_seconds=300)
validate_spec(dict(spec))
with a.profile.open("x", encoding="utf-8") as f:
    json.dump(spec, f, indent=2, ensure_ascii=False)
print("Profile ready:", a.profile.resolve())
