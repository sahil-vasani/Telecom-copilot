import json
from pathlib import Path

from src.pipeline.inference_pipeline import TelecomCopilot


TEST_PATH = "data/processed/test_cases.jsonl"
OUTPUT_PATH = "data/processed/full_system_results.jsonl"


def main():

    print("\nLoading Telecom Copilot...")
    system = TelecomCopilot()

    print("Loading test cases...")

    with open(TEST_PATH, "r", encoding="utf-8") as f:
        test_cases = [json.loads(line) for line in f][:20]

    results = []

    for i, case in enumerate(test_cases):

        print(f"\n[{i+1}/{len(test_cases)}] {case['query']}")

        result = system.run(
            query=case["query"],
            history=case.get("history", [])
        )

        result_record = {
            **case,

            # Main generated answer
            "answer": result.get(
                "answer",
                result.get("response", "")
            ),

            # Citations
            "citations": result.get("citations", []),

            # Tool trace
            "tool_trace": result.get("tool_trace", []),

            # Escalation
            "escalated": result.get("escalated", False),

            # Latency
            "latency_ms": result.get("latency_ms", 0),

            # Preserve original fields
            "query": case["query"],
            "gold_answer": case.get("gold_answer", ""),
            "gold_doc_id": case.get("gold_doc_id"),
            "domain": case.get("domain"),
            "requires_outage_check": case.get("requires_outage_check", False),
            "should_escalate": case.get("should_escalate"),
        }

        results.append(result_record)

    Path(OUTPUT_PATH).parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")

    print(f"\nSaved results → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()