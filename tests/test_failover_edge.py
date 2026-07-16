"""Edge-case tests for the failover simulator."""

from hoplink import synth
from hoplink.failover import simulate
from hoplink.model import Pathway


def test_empty_outages_timeline():
    r = simulate(synth.sample_plan(), [])
    assert r["sequence"] == []
    assert r["availability"] == 0.0
    assert r["transitions"] == 0
    assert r["blackout_steps"] == []


def test_all_up_selects_primary():
    r = simulate(synth.sample_plan(), [set()])
    assert r["sequence"] == ["P"]
    assert r["availability"] == 1.0


def test_priority_order_respected_when_multiple_available():
    # With nothing down, the highest-priority (P) is always chosen even though
    # lower tiers are also available.
    r = simulate(synth.sample_plan(), [set(), set(), set()])
    assert r["sequence"] == ["P", "P", "P"]
    assert r["transitions"] == 0


def test_full_blackout_when_all_domains_down():
    alldown = {"meo-satcom", "geo-satcom", "hf", "terrestrial"}
    r = simulate(synth.sample_plan(), [alldown])
    assert r["sequence"] == [None]
    assert r["availability"] == 0.0
    assert r["blackout_steps"] == [0]


def test_modality_outage_also_triggers_failover():
    # Downing by modality string (not domain) must also disable a pathway.
    plan = synth.sample_plan()
    r = simulate(plan, [{"MEO-SATCOM"}])  # P's modality
    assert r["sequence"] == ["A"]


def test_transitions_counted_across_recovery():
    plan = synth.sample_plan()
    timeline = [set(), {"meo-satcom"}, set()]  # P -> A -> P
    r = simulate(plan, timeline)
    assert r["sequence"] == ["P", "A", "P"]
    assert r["transitions"] == 2


def test_unknown_tier_sorts_last():
    # A pathway with a non-PACE tier must not be preferred over real tiers.
    plan = [
        Pathway("Z", "weird", "MODZ", "domz", 100.0),
        Pathway("P", "primary", "MODP", "domp", 100.0),
    ]
    r = simulate(plan, [set()])
    assert r["sequence"] == ["P"]
