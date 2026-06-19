import json
from pathlib import Path

task_id = "GSCF_003"

original_prompt = Path(f"agent/outputs/worker_prompts/{task_id}_worker_prompt.txt").read_text()
corrected_v1 = Path(f"agent/outputs/corrected_worker_outputs/{task_id}_corrected_worker_output.txt").read_text()
evaluation_v1 = json.loads(Path(f"agent/outputs/corrected_evaluator_outputs/{task_id}_corrected_eval.json").read_text())

detected_errors = "\n".join(f"- {e}" for e in evaluation_v1.get("detected_errors", []))
correction_suggestions = "\n".join(f"- {s}" for s in evaluation_v1.get("correction_suggestions", []))

prompt = f"""
You are a strict GROMACS workflow correction agent.

The previous corrected workflow still scored only {evaluation_v1.get("score")}/10.
Your task is to produce a second corrected version that directly fixes every remaining error.

Original task:
{original_prompt}

Previous corrected workflow:
{corrected_v1}

Remaining evaluator errors:
{detected_errors}

Required corrections:
{correction_suggestions}

Mandatory changes for this version:
1. After NPT equilibration, run production MD in NVT at fixed equilibrated volume.
2. Do not rely on a fixed make_ndx group number such as 'name 3 Water_Oxygen'. If make_ndx is used, say to use the actual group number printed after creating the OW group.
3. Prefer direct modern GROMACS selection syntax for MSD if available.
4. Do not use invalid options such as '-type no'.
5. Clearly state whether the MSD is oxygen-tracer MSD or molecule/COM MSD.
6. Include a clear warning that the linear fitting range must be visually inspected before reporting the diffusion coefficient.
7. Include finite-size-effect warning for a 3 nm water box.
8. Include a single final validation note at the end.
9. Keep topology preparation safe and consistent.
10. Do not mix water models unclearly. Use one consistent water model and topology.

Now write the full corrected GROMACS workflow again.
"""

out = Path(f"agent/outputs/correction_prompts/{task_id}_correction_prompt_v2.txt")
out.write_text(prompt)

print("Created:", out)
