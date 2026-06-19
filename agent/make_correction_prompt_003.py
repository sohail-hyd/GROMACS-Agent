import json
from pathlib import Path

task_id = "GSCF_003"

original_prompt = Path(f"agent/outputs/worker_prompts/{task_id}_worker_prompt.txt").read_text()
baseline_output = Path(f"agent/outputs/llm_worker_outputs/{task_id}_manual_llm_worker_output.txt").read_text()
evaluation = json.loads(Path(f"agent/outputs/llm_evaluator_outputs/{task_id}_manual_eval.json").read_text())

detected_errors = "\n".join(f"- {e}" for e in evaluation.get("detected_errors", []))
correction_suggestions = "\n".join(f"- {s}" for s in evaluation.get("correction_suggestions", []))

correction_prompt = f"""
You are a GROMACS workflow correction agent.

Your task is to revise the generated workflow using the evaluator feedback.

Original task prompt:
{original_prompt}

Generated baseline workflow:
{baseline_output}

Evaluator score:
{evaluation.get("score")}/10

Detected errors:
{detected_errors}

Correction suggestions:
{correction_suggestions}

Now produce a corrected, complete, reproducible GROMACS workflow.

Rules:
1. Keep the workflow focused on the original task.
2. Fix all detected errors.
3. Do not introduce unsupported GROMACS options.
4. Do not use invalid MSD options such as "-type no".
5. Use clear topology preparation.
6. Use clear command order.
7. Use physically reasonable MDP settings.
8. For NPT, prefer C-rescale barostat.
9. Include required input files, MDP settings, topology steps, command sequence, analysis commands, expected outputs, common errors/fixes, and final validation note.
10. Clearly state if the trajectory is short and only suitable for workflow validation.
"""

out = Path(f"agent/outputs/correction_prompts/{task_id}_correction_prompt.txt")
out.write_text(correction_prompt)

print("Created:", out)
