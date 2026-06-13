import json
import re
from pathlib import Path

packet_path = Path("track_telemetry_packet.json")
run_path = Path("track_telemetry_landed.json")

packet = json.loads(packet_path.read_text(encoding="utf-8"))
run = json.loads(run_path.read_text(encoding="utf-8"))

outputs = run.get("outputs") or []
solver = [o for o in outputs if isinstance(o, dict) and o.get("output_type") == "solver"]
physics = [o for o in outputs if isinstance(o, dict) and o.get("output_type") == "physics"]
qpe = [o for o in outputs if isinstance(o, dict) and o.get("output_type") == "qpe"]
c = (run.get("computing") or {}).get("result") or {}

print("============================================================")
print("TRACK TELEMETRY FRONTIER RESULT")
print("============================================================")
print()
print("Telemetry source:", packet.get("source_file"))
print("source_sha256   :", packet.get("source_sha256"))
print("row_count       :", packet.get("row_count"))
print("signals_detected:", packet.get("signals_detected"))
print()

print("PIT-WALL METRICS FROM CSV")
for k, v in packet.get("pit_wall_metrics", {}).items():
    print(f"{k:16}: {v}")
print()

print("LANDED RUN STATUS")
print("final_status  :", run.get("final_status"))
print("intake_status :", (run.get("intake") or {}).get("status"))
print("land_status   :", (run.get("land") or {}).get("status"))
print("compute_status:", (run.get("computing") or {}).get("status"))
print("outputs       :", len(outputs))
print()

print("COMPUTE SURFACE")
if isinstance(c, dict):
    for k in ["records_read", "atoms_found", "edges_created", "cycles_found", "solver_outputs", "physics_outputs", "qpe_outputs", "total_outputs", "records_written"]:
        print(f"{k:16}: {c.get(k)}")
print()

print("EMISSION COUNTS")
print("solver :", len(solver))
print("physics:", len(physics))
print("qpe    :", len(qpe))
print()

if physics:
    p = physics[0]
    print("PRIMARY PHYSICS EMISSION")
    print("state         :", p.get("state"))
    print("field         :", p.get("field"))
    print("energy        :", p.get("energy"))
    print("torque        :", [p.get("torque_x"), p.get("torque_y"), p.get("torque_z")])
    print("gate          :", p.get("gate"))
    print("pulse         :", p.get("pulse"))
    print("norm_preserved:", p.get("norm_preserved"))
    print("seal          :", p.get("seal"))
    print()

if solver:
    print("SOLVER EMISSIONS")
    for i, s in enumerate(solver, 1):
        print(i, s.get("solver_name"), "=>", s.get("solver_result"), "| predicate:", s.get("predicate_value"))
    print()

def grab(pattern, text):
    m = re.search(pattern, text)
    return m.group(1) if m else None

if qpe:
    q = qpe[0]
    qe = q.get("qpe_evidence") or {}
    platinum = str(qe.get("platinum") or "")
    sim_result = str(qe.get("sim_result") or "")

    print("QPE TOOL EMISSION")
    print("n_qubits            :", qe.get("n_qubits"))
    print("drift_dims_encoded  :", qe.get("drift_dims_encoded"))
    print("shots               :", qe.get("shots"))
    print("backend             :", grab(r"backend='([^']+)'", sim_result))
    print("certification       :", grab(r"level='([^']+)'", platinum))
    print("certification_ok    :", grab(r"ok=(True|False)", platinum))
    print("closure_verified    :", grab(r"closure_verified=(True|False)", platinum))
    print("born_consistency_TV :", grab(r"Born-consistency TV=([0-9.]+)", platinum))
    print("born_tolerance      :", grab(r"tol=([0-9.]+)", platinum))
    print("seal                :", q.get("seal"))
    print()

print("============================================================")
print("TECHNICAL TRANSLATION")
print("============================================================")
print()
print("This is now a telemetry-shaped run, not a missing-path raw argument.")
print("The CSV contained speed, yaw rate, throttle, brake, and tire temperature values.")
print("The packet builder computed pit-wall residual metrics before run_intake:")
print()
print("R_total     =", packet['pit_wall_metrics']['R_total'])
print("R_condition =", packet['pit_wall_metrics']['R_condition'])
print("R_artifact  =", packet['pit_wall_metrics']['R_artifact'])
print("chi_D       =", packet['pit_wall_metrics']['chi_D'])
print()
print("Meaning:")
print("The telemetry packet exposed a residual frontier coordinate chi_D from the")
print("difference between total observed variation, explained operating condition,")
print("and likely artifact surface.")
print()
print("SEALED TRACK-DATA CLAIM:")
print("Jerod has moved from static public motorsports software evidence into a")
print("track-telemetry-shaped governance run. The next step is replacing the sample")
print("CSV with actual logged car data or a decoded ROS bag topic export.")
