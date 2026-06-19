import subprocess
from pathlib import Path
import json
import csv

BASE = Path(__file__).resolve().parents[1]
RUNS = BASE / "agent" / "outputs" / "agent_runs"

tasks = [
    ("DEMO_001", "Generate a GROMACS workflow to calculate O-O RDF of pure water at 300 K"),
    ("DEMO_002", "Generate a GROMACS workflow to extract temperature time series of pure water at 300 K"),
    ("DEMO_003", "Generate a GROMACS workflow to calculate density of pure water at 300 K"),
    ("DEMO_004", "Generate a GROMACS workflow to calculate MSD and diffusion of pure water at 300 K"),
    ("DEMO_005", "Generate a GROMACS workflow to preprocess a pure water trajectory using PBC correction")
]

summary = []

for task_id, task in tasks:
    print("\nRunning", task_id)
    before = set(RUNS.glob("*")) if RUNS.exists() else set()

    subprocess.run(
        ["python3", "agent/gromacs_agent.py", "--task", task],
        cwd=BASE,
        check=True
    )

    after = set(RUNS.glob("*"))
    new_runs = sorted(after - before)
    run_dir = new_runs[-1] if new_runs else sorted(RUNS.glob("*"))[-1]

    evaluation = json.loads((run_dir / "final_evaluation.json").read_text())
    retrieved = json.loads((run_dir / "retrieved_examples.json").read_text())
    retrieved_ids = [r.get("id", "unknown") for r in retrieved]

    summary.append({
        "task_id": task_id,
        "task": task,
        "run_folder": str(run_dir),
        "retrieved_examples": ";".join(retrieved_ids),
        "final_score": evaluation["score"],
        "decision": evaluation["decision"]
    })

out = BASE / "results" / "agent_demo"
out.mkdir(parents=True, exist_ok=True)

csv_path = out / "gromacs_agent_demo_summary.csv"
with csv_path.open("w", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["task_id", "task", "run_folder", "retrieved_examples", "final_score", "decision"]
    )
    writer.writeheader()
    writer.writerows(summary)

print("\nGROMACS-Agent demo complete")
print("Summary:", csv_path)
print(csv_path.read_text())
