from pathlib import Path

template = Path("agent/prompts/evaluator_prompt.txt").read_text()

workflow = Path("agent/outputs/corrected_worker_outputs/GSCF_003_corrected_worker_output_v2.txt").read_text()

prompt = template.replace("{workflow}", workflow)

out = Path("agent/outputs/evaluator_prompts/GSCF_003_corrected_output_evaluator_prompt_v2.txt")
out.write_text(prompt)

print("Created:", out)
