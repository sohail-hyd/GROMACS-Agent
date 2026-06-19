from pathlib import Path

BASE = Path(__file__).resolve().parents[1]

required = [
    "agent/gromacs_agent.py",
    "agent_v2/run_mdagent_style_demo.py",
    "app.py",
    "data/gscf_dataset",
    "data/geqs_dataset",
    "results/mdagent_style_demo/mdagent_style_demo_summary.csv",
    "docs/gromacs_agent_architecture.md",
    "docs/reference_style_agent_status.md",
    "paper_dataset/GSCF",
    "paper_dataset/GEQS",
    "paper_dataset/demo_results",
    "README.md"
]

print("\nGROMACS-Agent package status\n")

ok = 0
for item in required:
    p = BASE / item
    if p.exists():
        print("[OK]     ", item)
        ok += 1
    else:
        print("[MISSING]", item)

print(f"\nCompleted: {ok}/{len(required)} required items")

gscf = list((BASE / "paper_dataset/GSCF").glob("*.json")) if (BASE / "paper_dataset/GSCF").exists() else []
geqs = list((BASE / "paper_dataset/GEQS").glob("*.json")) if (BASE / "paper_dataset/GEQS").exists() else []

print(f"GSCF records in paper_dataset: {len(gscf)}")
print(f"GEQS records in paper_dataset: {len(geqs)}")

csv = BASE / "results/mdagent_style_demo/mdagent_style_demo_summary.csv"
if csv.exists():
    print("\nMDAgent-style demo summary:")
    print(csv.read_text())
