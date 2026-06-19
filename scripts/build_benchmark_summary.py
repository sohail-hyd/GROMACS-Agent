import csv
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]

OUT = BASE / "results" / "benchmark"
OUT.mkdir(parents=True, exist_ok=True)

GSCF = BASE / "data" / "gscf_dataset"
GEQS = BASE / "data" / "geqs_dataset"
FT_WORKER = BASE / "fine_tuning" / "GSCF_GromacsWorker_SFT_Alpaca.json"
FT_EVAL = BASE / "fine_tuning" / "GEQS_GromacsEvaluator_SFT_Alpaca.json"
DEMO = BASE / "results" / "mdagent_style_demo" / "mdagent_style_demo_summary.csv"
EXEC = BASE / "results" / "executor_tests"

def count_json_files(path):
    return len(list(path.glob("*.json"))) if path.exists() else 0

def count_json_records(path):
    if not path.exists():
        return 0
    try:
        data = json.loads(path.read_text())
        return len(data) if isinstance(data, list) else 0
    except Exception:
        return 0

def read_demo_rows():
    if not DEMO.exists():
        return []
    with DEMO.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def read_executor_status():
    rows = []
    if not EXEC.exists():
        return rows
    for report in EXEC.glob("*/execution_report.json"):
        try:
            data = json.loads(report.read_text())
            rows.append({
                "task": data.get("task", report.parent.name),
                "status": data.get("status", "unknown"),
                "outputs": "; ".join(data.get("generated_outputs", [])),
                "report_path": str(report.relative_to(BASE)),
            })
        except Exception:
            continue
    return rows

# 1. Dataset scale summary
dataset_summary = [
    {"item": "GSCF curated workflow records", "count": count_json_files(GSCF)},
    {"item": "GEQS curated evaluator records", "count": count_json_files(GEQS)},
    {"item": "Worker SFT Alpaca records", "count": count_json_records(FT_WORKER)},
    {"item": "Evaluator SFT Alpaca records", "count": count_json_records(FT_EVAL)},
]

with (OUT / "dataset_scale_summary.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["item", "count"])
    writer.writeheader()
    writer.writerows(dataset_summary)

# 2. Agent benchmark from demo summary
demo_rows = read_demo_rows()
benchmark_rows = []

for row in demo_rows:
    benchmark_rows.append({
        "benchmark_type": "MDAgent-style multi-agent demo",
        "task_id": row.get("task_id", row.get("id", "")),
        "task": row.get("task", row.get("user_task", "")),
        "retrieved_examples": row.get("retrieved_examples", row.get("retrieved_ids", "")),
        "final_evaluator_score": row.get("final_score", row.get("score", "")),
        "decision": row.get("decision", ""),
        "agents": row.get("agents", row.get("agent_sequence", "")),
        "status": "completed_agent_generation_and_evaluation",
        "note": "This benchmark reports current GROMACS-Agent generation/evaluation behavior. Baseline external LLM comparison should be added after separate baseline testing."
    })

if not benchmark_rows:
    benchmark_rows.append({
        "benchmark_type": "MDAgent-style multi-agent demo",
        "task_id": "pending",
        "task": "No demo summary found",
        "retrieved_examples": "",
        "final_evaluator_score": "",
        "decision": "",
        "agents": "",
        "status": "pending",
        "note": "Run agent_v2/run_mdagent_style_demo.py to generate demo benchmark results."
    })

with (OUT / "gromacs_agent_benchmark_summary.csv").open("w", newline="", encoding="utf-8") as f:
    fieldnames = list(benchmark_rows[0].keys())
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(benchmark_rows)

# 3. Executor evidence summary
executor_rows = read_executor_status()
if not executor_rows:
    executor_rows = [{
        "task": "pending",
        "status": "pending",
        "outputs": "",
        "report_path": "",
    }]

with (OUT / "executor_evidence_summary.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["task", "status", "outputs", "report_path"])
    writer.writeheader()
    writer.writerows(executor_rows)

# 4. Markdown report for docs
md = []
md.append("# GROMACS-Agent benchmark and evaluation summary\n")
md.append("## Dataset scale\n")
for item in dataset_summary:
    md.append(f"- {item['item']}: {item['count']}")
md.append("\n## Agent benchmark summary\n")
md.append("The current benchmark uses the MDAgent-style multi-agent demo results stored in `results/mdagent_style_demo/`.")
md.append("These results report generation, retrieval, evaluation, correction-loop behavior, and final evaluator scores.")
md.append("\n## Executor evidence\n")
for row in executor_rows:
    md.append(f"- {row['task']}: {row['status']} | outputs: {row['outputs']}")
md.append("\n## Important limitation\n")
md.append("This benchmark summary does not yet claim a measured human time-reduction percentage or superiority over external LLM baselines. Those claims require a separate controlled baseline/user study.")
md.append("\n## Generated CSV files\n")
md.append("- `results/benchmark/dataset_scale_summary.csv`")
md.append("- `results/benchmark/gromacs_agent_benchmark_summary.csv`")
md.append("- `results/benchmark/executor_evidence_summary.csv`")

(BASE / "docs" / "benchmark_evaluation_summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")

print("Created benchmark summary files:")
print(" - results/benchmark/dataset_scale_summary.csv")
print(" - results/benchmark/gromacs_agent_benchmark_summary.csv")
print(" - results/benchmark/executor_evidence_summary.csv")
print(" - docs/benchmark_evaluation_summary.md")
print()
print("Dataset scale:")
for item in dataset_summary:
    print(f" - {item['item']}: {item['count']}")
print()
print(f"Agent benchmark rows: {len(benchmark_rows)}")
print(f"Executor evidence rows: {len(executor_rows)}")
