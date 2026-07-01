"""PACE plan validation and resilience scoring.

Hard constraints from the challenge:
- Four distinct pathways (P, A, C, E present).
- Modality diversity across physical domains (cannot be 100% one domain).
- pLEO solutions are disqualified.
LPI/LPD posture and man-portability are scored.
"""

from __future__ import annotations

from .model import TIERS


def validate(pathways: list) -> dict:
    violations = []
    tiers = {p.tier for p in pathways}
    for t in TIERS:
        if t not in tiers:
            violations.append(f"missing {t} pathway")
    domains = {p.domain for p in pathways}
    if len(pathways) and len(domains) < 2:
        violations.append("no physical-domain diversity (100% single domain)")
    if any(p.is_pleo for p in pathways):
        violations.append("pLEO pathway present — disqualified")

    return {
        "valid": len(violations) == 0,
        "violations": violations,
        "tiers_present": sorted(tiers),
        "domains": sorted(domains),
        "resilience_score": _score(pathways, violations),
    }


def _score(pathways: list, violations: list) -> float:
    if not pathways:
        return 0.0
    s = 0.25 * len({p.tier for p in pathways})          # up to 1.0 for full PACE
    s += 0.1 * min(3, len({p.domain for p in pathways}))  # domain diversity bonus
    s += 0.2 * (sum(p.lpi for p in pathways) / len(pathways))  # LPI posture
    s -= 0.5 * len(violations)                           # penalties
    return round(max(0.0, min(1.0, s)), 4)
