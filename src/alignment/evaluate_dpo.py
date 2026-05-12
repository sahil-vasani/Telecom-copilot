import json
import random
import numpy as np


def compute_win_rate(results):

    wins = 0
    total = len(results)

    for r in results:

        if r["winner"] == "dpo":
            wins += 1

    return round(wins / max(total, 1), 4)


def compute_reward_margin(results):

    margins = []

    for r in results:

        margins.append(
            r["chosen_score"] - r["rejected_score"]
        )

    return round(np.mean(margins), 4)


def evaluate():

    path = "data/processed/dpo_eval_results.json"

    with open(path, "r") as f:
        results = json.load(f)

    win_rate = compute_win_rate(results)

    reward_margin = compute_reward_margin(results)

    print("\n" + "="*50)
    print("DPO EVALUATION")
    print("="*50)

    print(f"Win Rate        : {win_rate:.4f}")
    print(f"Reward Margin   : {reward_margin:.4f}")

    print("="*50)


if __name__ == "__main__":
    evaluate()