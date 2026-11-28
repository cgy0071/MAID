"""Named CLI lane resolution for MAID.

Lanes only describe how to invoke a local CLI. Configuration never grants
dispatch or execution authorization, and executor/reviewer lanes must remain
distinct.
"""

import json
import os
from pathlib import Path

SUPPORTED_CLIS = ("codex", "claude", "pi", "omp", "agy")
VALID_ROLES = ("executor", "reviewer")
SCHEMA_VERSION = 1


class LaneError(ValueError):
    """Raised when a lanes file or lane selection is invalid."""


def validate_lanes_config(config):
    if not isinstance(config, dict):
        raise LaneError("Lanes config must be a JSON object.")
    if config.get("schema_version", SCHEMA_VERSION) != SCHEMA_VERSION:
        raise LaneError("Unsupported lanes schema_version.")
    lanes = config.get("lanes")
    if not isinstance(lanes, dict):
        raise LaneError("Lanes config must contain a 'lanes' object.")
    for name, entry in lanes.items():
        if not isinstance(name, str) or not name.strip():
            raise LaneError("Lane name must be a non-empty string.")
        if not isinstance(entry, dict):
            raise LaneError("Lane '%s' must be an object." % name)
        if entry.get("cli") not in SUPPORTED_CLIS:
            raise LaneError("Lane '%s' has unsupported cli." % name)
        exe = entry.get("executable")
        if not isinstance(exe, str) or not exe.strip() or exe.lower().endswith(".ps1"):
            raise LaneError("Lane '%s' must specify a native non-.ps1 executable." % name)
        default_args = entry.get("default_args", [])
        if not isinstance(default_args, list) or not all(isinstance(a, str) for a in default_args):
            raise LaneError("Lane '%s' default_args must be a list of strings." % name)
        roles = entry.get("allowed_roles")
        if (
            not isinstance(roles, list)
            or not roles
            or not all(isinstance(r, str) and r in VALID_ROLES for r in roles)
        ):
            raise LaneError("Lane '%s' allowed_roles must be a non-empty subset of executor/reviewer." % name)
    return config


def load_lanes(path):
    if not path:
        raise LaneError("Specify --lanes PATH or set MAID_LANES_FILE.")
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return validate_lanes_config(data)


def resolve_lane(lanes_path, lane_name, role="executor", peer_lane=None):
    config = load_lanes(lanes_path)
    if role not in VALID_ROLES:
        raise LaneError("Invalid role: " + str(role))
    if lane_name not in config["lanes"]:
        raise LaneError("Unknown lane: " + str(lane_name))
    if peer_lane is not None and peer_lane == lane_name:
        raise LaneError("Executor and reviewer lanes must be distinct; self-review is forbidden.")
    entry = config["lanes"][lane_name]
    if role not in entry["allowed_roles"]:
        raise LaneError("Lane '%s' is not allowed for role '%s'." % (lane_name, role))
    return {
        "lane": lane_name,
        "role": role,
        "cli": entry["cli"],
        "executable": entry["executable"],
        "default_args": list(entry.get("default_args", [])),
        "allowed_roles": list(entry["allowed_roles"]),
        "authorized": False,
    }


def _extract_flag(argv, name):
    out = []
    value = None
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == name:
            if i + 1 >= len(argv):
                raise LaneError("Missing value for " + name)
            value = argv[i + 1]
            i += 2
            continue
        if arg.startswith(name + "="):
            value = arg.split("=", 1)[1]
            i += 1
            continue
        out.append(arg)
        i += 1
    return value, out
