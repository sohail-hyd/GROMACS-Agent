import csv
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
INPUT = BASE / "results" / "benchmark" / "baseline_score_template.csv"
OUT_DIR = BASE / "results" / "benchmark"
DOC_DIR = BASE / "docs" / "paper_text"

OUT_DIR.mkdir(parents=True, exist_ok=True)
DOC_DIR.mkdir(parents=True, exist_ok=True)

OUT_CSV = OUT_DIR / "baseline_vs_agent_calculated.csv"
OUT_MD = DOC_DIR / "baseline_comparison_results_summary.md"

def is_number(x):
    try:
        float(x)
        return True
    except Exception:
        return False

if not INPUT.exists():
    raise FileNotFoundError(f"Missing file: {INPUT}")

rows = []
with INPUT.open(newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        baseline = row.get("baseline_score", "pending")
        agent = row.get("agent_score", "pending")

        if is_number(baseline) and is_number(agent):
            improvement = float(agent) - float(baseline)
            row["score_improvement"] = f"{improvement:.1f}"
            row["comparison_status"] = "complete"
        else:
            row["score_improvement"] = "pending"
            row["comparison_status"] = "pending_baseline_score"

        rows.append(row)

fieldnames = list(rows[0].keys())

with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

complete = [r for r in rows if r["comparison_status"] == "complete"]
pending = [r for r in rows if r["comparison_status"] != "complete"]

md = []
md.append("# Baseline vs GROMACS-Agent comparison summary\n")
md.append("## Current status\n")
md.append(f"- Total benchmark tasks: {len(rows)}")
md.append(f"- Completed baseline comparisons: {len(complete)}")
md.append(f"- Pending baseline comparisons: {len(pending)}")
md.append("\n## Benchmark tasks\n")

for r in rows:
    md.append(
        f"- {r.get('task_id','')}: {r.get('task','')} | "
        f"baseline score: {r.get('baseline_score','pending')} | "
        f"agent score: {r.get('agent_score','pending')} | "
        f"improvement: {r.get('score_improvement','pending')} | "
        f"status: {r.get('comparison_status','pending')}"
    )

md.append("\n## Important note\n")
md.append(
    "Baseline LLM scores must be measured before making claims about superiority, "
    "accuracy improvement, or time reduction. Until then, this table should be reported "
    "as a planned comparison framework."
)

OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")

print("Created:")
print(f" - {OUT_CSV}")
print(f" - {OUT_MD}")
print()
print(f"Total tasks: {len(rows)}")
print(f"Completed comparisons: {len(complete)}")
print(f"Pending comparisons: {len(pending)}")
