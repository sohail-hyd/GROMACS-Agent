import json
from pathlib import Path

task_id = "GSCF_009"

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

Mandatory corrections for trajectory preprocessing:
1. Keep the workflow focused on PBC correction, molecule-whole reconstruction, centering, and cleaned trajectory generation.
2. Do not overwrite md.xtc.
3. Explain the purpose of -pbc nojump, -pbc mol, and -center.
4. Use clear non-interactive selection handling, for example printf-based selections.
5. For homogeneous pure water, selecting System is acceptable.
6. State that for solute-water systems, the solute should usually be centered instead of the whole System.
7. Warn that md_center.xtc is good for visualization and many structural analyses, but MSD/diffusion may require md_nojump.xtc or an unwrapped trajectory.
8. Include a reproducible visual-inspection command, such as extracting a frame to check_frame.gro.
9. Include expected output files.
10. Include common errors and fixes.
11. End with one clear final validation note.

Now write the full corrected GROMACS workflow again.
"""

out = Path(f"agent/outputs/correction_prompts/{task_id}_correction_prompt.txt")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(prompt)

print("Created:", out)
