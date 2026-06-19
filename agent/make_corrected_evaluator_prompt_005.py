from pathlib import Path

template = Path("agent/prompts/evaluator_prompt.txt").read_text()

workflow = Path("agent/outputs/corrected_worker_outputs/GSCF_005_corrected_worker_output.txt").read_text()

prompt = template.replace("{workflow}", workflow)

out = Path("agent/outputs/evaluator_prompts/GSCF_005_corrected_output_evaluator_prompt.txt")
out.write_text(prompt)

print("Created:", out)
