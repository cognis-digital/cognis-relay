"""Accuracy evaluation: PACE rule verdicts and failover correctness."""

from __future__ import annotations

import json

from hoplink import synth
from hoplink.failover import simulate
from hoplink.pace import validate


def evaluate() -> dict:
    # PACE rule verdicts on labeled configs (expected valid?)
    cases = [
        ("valid", synth.sample_plan(), True),
        ("single_domain", synth.invalid_single_domain(), False),
        ("pleo", synth.invalid_pleo(), False),
        ("missing_tier", synth.invalid_missing_tier(), False),
    ]
    correct = 0
    detail = {}
    for name, plan, expected in cases:
        got = validate(plan)["valid"]
        detail[name] = {"expected": expected, "got": got}
        if got == expected:
            correct += 1
    rule_accuracy = round(correct / len(cases), 4)

    # failover correctness vs planted expected active-tier sequence
    plan = synth.sample_plan()
    timeline, expected_seq = synth.sample_outages()
    seq = simulate(plan, timeline)["sequence"]
    failover_correct = (seq == expected_seq)

    # pLEO must always be flagged
    pleo_flagged = not validate(synth.invalid_pleo())["valid"]

    # determinism
    determinism = simulate(plan, timeline)["sequence"] == seq

    return {
        "rule_accuracy": rule_accuracy,
        "rule_detail": detail,
        "failover_correct": failover_correct,
        "failover_sequence": seq,
        "pleo_disqualified": pleo_flagged,
        "determinism": determinism,
    }


def main():
    print(json.dumps(evaluate(), indent=2))


if __name__ == "__main__":
    main()
