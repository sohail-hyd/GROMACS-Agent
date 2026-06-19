from pathlib import Path

template = Path("agent/prompts/evaluator_prompt.txt").read_text()

workflow_path = Path("agent/outputs/llm_worker_outputs/GSCF_002_manual_llm_worker_output.txt")
workflow = workflow_path.read_text()

prompt = template.replace("{workflow}", workflow)

out = Path("agent/outputs/evaluator_prompts/GSCF_002_manual_output_evaluator_prompt.txt")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(prompt)

print("Created:", out)
