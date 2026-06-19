import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "fine_tuning"
OUT.mkdir(exist_ok=True)

def load_jsons(folder):
    data = []
    for p in sorted(folder.glob("*.json")):
        try:
            d = json.loads(p.read_text())
            d["_source_file"] = p.name
            data.append(d)
        except Exception as e:
            print("skip", p, e)
    return data

def best_text(record):
    for key in [
        "validated_workflow",
        "workflow",
        "corrected_workflow",
        "generated_workflow",
        "output",
        "commands",
        "answer"
    ]:
        if key in record:
            value = record[key]
            if isinstance(value, (dict, list)):
                return json.dumps(value, indent=2)
            return str(value)
    return json.dumps(record, indent=2)

gscf_records = load_jsons(BASE / "data" / "gscf_dataset")
geqs_records = load_jsons(BASE / "data" / "geqs_dataset")

gscf_sft = []
for r in gscf_records:
    task = r.get("user_task") or r.get("task") or r.get("task_description") or r.get("id") or r.get("_source_file")
    gscf_sft.append({
        "instruction": "Generate a complete, reproducible, and scientifically validated GROMACS workflow for the given molecular dynamics task.",
        "input": str(task),
        "output": best_text(r)
    })

geqs_sft = []
for r in geqs_records:
    task = r.get("user_task") or r.get("task") or r.get("task_description") or r.get("id") or r.get("_source_file")
    geqs_sft.append({
        "instruction": "Evaluate the generated GROMACS workflow using a 10-point scientific rubric and provide detected errors and correction suggestions.",
        "input": json.dumps(r, indent=2),
        "output": best_text(r)
    })

(OUT / "GSCF_GromacsWorker_SFT_Alpaca.json").write_text(json.dumps(gscf_sft, indent=2))
(OUT / "GEQS_GromacsEvaluator_SFT_Alpaca.json").write_text(json.dumps(geqs_sft, indent=2))

print("Exported:")
print(OUT / "GSCF_GromacsWorker_SFT_Alpaca.json", len(gscf_sft))
print(OUT / "GEQS_GromacsEvaluator_SFT_Alpaca.json", len(geqs_sft))
