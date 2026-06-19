import subprocess
import json
import shutil
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parents[1]
OLD_RUNS = BASE / "agent" / "outputs" / "agent_runs"
NEW_RUNS = BASE / "agent_v2" / "runs"
NEW_RUNS.mkdir(parents=True, exist_ok=True)

def latest_old_run():
    runs = sorted(OLD_RUNS.glob("*"), key=lambda p: p.stat().st_mtime)
    return runs[-1]

def run(task):
    before = set(OLD_RUNS.glob("*")) if OLD_RUNS.exists() else set()

    subprocess.run(
        ["python3", "agent/gromacs_agent.py", "--task", task],
        cwd=BASE,
        check=True
    )

    after = set(OLD_RUNS.glob("*"))
    new_runs = sorted(after - before, key=lambda p: p.stat().st_mtime)
    source_run = new_runs[-1] if new_runs else latest_old_run()

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    target_run = NEW_RUNS / run_id
    target_run.mkdir(parents=True, exist_ok=True)

    for f in source_run.glob("*"):
        shutil.copy(f, target_run / f.name)

    workflow = (target_run / "final_workflow.md").read_text()
    evaluation = json.loads((target_run / "final_evaluation.json").read_text())
    retrieved = json.loads((target_run / "retrieved_examples.json").read_text())
    retrieved_ids = [r.get("id", "unknown") for r in retrieved]

    transcript = [
        {
            "agent": "ManagerAgent",
            "role": "Interpret user task and coordinate the agent team",
            "task": task
        },
        {
            "agent": "PlannerAgent",
            "role": "Decompose the GROMACS task",
            "plan": [
                "identify required GROMACS files",
                "retrieve related GSCF examples",
                "generate workflow",
                "evaluate workflow",
                "apply correction loop if needed",
                "save final workflow"
            ]
        },
        {
            "agent": "Retriever",
            "role": "Retrieve validated GSCF memory records",
            "retrieved_examples": retrieved_ids
        },
        {
            "agent": "GromacsWorkerAgent",
            "role": "Generate topology-aware GROMACS workflow",
            "output_file": "final_workflow.md"
        },
        {
            "agent": "GromacsEvaluatorAgent",
            "role": "Score the workflow using scientific rubric",
            "score": evaluation.get("score"),
            "decision": evaluation.get("decision"),
            "detected_errors": evaluation.get("detected_errors", [])
        },
        {
            "agent": "CodeExecutorAgent",
            "role": "Execution-aware dry-run checker",
            "status": "dry_run_only",
            "note": "Automatic GROMACS execution is disabled in this prototype; selected benchmark tasks can be executed manually."
        }
    ]

    (target_run / "mdagent_style_transcript.json").write_text(json.dumps(transcript, indent=2))

    print("MDAgent-style GROMACS-Agent run complete")
    print("Run folder:", target_run)
    print("Retrieved:", retrieved_ids)
    print("Score:", evaluation.get("score"))
    print("Decision:", evaluation.get("decision"))

if __name__ == "__main__":
    task = "Generate a GROMACS workflow to calculate O-O RDF of pure water at 300 K"
    run(task)
