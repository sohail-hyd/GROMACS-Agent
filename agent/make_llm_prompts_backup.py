import json
from pathlib import Path

worker_template = Path("agent/prompts/worker_prompt.txt").read_text()
evaluator_template = Path("agent/prompts/evaluator_prompt.txt").read_text()

Path("agent/outputs/worker_prompts").mkdir(parents=True, exist_ok=True)
Path("agent/outputs/evaluator_prompts").mkdir(parents=True, exist_ok=True)

# Worker prompts from GSCF
for path in sorted(Path("data/gscf_dataset").glob("*.json")):
    record = json.loads(path.read_text())
    task = record["instruction"]
    prompt = worker_template.replace("{task}", task)

    out = Path("agent/outputs/worker_prompts") / f"{record['id']}_worker_prompt.txt"
    out.write_text(prompt)
    print("Created:", out)

# Evaluator prompts from GEQS
for path in sorted(Path("data/geqs_dataset").glob("*.json")):
    record = json.loads(path.read_text())
    workflow = json.dumps(record["generated_workflow"], indent=2)
    prompt = evaluator_template.replace("{workflow}", workflow)

    out = Path("agent/outputs/evaluator_prompts") / f"{record['id']}_evaluator_prompt.txt"
    out.write_text(prompt)
    print("Created:", out)
