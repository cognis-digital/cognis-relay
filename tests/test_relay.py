from bench import evaluate
from cognis_relay import synth
from cognis_relay.failover import simulate
from cognis_relay.pace import validate


def test_valid_plan_passes():
    v = validate(synth.sample_plan())
    assert v["valid"] is True
    assert v["resilience_score"] > 0.7


def test_single_domain_fails():
    v = validate(synth.invalid_single_domain())
    assert v["valid"] is False
    assert any("domain" in x for x in v["violations"])


def test_pleo_disqualified():
    v = validate(synth.invalid_pleo())
    assert v["valid"] is False
    assert any("pLEO" in x for x in v["violations"])


def test_missing_tier_fails():
    v = validate(synth.invalid_missing_tier())
    assert v["valid"] is False
    assert any("missing E" in x for x in v["violations"])


def test_failover_sequence():
    plan = synth.sample_plan()
    timeline, expected = synth.sample_outages()
    assert simulate(plan, timeline)["sequence"] == expected


def test_bench_gates():
    r = evaluate.evaluate()
    assert r["rule_accuracy"] == 1.0
    assert r["failover_correct"] is True
    assert r["pleo_disqualified"] is True
    assert r["determinism"] is True
