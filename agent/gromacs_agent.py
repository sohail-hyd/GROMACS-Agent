import argparse
import json
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parents[1]
RUNS = BASE / "agent" / "outputs" / "agent_runs"
RUNS.mkdir(parents=True, exist_ok=True)

def retrieve_examples(task, max_examples=3):
    records = []
    data_dir = BASE / "data" / "gscf_dataset"

    if not data_dir.exists():
        return []

    task_words = set(task.lower().replace("-", " ").split())

    for p in sorted(data_dir.glob("*.json")):
        try:
            d = json.loads(p.read_text())
            text = json.dumps(d).lower()
            score = sum(1 for w in task_words if w in text)
            records.append((score, d))
        except Exception:
            pass

    records.sort(key=lambda x: x[0], reverse=True)
    return [d for score, d in records[:max_examples] if score > 0]

def manager(task):
    return {
        "role": "Manager",
        "interpreted_task": task,
        "goal": "Generate a reproducible GROMACS workflow with validation."
    }

def planner(task):
    return {
        "role": "Planner",
        "subtasks": [
            "Identify required input files.",
            "Prepare or verify topology and coordinate files.",
            "Define MDP/settings if simulation is required.",
            "Generate ordered GROMACS commands.",
            "Add analysis/post-processing commands.",
            "Add expected outputs.",
            "Add common errors and fixes.",
            "Add validation and short-trajectory warning."
        ]
    }

def worker(task, examples):
    task_lower = task.lower()

    if "rdf" in task_lower and ("o-o" in task_lower or "oxygen" in task_lower):
        analysis = """gmx rdf -f md.xtc -s md.tpr -o rdf_OW_OW.xvg -ref "name OW" -sel "name OW"
"""
        expected = "rdf_OW_OW.xvg"
        note = "Check that the first O-O RDF peak is physically reasonable. For pure water, the first O-O peak is commonly near 0.28 nm."
    elif "temperature" in task_lower:
        analysis = """echo Temperature | gmx energy -f md.edr -o temperature.xvg
"""
        expected = "temperature.xvg"
        note = "Temperature should fluctuate around the target temperature, for example 300 K."
    elif "density" in task_lower:
        analysis = """echo Density | gmx energy -f md.edr -o density.xvg
"""
        expected = "density.xvg"
        note = "Average density should be checked against expected water density near the simulated thermodynamic state."
    elif "msd" in task_lower or "diffusion" in task_lower:
        analysis = """echo System | gmx trjconv -s md.tpr -f md.xtc -o md_nojump.xtc -pbc nojump
gmx msd -f md_nojump.xtc -s md.tpr -o msd_water.xvg
"""
        expected = "md_nojump.xtc, msd_water.xvg"
        note = "Use the linear MSD region only. Short trajectories are workflow-validation tests, not final diffusion estimates."
    else:
        analysis = """# Replace this block with task-specific GROMACS commands.
# Use non-interactive selections where possible.
"""
        expected = "task-specific output files"
        note = "Validate both command execution and scientific meaning of outputs."

    retrieved_ids = [ex.get("id", "unknown") for ex in examples]

    workflow = f"""# GROMACS-Agent Generated Workflow

## User task
{task}

## Retrieved validated workflow examples
{retrieved_ids}

## Required input files
- `topol.top`
- coordinate file such as `water_box.gro`, `npt.gro`, or `md.gro`
- trajectory file such as `md.xtc` when post-processing is required
- run input file such as `md.tpr`
- energy file such as `md.edr` when energy analysis is required

## Topology and preparation check
Before running `gmx grompp`, confirm that `topol.top` exists and that the molecule count in `[ molecules ]` matches the coordinate file.

If the system is solvated using `gmx solvate`, count the final water molecules after solvation and write the correct `SOL` number into `topol.top`.

## Main analysis command
```bash
{analysis}```

## Expected output
{expected}

## Common errors and fixes
- Missing topology file: create or verify `topol.top`.
- Wrong solvent count: update `[ molecules ]` after `gmx solvate`.
- Wrong atom selection: check atom names in `.gro`, `.top`, or index groups.
- Interactive selection problem: use `echo` or explicit selections where possible.
- Short trajectory: do not claim publication-quality physical properties from very short tests.

## Validation note
{note}

The generated workflow is considered valid only if commands run without fatal GROMACS errors and outputs are physically meaningful.
"""
    return workflow

def evaluator(workflow):
    text = workflow.lower()
    errors = []
    score = 10

    if "topol.top" not in text:
        errors.append("Missing topology discussion.")
        score -= 2
    if "validation note" not in text:
        errors.append("Missing validation note.")
        score -= 1
    if "short trajectory" not in text:
        errors.append("Missing short-trajectory warning.")
        score -= 1
    if "-type no" in text:
        errors.append("Invalid GROMACS MSD option: -type no.")
        score -= 2
    if "echo" not in text and "non-interactive" not in text:
        errors.append("Weak reproducible interactive-selection handling.")
        score -= 1

    score = max(0, min(10, score))

    return {
        "score": score,
        "decision": "accept" if score >= 8 else "revise",
        "detected_errors": errors,
        "rubric": {
            "syntax_correctness": 2 if score >= 8 else 1,
            "workflow_sequence": 2 if score >= 8 else 1,
            "parameter_rationality": 2 if score >= 8 else 1,
            "analysis_correctness": 2 if score >= 8 else 1,
            "completeness_reproducibility": 2 if score >= 8 else 1
        }
    }

def correction_loop(workflow, evaluation):
    if evaluation["score"] >= 8:
        return workflow

    correction = "\n\n## Evaluator-guided correction\n"
    correction += "The evaluator requested revision for these issues:\n"
    for e in evaluation["detected_errors"]:
        correction += f"- {e}\n"

    correction += """
Correction rules added:
- Include topology verification.
- Include validation note.
- Use reproducible non-interactive GROMACS selections.
- Include a short-trajectory warning.
- Avoid invalid command options.
"""
    return workflow + correction

def run(task):
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    run_dir = RUNS / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    m = manager(task)
    p = planner(task)
    examples = retrieve_examples(task)
    workflow = worker(task, examples)
    initial_eval = evaluator(workflow)
    corrected = correction_loop(workflow, initial_eval)
    final_eval = evaluator(corrected)

    (run_dir / "task.txt").write_text(task)
    (run_dir / "manager.json").write_text(json.dumps(m, indent=2))
    (run_dir / "planner.json").write_text(json.dumps(p, indent=2))
    (run_dir / "retrieved_examples.json").write_text(json.dumps(examples, indent=2))
    (run_dir / "worker_output.md").write_text(workflow)
    (run_dir / "initial_evaluation.json").write_text(json.dumps(initial_eval, indent=2))
    (run_dir / "final_workflow.md").write_text(corrected)
    (run_dir / "final_evaluation.json").write_text(json.dumps(final_eval, indent=2))

    print("GROMACS-Agent run complete")
    print("Run folder:", run_dir)
    print("Initial score:", initial_eval["score"])
    print("Final score:", final_eval["score"])
    print("Decision:", final_eval["decision"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GROMACS-Agent prototype")
    parser.add_argument("--task", required=True)
    args = parser.parse_args()
    run(args.task)
