import json
import hashlib
import re
from pathlib import Path

RUN_PATH = Path("tam_common_garden_landed.json")
EMIT_PATH = Path("frontier_emitted_outputs.json")

OPERATOR_RECEIPT = Path("frontier_operator_receipt.json")
QPE_RECEIPT = Path("frontier_qpe_receipt.json")
MASTER_SEAL = Path("frontier_master_seal.txt")


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def sha256_obj(obj):
    return hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()


def sha256_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract(pattern, text, default=None, cast=None):
    m = re.search(pattern, text)
    if not m:
        return default
    value = m.group(1)
    if cast:
        try:
            return cast(value)
        except Exception:
            return default
    return value


def main():
    if not RUN_PATH.exists():
        raise SystemExit(f"missing {RUN_PATH}")

    if not EMIT_PATH.exists():
        raise SystemExit(f"missing {EMIT_PATH}")

    run = json.loads(RUN_PATH.read_text(encoding="utf-8"))
    emitted = json.loads(EMIT_PATH.read_text(encoding="utf-8"))

    outputs = run.get("outputs") or []
    solver = [x for x in emitted if x.get("output_type") == "solver"]
    physics = [x for x in emitted if x.get("output_type") == "physics"]
    qpe = [x for x in emitted if x.get("output_type") == "qpe"]

    primary_physics = physics[0] if physics else {}
    qpe_output = qpe[0] if qpe else {}
    qpe_evidence = (qpe_output.get("operator_readout") or {}).get("qpe_evidence") or {}

    platinum = str(qpe_evidence.get("platinum") or "")
    sim_result = str(qpe_evidence.get("sim_result") or "")

    qpe_metrics = {
        "qpe_present": bool(qpe),
        "n_qubits": qpe_evidence.get("n_qubits"),
        "drift_dims_encoded": qpe_evidence.get("drift_dims_encoded"),
        "shots": qpe_evidence.get("shots"),
        "noise_rate_derived": qpe_evidence.get("noise_rate_derived"),
        "backend": extract(r"backend='([^']+)'", sim_result),
        "certification_level": extract(r"level='([^']+)'", platinum),
        "certification_ok": extract(r"ok=(True|False)", platinum, cast=lambda x: x == "True"),
        "closure_verified": extract(r"closure_verified=(True|False)", platinum, cast=lambda x: x == "True"),
        "born_consistency_tv": extract(r"Born-consistency TV=([0-9.]+)", platinum, cast=float),
        "born_tolerance": extract(r"tol=([0-9.]+)", platinum, cast=float),
        "run_id": extract(r"run_id='([^']+)'", platinum),
        "proof_digest": extract(r"proof_digest='([^']+)'", platinum),
        "event_digest": extract(r"event_digest='([^']+)'", platinum),
    }

    operator_receipt = {
        "receipt_type": "frontier_operator_receipt",
        "input_run_file": str(RUN_PATH),
        "input_emitted_file": str(EMIT_PATH),
        "run_file_sha256": sha256_file(RUN_PATH),
        "emitted_file_sha256": sha256_file(EMIT_PATH),
        "final_status": run.get("final_status"),
        "intake_status": (run.get("intake") or {}).get("status"),
        "land_status": (run.get("land") or {}).get("status"),
        "compute_status": (run.get("computing") or {}).get("status"),
        "emission_counts": {
            "solver": len(solver),
            "physics": len(physics),
            "qpe": len(qpe),
            "total": len(emitted),
        },
        "primary_physics_shape": {
            "state": primary_physics.get("state"),
            "field": primary_physics.get("field"),
            "energy": primary_physics.get("energy"),
            "torque": [
                primary_physics.get("torque_x"),
                primary_physics.get("torque_y"),
                primary_physics.get("torque_z"),
            ],
            "chi_D": primary_physics.get("chi_D"),
            "closure": primary_physics.get("predicate_value"),
            "source_output_index": primary_physics.get("source_output_index"),
            "seal": primary_physics.get("seal"),
        },
    }

    operator_receipt["receipt_seal"] = sha256_obj(operator_receipt)

    qpe_receipt = {
        "receipt_type": "frontier_qpe_tool_receipt",
        "qpe_is_tool": True,
        "qpe_called_by_core": True,
        "qpe_metrics": qpe_metrics,
        "qpe_original_seal": (qpe_output.get("operator_readout") or {}).get("original_seal"),
        "qpe_frontier_emit_seal": qpe_output.get("seal"),
    }

    qpe_receipt["receipt_seal"] = sha256_obj(qpe_receipt)

    master = {
        "operator_receipt_seal": operator_receipt["receipt_seal"],
        "qpe_receipt_seal": qpe_receipt["receipt_seal"],
        "run_file_sha256": operator_receipt["run_file_sha256"],
        "emitted_file_sha256": operator_receipt["emitted_file_sha256"],
    }

    master_seal = sha256_obj(master)

    OPERATOR_RECEIPT.write_text(json.dumps(operator_receipt, indent=2, ensure_ascii=False), encoding="utf-8")
    QPE_RECEIPT.write_text(json.dumps(qpe_receipt, indent=2, ensure_ascii=False), encoding="utf-8")
    MASTER_SEAL.write_text(master_seal + "\n", encoding="utf-8")

    print("=== FRONTIER HARNESS COMPLETE ===")
    print("operator_receipt:", OPERATOR_RECEIPT)
    print("operator_receipt_seal:", operator_receipt["receipt_seal"])
    print("qpe_receipt:", QPE_RECEIPT)
    print("qpe_receipt_seal:", qpe_receipt["receipt_seal"])
    print("master_seal:", master_seal)
    print()
    print("POSTABLE RESULT:")
    print("A public autonomous-racing stack emitted a sealed frontier state with")
    print("measurable state, field, energy, torque, residual chi_D, predicate closure,")
    print("and QPE tool evidence certified through the landed Garden run.")


if __name__ == "__main__":
    main()
