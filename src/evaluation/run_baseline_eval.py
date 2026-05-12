import json
from pathlib import Path

# from src.baseline.baseline_system import BaselineRAG
from src.baseline.baseline_system import BaselineSystem

TEST_PATH = "data/processed/test_cases.jsonl"
OUTPUT_PATH = "data/processed/baseline_results.jsonl"


def main():

    print("\nLoading Baseline System...")
    system = BaselineSystem()

    print("Loading test cases...")

    with open(TEST_PATH, "r", encoding="utf-8") as f:
        test_cases = [json.loads(line) for line in f]

    results = []

    for i, case in enumerate(test_cases):

        print(f"\n[{i+1}/{len(test_cases)}] {case['query']}")

        # result = system.answer(case["query"])
        result = system.run(case["query"])

        result_record = {
            **case,
            "answer": result.get("answer", ""),
            "citations": result.get("citations", []),
            "latency_ms": result.get("latency_ms", 0),
            "tool_trace": [],
            "escalated": False,
        }

        results.append(result_record)

    Path(OUTPUT_PATH).parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")

    print(f"\nSaved results → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()