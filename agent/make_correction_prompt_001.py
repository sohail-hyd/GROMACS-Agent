import json
from pathlib import Path

task_id = "GSCF_001"

original_prompt = Path(f"agent/outputs/worker_prompts/{task_id}_worker_prompt.txt").read_text()
baseline_output = Path(f"agent/outputs/llm_worker_outputs/{task_id}_manual_llm_worker_output.txt").read_text()
evaluation = json.loads(Path(f"agent/outputs/llm_evaluator_outputs/{task_id}_manual_eval.json").read_text())

detected_errors = "\n".join(f"- {e}" for e in evaluation.get("detected_errors", []))
correction_suggestions = "\n".join(f"- {s}" for s in evaluation.get("correction_suggestions", []))

prompt = f"""
You are a strict GROMACS workflow correction agent.

Your task is to revise the generated workflow using the evaluator feedback.

Original task:
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

Mandatory rules:
1. Keep the workflow focused on pure water density at 300 K and 1 bar.
2. Fix every detected error.
3. Use safe topology preparation.
4. Do not use gmx solvate -p topol.top unless topol.top already exists.
5. Use clear minimization, NVT, NPT, and production steps.
6. Use C-rescale barostat for NPT.
7. Use non-interactive density extraction, for example echo-based gmx energy.
8. Avoid unnecessary position-restraint reference files unless restraints are actually used.
9. Include expected output files.
10. Include common errors and fixes.
11. End with one clear final validation note.
12. Clearly state if a short trajectory is only workflow validation and not final publication-quality density.

Now write the full corrected workflow again.
"""

out = Path(f"agent/outputs/correction_prompts/{task_id}_correction_prompt.txt")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(prompt)

print("Created:", out)
