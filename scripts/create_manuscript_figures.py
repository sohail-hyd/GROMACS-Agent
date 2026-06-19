import csv
from pathlib import Path
import matplotlib.pyplot as plt

FIG = Path("figures")
FIG.mkdir(exist_ok=True)

def read_csv(path):
    with open(path) as f:
        return list(csv.DictReader(f))

# -----------------------------
# Figure 1: GSCF baseline scores
# -----------------------------
baseline_path = Path("results/tables/table_2_gscf_baseline_scores.csv")
baseline = read_csv(baseline_path)

task_ids = [r["task_id"] for r in baseline]
scores = [float(r["evaluator_score"]) for r in baseline]

plt.figure(figsize=(10, 5))
plt.bar(task_ids, scores)
plt.ylim(0, 10)
plt.xlabel("GSCF task ID")
plt.ylabel("Evaluator score / 10")
plt.title("Manual LLM Baseline Performance on GSCF Workflow Tasks")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(FIG / "figure_1_gscf_baseline_scores.png", dpi=300)
plt.close()

# -----------------------------
# Figure 2: GEQS expert vs evaluator scores
# -----------------------------
geqs_path = Path("results/tables/table_3_geqs_evaluator_accuracy.csv")
geqs = read_csv(geqs_path)

geqs_ids = [r["task_id"] for r in geqs]
expert_scores = [float(r["expert_score"]) for r in geqs]
evaluator_scores = [float(r["evaluator_score"]) for r in geqs]

plt.figure(figsize=(10, 5))
plt.plot(geqs_ids, expert_scores, marker="o", label="Expert score")
plt.plot(geqs_ids, evaluator_scores, marker="s", label="Evaluator score")
plt.ylim(0, 10)
plt.xlabel("GEQS task ID")
plt.ylabel("Score / 10")
plt.title("Evaluator Agreement with Expert Scores on GEQS Error Cases")
plt.xticks(rotation=45, ha="right")
plt.legend()
plt.tight_layout()
plt.savefig(FIG / "figure_2_geqs_expert_vs_evaluator.png", dpi=300)
plt.close()

# -----------------------------
# Figure 3: Correction-loop improvement
# -----------------------------
corr_path = Path("results/tables/table_4_correction_loop_improvement.csv")
corr = read_csv(corr_path)

corr_ids = [r["task_id"] for r in corr]
baseline_scores = [float(r["baseline_score"]) for r in corr]
best_scores = [float(r["best_corrected_score"]) for r in corr]

x = range(len(corr_ids))
width = 0.35

plt.figure(figsize=(9, 5))
plt.bar([i - width/2 for i in x], baseline_scores, width, label="Baseline")
plt.bar([i + width/2 for i in x], best_scores, width, label="Best corrected")
plt.ylim(0, 10)
plt.xlabel("Correction-tested task ID")
plt.ylabel("Evaluator score / 10")
plt.title("Evaluator-Guided Correction Improves Weaker Workflows")
plt.xticks(list(x), corr_ids, rotation=45, ha="right")
plt.legend()
plt.tight_layout()
plt.savefig(FIG / "figure_3_correction_loop_improvement.png", dpi=300)
plt.close()

# -----------------------------
# Figure 4: GEQS absolute error
# -----------------------------
abs_errors = [float(r["absolute_error"]) for r in geqs]

plt.figure(figsize=(10, 5))
plt.bar(geqs_ids, abs_errors)
plt.ylim(0, max(1, max(abs_errors) + 0.5))
plt.xlabel("GEQS task ID")
plt.ylabel("Absolute error")
plt.title("Absolute Error Between Expert and Evaluator Scores")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(FIG / "figure_4_geqs_absolute_error.png", dpi=300)
plt.close()

print("Created manuscript figures:")
for p in sorted(FIG.glob("figure_*.png")):
    print(p)
