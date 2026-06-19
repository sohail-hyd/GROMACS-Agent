import json
from pathlib import Path

worker_template = Path("agent/prompts/worker_prompt.txt").read_text()
evaluator_template = Path("agent/prompts/evaluator_prompt.txt").read_text()

Path("agent/outputs/worker_prompts").mkdir(parents=True, exist_ok=True)
Path("agent/outputs/evaluator_prompts").mkdir(parents=True, exist_ok=True)

def as_text(value):
    if isinstance(value, str):
        return value
    return json.dumps(value, indent=2)

def get_task_text(record):
    value = (
        record.get("instruction")
        or record.get("user_task")
        or record.get("task")
        or record.get("task_description")
        or record.get("description")
        or record
    )
    return as_text(value)

# Create worker prompts from GSCF records
for path in sorted(Path("data/gscf_dataset").glob("*.json")):
    record = json.loads(path.read_text())
    task_id = record.get("id", path.stem.upper())
    task = get_task_text(record)

    prompt = worker_template.replace("{task}", task)
    prompt += "\n\nAdditional validated dataset record:\n"
    prompt += json.dumps(record, indent=2)
    prompt += "\n\nGenerate the complete GROMACS workflow according to this prompt.\n"

    out = Path(f"agent/outputs/worker_prompts/{task_id}_worker_prompt.txt")
    out.write_text(prompt)
    print("Created:", out)

# Create evaluator prompts from GEQS records
for path in sorted(Path("data/geqs_dataset").glob("*.json")):
    record = json.loads(path.read_text())
    task_id = record.get("id", path.stem.upper())

    workflow_value = (
        record.get("generated_workflow")
        or record.get("workflow")
        or record.get("generated_answer")
        or record
    )

    workflow = as_text(workflow_value)

    prompt = evaluator_template.replace("{workflow}", workflow)
    prompt += "\n\nAdditional evaluator dataset record:\n"
    prompt += json.dumps(record, indent=2)

    out = Path(f"agent/outputs/evaluator_prompts/{task_id}_evaluator_prompt.txt")
    out.write_text(prompt)
    print("Created:", out)
