import json
from pathlib import Path

task_id = "GSCF_002"

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
1. Keep the workflow focused on oxygen-oxygen RDF of pure water at 300 K.
2. Fix every detected error.
3. Use safe topology preparation.
4. Use clear minimization, NVT, NPT, and production steps.
5. Use C-rescale barostat for NPT.
6. Include a correct RDF command such as:
   gmx rdf -f md.xtc -s md.tpr -o rdf_OW_OW.xvg -ref "name OW" -sel "name OW"
7. Use non-interactive or explicit selection handling for energy validation commands.
8. Clearly state that 1 ns or shorter production is workflow validation/basic RDF only, not final publication-quality RDF.
9. Suggest optional longer production or NVT production after NPT equilibration for cleaner structural analysis.
10. Include expected output files.
11. Include common errors and fixes.
12. End with one clear final validation note.

Now write the full corrected workflow again.
"""

out = Path(f"agent/outputs/correction_prompts/{task_id}_correction_prompt.txt")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(prompt)

print("Created:", out)
