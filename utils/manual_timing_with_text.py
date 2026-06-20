import csv
import subprocess
import time
from pathlib import Path

tasks = [
    ("TIME_001", "O-O RDF calculation"),
    ("TIME_002", "Temperature time-series extraction"),
    ("TIME_003", "Density calculation"),
    ("TIME_004", "MSD and diffusion"),
    ("TIME_005", "PBC trajectory preprocessing"),
    ("TIME_006", "Li-O and Br-O RDF"),
    ("TIME_007", "Hydrogen-bond analysis"),
    ("TIME_008", "Density profile along z"),
    ("TIME_009", "Coordination number"),
    ("TIME_010", "Equilibration validation"),
]

timing_file = Path("results/time_study/manual_timing/manual_timing_raw.csv")
workflow_dir = Path("results/time_study/manual_workflows")
workflow_dir.mkdir(parents=True, exist_ok=True)
timing_file.parent.mkdir(parents=True, exist_ok=True)

print("\nManual GROMACS workflow timing with saved text evidence\n")
for i, (_, task) in enumerate(tasks, start=1):
    print(f"{i}. {task}")

choice = int(input("\nTask number: "))
task_id, task = tasks[choice - 1]

workflow_file = workflow_dir / f"{task_id}_manual_workflow.md"

template = f"""# {task_id}: {task}

Write the complete manual GROMACS workflow below.

Include:
1. Required input files
2. Required topology/MDP/TPR files
3. Command sequence
4. Analysis command
5. Expected output files
6. Validation note

Manual workflow:
"""

workflow_file.write_text(template)

print(f"\nNano editor will open now: {workflow_file}")
print("Write the workflow manually. Save with Ctrl+O, Enter, then exit with Ctrl+X.")
input("Press Enter to START timing and open editor...")

start = time.time()
subprocess.run(["nano", str(workflow_file)])
end = time.time()

text = workflow_file.read_text()
word_count = len(text.split())
seconds = end - start
minutes = seconds / 60

file_exists = timing_file.exists()
with timing_file.open("a", newline="") as f:
    writer = csv.writer(f)
    if not file_exists or timing_file.stat().st_size == 0:
        writer.writerow(["task_id", "task", "manual_time_seconds", "manual_time_minutes", "manual_workflow_file", "word_count"])
    writer.writerow([task_id, task, f"{seconds:.2f}", f"{minutes:.2f}", str(workflow_file), word_count])

print(f"\nSaved timing:")
print(f"{task_id}, {task}")
print(f"Manual time: {seconds:.2f} seconds = {minutes:.2f} minutes")
print(f"Workflow file: {workflow_file}")
print(f"Word count: {word_count}")
