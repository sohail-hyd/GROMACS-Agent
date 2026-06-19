import csv
import json
from pathlib import Path

BASE = Path(".")
OUT = BASE / "results" / "tables"
OUT.mkdir(parents=True, exist_ok=True)

def read_json_files(folder):
    records = []
    for p in sorted(Path(folder).glob("*.json")):
        try:
            d = json.loads(p.read_text())
            d["_file"] = str(p)
            records.append(d)
        except Exception as e:
            print(f"Warning: could not read {p}: {e}")
    return records

def write_csv(path, rows, fieldnames):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in fieldnames})
    print("Created:", path)

# Table 1: GSCF dataset summary
gscf = read_json_files("data/gscf_dataset")
gscf_rows = []
for d in gscf:
    gscf_rows.append({
        "task_id": d.get("id", ""),
        "task_type": d.get("task_type", ""),
        "system": d.get("system", ""),
        "temperature_K": d.get("temperature_K", ""),
        "pressure_bar": d.get("pressure_bar", ""),
        "task_description": d.get("user_task", d.get("instruction", d.get("task", "")))
    })

write_csv(
    OUT / "table_1_gscf_dataset_summary.csv",
    gscf_rows,
    ["task_id", "task_type", "system", "temperature_K", "pressure_bar", "task_description"]
)

# Table 2: GSCF baseline scores
baseline_path = Path("results/baseline_tests/manual_llm_baseline_scores.csv")
if baseline_path.exists():
    with baseline_path.open() as f:
        baseline_rows = list(csv.DictReader(f))
    write_csv(
        OUT / "table_2_gscf_baseline_scores.csv",
        baseline_rows,
        baseline_rows[0].keys() if baseline_rows else ["task_id"]
    )

# Table 3: GEQS evaluator accuracy
geqs_scores_path = Path("results/evaluator_tests/geqs_evaluator_scores.csv")
if geqs_scores_path.exists():
    with geqs_scores_path.open() as f:
        geqs_rows = list(csv.DictReader(f))
    write_csv(
        OUT / "table_3_geqs_evaluator_accuracy.csv",
        geqs_rows,
        geqs_rows[0].keys() if geqs_rows else ["task_id"]
    )

# Table 4: Correction-loop improvement
corr_path = Path("results/correction_tests/correction_results_overview.csv")
if corr_path.exists():
    with corr_path.open() as f:
        corr_rows = list(csv.DictReader(f))
    write_csv(
        OUT / "table_4_correction_loop_improvement.csv",
        corr_rows,
        corr_rows[0].keys() if corr_rows else ["task_id"]
    )

# Summary statistics
summary_lines = []

summary_lines.append("Publication result tables summary")
summary_lines.append("")

summary_lines.append(f"GSCF dataset records: {len(gscf_rows)}")

if baseline_path.exists():
    scores = []
    for r in baseline_rows:
        value = r.get("evaluator_score") or r.get("score")
        if value not in (None, ""):
            scores.append(float(value))
    if scores:
        summary_lines.append(f"GSCF baseline tasks: {len(scores)}")
        summary_lines.append(f"GSCF average score: {sum(scores)/len(scores):.3f}")
        summary_lines.append(f"GSCF minimum score: {min(scores):.1f}")
        summary_lines.append(f"GSCF maximum score: {max(scores):.1f}")

if geqs_scores_path.exists():
    expert = []
    evaluator = []
    abs_errors = []
    for r in geqs_rows:
        expert.append(float(r["expert_score"]))
        evaluator.append(float(r["evaluator_score"]))
        abs_errors.append(float(r["absolute_error"]))
    if expert:
        mae = sum(abs_errors) / len(abs_errors)
        mse = sum((a-b)**2 for a, b in zip(expert, evaluator)) / len(expert)
        rmse = mse ** 0.5
        exact = sum(1 for a, b in zip(expert, evaluator) if a == b)
        summary_lines.append(f"GEQS evaluator tasks: {len(expert)}")
        summary_lines.append(f"GEQS MAE: {mae:.3f}")
        summary_lines.append(f"GEQS MSE: {mse:.3f}")
        summary_lines.append(f"GEQS RMSE: {rmse:.3f}")
        summary_lines.append(f"GEQS exact matches: {exact}/{len(expert)}")

if corr_path.exists():
    improvements = []
    for r in corr_rows:
        value = r.get("net_improvement")
        if value not in (None, "", "NA"):
            improvements.append(float(value))
    if improvements:
        summary_lines.append(f"Correction-loop tested tasks: {len(improvements)}")
        summary_lines.append(f"Average correction improvement: {sum(improvements)/len(improvements):.3f}")
        summary_lines.append(f"Improved tasks: {sum(1 for x in improvements if x > 0)}/{len(improvements)}")

summary_text = "\n".join(summary_lines) + "\n"
(OUT / "publication_result_tables_summary.txt").write_text(summary_text)
print("")
print(summary_text)
