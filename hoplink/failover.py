"""Automated PACE failover simulation.

Given an ordered PACE plan and a timeline of outages (down modalities/domains
per step), determine which pathway is active at each step: the highest-priority
tier (P>A>C>E) whose modality and domain are not degraded.
"""

from __future__ import annotations

from typing import Iterable, List, Optional

#: PACE priority order — lower is higher priority.
ORDER = {"P": 0, "A": 1, "C": 2, "E": 3}


def simulate(pathways: list, outages: Iterable) -> dict:
    ordered = sorted(pathways, key=lambda p: ORDER.get(p.tier, 9))
    sequence: List[Optional[str]] = []
    for down in outages:
        down = set(down)
        active = None
        for p in ordered:
            if p.modality not in down and p.domain not in down:
                active = p
                break
        sequence.append(active.tier if active else None)
    covered = sum(1 for s in sequence if s is not None)
    transitions = sum(1 for i in range(1, len(sequence)) if sequence[i] != sequence[i - 1])
    return {
        "sequence": sequence,
        "availability": round(covered / len(sequence), 4) if sequence else 0.0,
        "transitions": transitions,
        "blackout_steps": [i for i, s in enumerate(sequence) if s is None],
    }
