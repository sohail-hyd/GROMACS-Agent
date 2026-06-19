import json
from pathlib import Path

task_id = "GSCF_005"

original_prompt = Path(f"agent/outputs/worker_prompts/{task_id}_worker_prompt.txt").read_text()
baseline_output = Path(f"agent/outputs/llm_worker_outputs/{task_id}_manual_llm_worker_output.txt").read_text()
evaluation = json.loads(Path(f"agent/outputs/llm_evaluator_outputs/{task_id}_manual_eval.json").read_text())

detected_errors = "\n".join(f"- {e}" for e in evaluation.get("detected_errors", []))
correction_suggestions = "\n".join(f"- {s}" for s in evaluation.get("correction_suggestions", []))

prompt = f"""
You are a strict GROMACS workflow correction agent.

Your task is to revise the generated workflow using evaluator feedback.

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

Mandatory corrections for density-profile workflow:
1. Keep the workflow focused on mass density profile of pure water along the z direction at 300 K.
2. Use safe topology preparation.
3. Use clear minimization, NVT, NPT, and production steps.
4. Use C-rescale barostat for NPT.
5. Include the correct density-profile command:
   echo System | gmx density -f md.xtc -s md.tpr -o density_profile_z.xvg -d Z -sl 100
6. Clearly explain that -d Z means the profile is calculated along the z direction.
7. Clearly explain that -sl 100 means 100 slabs/bins.
8. Explain group selection for gmx density.
9. Include expected output files.
10. Include common errors and fixes.
11. Clearly warn that short trajectories are only workflow validation, not publication-quality density-profile statistics.
12. End with one clear final validation note.

Now write the full corrected GROMACS workflow again.
"""

out = Path(f"agent/outputs/correction_prompts/{task_id}_correction_prompt.txt")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(prompt)

print("Created:", out)
