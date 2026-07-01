"""Deterministic sample PACE plans and outage scenarios with expected results."""

from __future__ import annotations

from .model import Pathway


def sample_plan() -> list:
    """A valid, domain-diverse, non-pLEO PACE package."""
    return [
        Pathway("P", "MEO-SATCOM terminal", "MEO-SATCOM", "meo-satcom", 2048, lpi=0.6),
        Pathway("A", "GEO TSAT", "GEO-SATCOM", "geo-satcom", 1024, lpi=0.5),
        Pathway("C", "HF-ALE", "HF-ALE", "hf", 9.6, lpi=0.7),
        Pathway("E", "PLB distress beacon", "PLB-SATCOM", "terrestrial", 0.05, lpi=0.8),
    ]


def invalid_single_domain() -> list:
    return [
        Pathway("P", "GEO-1", "GEO-SATCOM", "geo-satcom", 2048),
        Pathway("A", "GEO-2", "GEO-SATCOM", "geo-satcom", 1024),
        Pathway("C", "GEO-3", "GEO-SATCOM", "geo-satcom", 128),
        Pathway("E", "GEO-4", "GEO-SATCOM", "geo-satcom", 4.8),
    ]


def invalid_pleo() -> list:
    plan = sample_plan()
    plan[0] = Pathway("P", "pLEO constellation", "pLEO", "pleo", 4096, is_pleo=True)
    return plan


def invalid_missing_tier() -> list:
    return sample_plan()[:3]  # no Emergency


def sample_outages():
    """Timeline degrading domains over time; with expected active tier per step
    for sample_plan()."""
    timeline = [
        set(),                                  # all up -> P
        {"meo-satcom"},                         # P down -> A
        {"meo-satcom", "geo-satcom"},           # P,A down -> C
        {"meo-satcom", "geo-satcom", "hf"},     # -> E
        {"meo-satcom"},                         # recover -> A
        set(),                                  # -> P
    ]
    expected = ["P", "A", "C", "E", "A", "P"]
    return timeline, expected
