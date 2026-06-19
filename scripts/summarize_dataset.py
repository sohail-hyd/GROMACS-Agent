import json
from pathlib import Path

root = Path("data")
files = sorted(root.glob("*_dataset/*.json"))

print("Dataset Summary")
print("=" * 60)

for file in files:
    with open(file, "r") as f:
        data = json.load(f)

    print(f"File: {file}")
    print(f"ID: {data.get('id')}")
    print(f"Type: {data.get('task_type')}")
    print(f"Software: {data.get('software')}")
    if "validated_result" in data:
        print(f"Validated result: {data['validated_result']}")
    if "expert_score" in data:
        print(f"Expert score: {data['expert_score']}")
        print(f"Error type: {data.get('error_type')}")
    print("-" * 60)

print(f"Total JSON records: {len(files)}")
