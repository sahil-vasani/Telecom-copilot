import json
from datasets import Dataset


def load_dpo_dataset(path="data/processed/dpo_pairs.jsonl"):

    rows = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))

    formatted = []

    for r in rows:

        formatted.append({
            "prompt": r["prompt"],
            "chosen": r["chosen"],
            "rejected": r["rejected"]
        })

    return Dataset.from_list(formatted)