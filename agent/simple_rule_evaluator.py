import json
from pathlib import Path

def evaluate_workflow(text: str):
    lower = text.lower()
    score = 10
    errors = []
    suggestions = []
    rubric = {
        "syntax_correctness": 2,
        "workflow_sequence": 2,
        "parameter_rationality": 2,
        "analysis_correctness": 2,
        "completeness_reproducibility": 2
    }

    # Missing topology / wrong topology order
    if "-p topol.top" in lower and "gmx solvate" in lower:
        if "create topol.top" not in lower and "cat > topol.top" not in lower:
            score -= 6
            rubric["syntax_correctness"] = max(rubric["syntax_correctness"] - 1, 0)
            rubric["workflow_sequence"] = 0
            rubric["completeness_reproducibility"] = max(rubric["completeness_reproducibility"] - 1, 0)
            errors.append("topol.top is used with gmx solvate before being created.")
            suggestions.append("Create topol.top first, or generate the water box without -p, count SOL molecules, and then create topol.top manually.")

    # Berendsen barostat warning
    if "berendsen" in lower:
        score -= 4
        rubric["parameter_rationality"] = 1
        rubric["completeness_reproducibility"] = max(rubric["completeness_reproducibility"] - 1, 0)
        errors.append("Berendsen barostat is used and may trigger a warning/failure in newer GROMACS workflows.")
        suggestions.append("Use C-rescale for NPT equilibration instead of Berendsen.")

    # Invalid MSD option
    if "-type no" in lower:
        score -= 5
        rubric["syntax_correctness"] = 0
        rubric["analysis_correctness"] = max(rubric["analysis_correctness"] - 1, 0)
        errors.append("Invalid gmx msd option: -type no.")
        suggestions.append("Remove -type no for normal three-dimensional MSD analysis.")

    # Density workflow missing density extraction
    if "density" in lower and "gmx energy" not in lower and "md.edr" not in lower:
        score -= 1
        rubric["analysis_correctness"] = max(rubric["analysis_correctness"] - 1, 0)
        errors.append("Density extraction command may be missing.")
        suggestions.append("Use gmx energy to extract Density from md.edr.")

    score = max(score, 0)

    return {
        "score": score,
        "decision": "accept" if score >= 8 else "revise",
        "detected_errors": errors,
        "correction_suggestions": suggestions,
        "rubric": rubric
    }

def main():
    geqs_files = sorted(Path("data/geqs_dataset").glob("*.json"))

    for path in geqs_files:
        with open(path, "r") as f:
            record = json.load(f)

        workflow_text = json.dumps(record.get("generated_workflow", {}), indent=2)
        result = evaluate_workflow(workflow_text)

        print("=" * 70)
        print("File:", path)
        print("Dataset expert score:", record.get("expert_score"))
        print("Rule evaluator result:")
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
