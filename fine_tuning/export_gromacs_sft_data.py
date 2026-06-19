import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "fine_tuning"
OUT.mkdir(parents=True, exist_ok=True)

def load_jsons(folder):
    records = []
    for p in sorted(folder.glob("*.json")):
        try:
            d = json.loads(p.read_text())
            d["_source_file"] = p.name
            records.append(d)
        except Exception as e:
            print("Skipped", p, e)
    return records

def record_to_text(record):
    keys = [
        "workflow",
        "output",
        "validated_workflow",
        "generated_workflow",
        "command_sequence",
        "commands"
    ]
    for k in keys:
        if k in record:
            v = record[k]
            return json.dumps(v, indent=2) if isinstance(v, (dict, list)) else str(v)
    return json.dumps(record, indent=2)

gscf_records = load_jsons(BASE / "data" / "gscf_dataset")
geqs_records = load_jsons(BASE / "data" / "geqs_dataset")

gscf_sft = []
for r in gscf_records:
    task = r.get("user_task") or r.get("task") or r.get("task_name") or r.get("id")
    gscf_sft.append({
        "instruction": "Generate a complete, reproducible, topology-aware GROMACS workflow for the given molecular dynamics task. Include required files, command sequence, expected outputs, common errors, and validation notes.",
        "input": task,
        "output": record_to_text(r)
    })

geqs_sft = []
for r in geqs_records:
    geqs_sft.append({
        "instruction": "Evaluate the generated GROMACS workflow using a strict 10-point scientific rubric. Return score, decision, detected errors, and correction suggestions.",
        "input": json.dumps(r.get("input", r), indent=2),
        "output": json.dumps(r.get("output", r), indent=2)
    })

worker_path = OUT / "GSCF_GromacsWorker_SFT_Alpaca.json"
evaluator_path = OUT / "GEQS_GromacsEvaluator_SFT_Alpaca.json"

worker_path.write_text(json.dumps(gscf_sft, indent=2))
evaluator_path.write_text(json.dumps(geqs_sft, indent=2))

print("Export complete")
print("Worker SFT records:", len(gscf_sft), worker_path)
print("Evaluator SFT records:", len(geqs_sft), evaluator_path)
