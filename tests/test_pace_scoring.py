"""Focused tests for PACE validation edge cases and resilience scoring."""

from hoplink import synth
from hoplink.model import Pathway
from hoplink.pace import validate


def test_empty_plan_all_tiers_missing():
    v = validate([])
    assert v["valid"] is False
    # Every required tier reported missing; no phantom domain-diversity violation.
    for t in ("P", "A", "C", "E"):
        assert any(f"missing {t}" in x for x in v["violations"])
    assert v["resilience_score"] == 0.0


def test_valid_sample_scores_high():
    v = validate(synth.sample_plan())
    assert v["valid"] is True
    assert v["resilience_score"] >= 0.9
    assert v["tiers_present"] == ["A", "C", "E", "P"]
    assert v["domains"] == ["geo-satcom", "hf", "meo-satcom", "terrestrial"]


def test_single_domain_violation_lowers_score():
    good = validate(synth.sample_plan())["resilience_score"]
    bad = validate(synth.invalid_single_domain())
    assert bad["valid"] is False
    assert bad["resilience_score"] < good
    assert any("single domain" in x for x in bad["violations"])


def test_pleo_violation_message():
    v = validate(synth.invalid_pleo())
    assert v["valid"] is False
    assert any("disqualified" in x for x in v["violations"])


def test_missing_tier_only_reports_absent_tier():
    v = validate(synth.invalid_missing_tier())  # drops Emergency
    assert v["valid"] is False
    assert any("missing E" in x for x in v["violations"])
    assert not any("missing P" in x for x in v["violations"])


def test_score_is_bounded_between_zero_and_one():
    # Many violations should not drive the score negative.
    plan = [Pathway("P", "only", "GEO", "geo-satcom", 1.0, lpi=0.0)]
    v = validate(plan)
    assert 0.0 <= v["resilience_score"] <= 1.0


def test_higher_lpi_scores_at_least_as_high():
    base = [Pathway(t, t, "M" + t, d, 100.0, lpi=0.2)
            for t, d in zip("PACE", ["a", "b", "c", "d"])]
    hi = [Pathway(t, t, "M" + t, d, 100.0, lpi=0.9)
          for t, d in zip("PACE", ["a", "b", "c", "d"])]
    assert validate(hi)["resilience_score"] >= validate(base)["resilience_score"]
