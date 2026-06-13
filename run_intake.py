import json
import sys
from pathlib import Path
import importlib.util

# Runner-level tool bridge.
# QPE is not core. QPE remains a tool package.
# This only makes Jerod's tool packages visible before the Garden core imports/runs.
TOOLS_PATHS = [
    Path('/mnt/c/Users/jerod/eden/garden/tools'),
]

BRIDGED_TOOL_PATHS = []
for tool_path in TOOLS_PATHS:
    if tool_path.exists():
        value = str(tool_path)
        if value not in sys.path:
            sys.path.insert(0, value)
        BRIDGED_TOOL_PATHS.append(value)

import the_garden


def tool_visible(name):
    spec = importlib.util.find_spec(name)
    if spec is None:
        return {"visible": False, "origin": None}
    return {"visible": True, "origin": getattr(spec, "origin", None)}


def load_payload_any(value):
    if value is None:
        return {
            "_input_status": "null_input_pass",
            "raw": None,
        }

    path = Path(value)

    if path.exists() and path.is_file():
        raw = path.read_text(encoding="utf-8")

        try:
            payload = json.loads(raw)
            if isinstance(payload, dict):
                payload.setdefault("_input_status", "json_payload")
            return payload
        except Exception as exc:
            return {
                "_input_status": "json_error_pass",
                "_error_type": type(exc).__name__,
                "_error_message": str(exc),
                "raw": raw,
            }

    return {
        "_input_status": "raw_argument_pass",
        "raw": value,
    }


def get_flag_value(args, flag, default=None, cast=None):
    if flag not in args:
        return default
    i = args.index(flag)
    if i + 1 >= len(args):
        return default
    value = args[i + 1]
    if cast is None:
        return value
    try:
        return cast(value)
    except Exception:
        return default


def main():
    args = sys.argv[1:]

    land = "--land" in args

    out_path = get_flag_value(args, "--out", "garden_full_run.json")
    source_label = get_flag_value(args, "--source", "run_intake")
    read_limit = get_flag_value(args, "--read-limit", 10, int)
    max_cycles = get_flag_value(args, "--max-cycles", 1, int)

    flags_with_values = {"--out", "--source", "--read-limit", "--max-cycles"}
    flags_no_values = {"--land"}

    cleaned = []
    skip_next = False

    for arg in args:
        if skip_next:
            skip_next = False
            continue

        if arg in flags_with_values:
            skip_next = True
            continue

        if arg in flags_no_values:
            continue

        cleaned.append(arg)

    input_value = cleaned[0] if cleaned else None
    payload = load_payload_any(input_value)

    qpe_status = tool_visible("qpe")

    if not hasattr(the_garden, "run"):
        result = {
            "final_status": "error_pass",
            "error": "the_garden.run is not exposed. Add run(...) to identity.py.",
            "payload": payload,
            "tool_bridge": {
                "role": "runner_tool_visibility_only_not_core_execution",
                "bridged_tool_paths": BRIDGED_TOOL_PATHS,
                "qpe": qpe_status,
            },
        }
    else:
        result = the_garden.run(
            source=payload,
            source_label=source_label,
            land=land,
            read_limit=read_limit,
            max_cycles=max_cycles,
        )
        if isinstance(result, dict):
            result.setdefault("tool_bridge", {
                "role": "runner_tool_visibility_only_not_core_execution",
                "bridged_tool_paths": BRIDGED_TOOL_PATHS,
                "qpe": qpe_status,
            })

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, default=str, ensure_ascii=False)

    print(f"source        : {source_label}")
    print(f"input_status  : {payload.get('_input_status') if isinstance(payload, dict) else 'payload'}")
    print(f"has run       : {hasattr(the_garden, 'run')}")
    print(f"tools_bridged : {len(BRIDGED_TOOL_PATHS)}")
    print(f"qpe_tool_seen : {qpe_status.get('visible')}")
    print(f"qpe_origin    : {qpe_status.get('origin')}")
    print(f"read_limit    : {read_limit}")
    print(f"max_cycles    : {max_cycles}")
    print(f"final_status  : {result.get('final_status') if isinstance(result, dict) else None}")
    print(f"output        : {out_path}")

    if isinstance(result, dict):
        print(f"intake_status : {result.get('intake', {}).get('status') if isinstance(result.get('intake'), dict) else None}")
        print(f"land_status   : {result.get('land', {}).get('status') if isinstance(result.get('land'), dict) else None}")
        print(f"compute_status: {result.get('computing', {}).get('status') if isinstance(result.get('computing'), dict) else None}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
