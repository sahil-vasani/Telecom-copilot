def reward_margin(chosen_logps, rejected_logps):
    
    margins = [
        c - r
        for c, r in zip(chosen_logps, rejected_logps)
    ]

    return sum(margins) / len(margins)