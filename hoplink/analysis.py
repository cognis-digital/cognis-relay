"""Resilience analytics for PACE plans and failover runs.

This module is purely additive: it composes the existing :mod:`hoplink.pace`
and :mod:`hoplink.failover` primitives into higher-order resilience products
without changing their behavior.

Two families of analysis are provided:

* **Single-point-of-failure (SPOF) analysis** — for each physical domain in a
  plan, simulate a total outage of that domain and report which PACE tiers
  survive. A plan is *single-domain fault tolerant* when every one-domain
  outage still leaves at least one usable pathway.
* **Sequence metrics** — turn a raw failover ``sequence`` (as produced by
  :func:`hoplink.failover.simulate`) into operational figures of merit: mean
  time to recover, longest blackout, degradation/recovery event counts, and
  per-tier occupancy.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence

from .failover import ORDER, simulate
from .model import TIER_NAME, TIERS


def single_domain_outages(pathways: list) -> dict:
    """Assess tolerance to the loss of any single physical domain.

    For every distinct ``domain`` present in ``pathways`` the function drops
    that entire domain (as a one-step outage) and records which tiers remain
    usable and which is the highest-priority survivor.

    Returns a dict with:

    * ``per_domain`` — list of ``{domain, top_surviving_tier, surviving_tiers,
      survives}`` records, one per domain, sorted by domain name.
    * ``single_domain_fault_tolerant`` — ``True`` when no single-domain outage
      causes a blackout.
    * ``weakest_domains`` — domains whose loss leaves the fewest survivors.
    """
    domains = sorted({p.domain for p in pathways})
    ordered = sorted(pathways, key=lambda p: ORDER.get(p.tier, 9))
    per_domain: List[dict] = []
    for d in domains:
        down = {d}
        survivors = [p.tier for p in ordered
                     if p.domain not in down and p.modality not in down]
        top = simulate(pathways, [down])["sequence"][0]
        per_domain.append({
            "domain": d,
            "top_surviving_tier": top,
            "surviving_tiers": sorted(set(survivors), key=lambda t: ORDER.get(t, 9)),
            "survives": top is not None,
        })

    fault_tolerant = all(r["survives"] for r in per_domain) and bool(per_domain)
    min_survivors = min((len(r["surviving_tiers"]) for r in per_domain), default=0)
    weakest = [r["domain"] for r in per_domain
               if len(r["surviving_tiers"]) == min_survivors]
    return {
        "per_domain": per_domain,
        "single_domain_fault_tolerant": fault_tolerant,
        "weakest_domains": weakest,
        "domains_tested": domains,
    }


def sequence_metrics(sequence: Sequence[Optional[str]]) -> dict:
    """Derive operational figures of merit from a failover ``sequence``.

    ``sequence`` is a list whose entries are tier letters (``"P"``/``"A"``/…)
    or ``None`` for a blackout step, exactly as returned by
    :func:`hoplink.failover.simulate`.

    Returns:

    * ``steps`` — total number of steps.
    * ``availability`` — fraction of steps with any active tier.
    * ``longest_blackout`` — length of the longest run of consecutive blackouts.
    * ``blackout_intervals`` — number of distinct blackout runs.
    * ``mttr_steps`` — mean length of blackout runs that recover (return to a
      usable tier). ``None`` if there is no recovered blackout.
    * ``degradations`` — transitions to a lower-priority tier or into blackout.
    * ``recoveries`` — transitions to a higher-priority tier (blackout counts as
      the lowest priority).
    * ``tier_occupancy`` — fraction of steps spent on each PACE tier.
    """
    seq = list(sequence)
    n = len(seq)
    if n == 0:
        return {
            "steps": 0, "availability": 0.0, "longest_blackout": 0,
            "blackout_intervals": 0, "mttr_steps": None,
            "degradations": 0, "recoveries": 0,
            "tier_occupancy": {t: 0.0 for t in TIERS},
        }

    covered = sum(1 for s in seq if s is not None)

    # Blackout run analysis.
    runs: List[Dict[str, object]] = []
    i = 0
    while i < n:
        if seq[i] is None:
            j = i
            while j < n and seq[j] is None:
                j += 1
            runs.append({"length": j - i, "recovered": j < n})
            i = j
        else:
            i += 1
    recovered_runs = [r["length"] for r in runs if r["recovered"]]
    mttr = round(sum(recovered_runs) / len(recovered_runs), 4) if recovered_runs else None
    longest_blackout = max((int(r["length"]) for r in runs), default=0)

    # Priority for transition classification: lower rank = better; blackout worst.
    def rank(s: Optional[str]) -> int:
        return ORDER.get(s, 99) if s is not None else 999

    degradations = recoveries = 0
    for a, b in zip(seq, seq[1:]):
        if rank(b) > rank(a):
            degradations += 1
        elif rank(b) < rank(a):
            recoveries += 1

    occupancy = {t: round(sum(1 for s in seq if s == t) / n, 4) for t in TIERS}

    return {
        "steps": n,
        "availability": round(covered / n, 4),
        "longest_blackout": longest_blackout,
        "blackout_intervals": len(runs),
        "mttr_steps": mttr,
        "degradations": degradations,
        "recoveries": recoveries,
        "tier_occupancy": occupancy,
    }


def analyze_failover(pathways: list, outages: list) -> dict:
    """Run a failover simulation and enrich it with :func:`sequence_metrics`.

    The base :func:`hoplink.failover.simulate` result is preserved verbatim
    under all its original keys; a ``metrics`` sub-dict is added.
    """
    base = simulate(pathways, outages)
    base = dict(base)
    base["metrics"] = sequence_metrics(base["sequence"])
    return base


def resilience_report(pathways: list) -> dict:
    """One-call structural resilience product for a plan (no outage timeline).

    Combines domain-diversity depth with single-domain fault tolerance and a
    human-readable grade.
    """
    domains = sorted({p.domain for p in pathways})
    spof = single_domain_outages(pathways)
    n_domains = len(domains)
    if spof["single_domain_fault_tolerant"] and n_domains >= 3:
        grade = "hardened"
    elif spof["single_domain_fault_tolerant"]:
        grade = "resilient"
    elif n_domains >= 2:
        grade = "diverse-but-fragile"
    else:
        grade = "fragile"
    return {
        "domains": domains,
        "domain_count": n_domains,
        "tiers": sorted({p.tier for p in pathways}, key=lambda t: ORDER.get(t, 9)),
        "tier_names": [TIER_NAME.get(p.tier, p.tier)
                       for p in sorted(pathways, key=lambda p: ORDER.get(p.tier, 9))],
        "spof": spof,
        "grade": grade,
    }
