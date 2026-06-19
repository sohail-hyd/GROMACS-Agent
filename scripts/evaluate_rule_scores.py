import json
import math
import sys
from pathlib import Path

sys.path.append("agent")
from simple_rule_evaluator import evaluate_workflow

records = sorted(Path("data/geqs_dataset").glob("*.json"))

abs_errors = []
sq_errors = []

print("Rule Evaluator vs Expert Scores")
print("=" * 70)

for path in records:
    with open(path, "r") as f:
        record = json.load(f)

    workflow_text = json.dumps(record.get("generated_workflow", {}), indent=2)
    pred = evaluate_workflow(workflow_text)

    expert = record["expert_score"]
    predicted = pred["score"]
    err = predicted - expert

    abs_errors.append(abs(err))
    sq_errors.append(err ** 2)

    print(f"{record['id']}: expert={expert}, predicted={predicted}, error={err}")

mae = sum(abs_errors) / len(abs_errors)
mse = sum(sq_errors) / len(sq_errors)
rmse = math.sqrt(mse)

print("=" * 70)
print(f"MAE  = {mae:.4f}")
print(f"MSE  = {mse:.4f}")
print(f"RMSE = {rmse:.4f}")
