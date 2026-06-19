import sys
from pathlib import Path

if len(sys.argv) != 2:
    print("Usage: python3 agent/make_manual_evaluator_prompt.py GSCF_004")
    raise SystemExit(1)

task_id = sys.argv[1]

template = Path("agent/prompts/evaluator_prompt.txt").read_text()

workflow_path = Path(f"agent/outputs/llm_worker_outputs/{task_id}_manual_llm_worker_output.txt")
workflow = workflow_path.read_text()

prompt = template.replace("{workflow}", workflow)

out = Path(f"agent/outputs/evaluator_prompts/{task_id}_manual_output_evaluator_prompt.txt")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(prompt)

print("Created:", out)
