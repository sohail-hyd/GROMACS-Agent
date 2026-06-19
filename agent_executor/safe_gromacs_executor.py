import argparse
import subprocess
import json
from pathlib import Path
from datetime import datetime

SAFE_TASKS = {
    "temperature": {
        "required": ["md.edr"],
        "commands": [
            "echo Temperature | gmx energy -f md.edr -o temperature_executor.xvg"
        ],
        "outputs": ["temperature_executor.xvg"]
    },
    "density": {
        "required": ["md.edr"],
        "commands": [
            "echo Density | gmx energy -f md.edr -o density_executor.xvg"
        ],
        "outputs": ["density_executor.xvg"]
    },
    "rdf_oo": {
        "required": ["md.xtc", "md.tpr"],
        "commands": [
            'gmx rdf -f md.xtc -s md.tpr -o rdf_OW_OW_executor.xvg -ref "name OW" -sel "name OW"'
        ],
        "outputs": ["rdf_OW_OW_executor.xvg"]
    },
    "msd": {
        "required": ["md.xtc", "md.tpr"],
        "commands": [
            "echo System | gmx trjconv -s md.tpr -f md.xtc -o md_nojump_executor.xtc -pbc nojump",
            "gmx msd -f md_nojump_executor.xtc -s md.tpr -o msd_executor.xvg"
        ],
        "outputs": ["md_nojump_executor.xtc", "msd_executor.xvg"]
    },
    "pbc_nojump": {
        "required": ["md.xtc", "md.tpr"],
        "commands": [
            "echo System | gmx trjconv -s md.tpr -f md.xtc -o md_nojump_executor.xtc -pbc nojump"
        ],
        "outputs": ["md_nojump_executor.xtc"]
    }
}

def run_command(command, workdir, timeout=300):
    p = subprocess.run(
        command,
        shell=True,
        cwd=workdir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout
    )
    return {
        "command": command,
        "returncode": p.returncode,
        "stdout": p.stdout,
        "stderr": p.stderr
    }

def main():
    parser = argparse.ArgumentParser(description="Safe GROMACS executor for selected validated tasks")
    parser.add_argument("--task", required=True, choices=SAFE_TASKS.keys())
    parser.add_argument("--workdir", required=True)
    args = parser.parse_args()

    workdir = Path(args.workdir).resolve()
    task = SAFE_TASKS[args.task]

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    outdir = Path.cwd() / "results" / "executor_tests" / f"{args.task}_{run_id}"
    outdir.mkdir(parents=True, exist_ok=True)

    report = {
        "task": args.task,
        "workdir": str(workdir),
        "execution_mode": "safe_selected_gromacs_commands",
        "required_files": task["required"],
        "missing_files": [],
        "commands": task["commands"],
        "command_results": [],
        "expected_outputs": task["outputs"],
        "generated_outputs": [],
        "status": "not_started"
    }

    if not workdir.exists():
        report["status"] = "failed"
        report["missing_files"] = ["workdir_not_found"]
        (outdir / "execution_report.json").write_text(json.dumps(report, indent=2))
        print(json.dumps(report, indent=2))
        return

    for f in task["required"]:
        if not (workdir / f).exists():
            report["missing_files"].append(f)

    if report["missing_files"]:
        report["status"] = "failed_missing_files"
        (outdir / "execution_report.json").write_text(json.dumps(report, indent=2))
        print(json.dumps(report, indent=2))
        return

    report["status"] = "running"

    for command in task["commands"]:
        result = run_command(command, workdir)
        report["command_results"].append(result)
        if result["returncode"] != 0:
            report["status"] = "failed_command_error"
            break

    for f in task["outputs"]:
        if (workdir / f).exists():
            report["generated_outputs"].append(f)

    if report["status"] == "running":
        if set(task["outputs"]).issubset(set(report["generated_outputs"])):
            report["status"] = "success"
        else:
            report["status"] = "partial_output_missing"

    (outdir / "execution_report.json").write_text(json.dumps(report, indent=2))
    (outdir / "execution_summary.txt").write_text(
        f"Task: {args.task}\n"
        f"Status: {report['status']}\n"
        f"Workdir: {workdir}\n"
        f"Generated outputs: {report['generated_outputs']}\n"
    )

    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
