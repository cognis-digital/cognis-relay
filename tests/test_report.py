"""Tests for the report renderers (text / json / markdown)."""

import json

from hoplink import synth
from hoplink.analysis import analyze_failover, resilience_report
from hoplink.pace import validate
from hoplink.report import render_json, render_markdown, render_text


def _full_product():
    plan = synth.sample_plan()
    timeline, _ = synth.sample_outages()
    return {
        "validation": validate(plan),
        "pathways": [p.to_dict() for p in plan],
        "resilience": resilience_report(plan),
        "failover": analyze_failover(plan, timeline),
    }


def test_render_json_is_valid_json():
    product = _full_product()
    out = render_json(product)
    parsed = json.loads(out)
    assert parsed["validation"]["valid"] is True
    assert parsed["failover"]["sequence"] == ["P", "A", "C", "E", "A", "P"]


def test_render_text_contains_core_fields():
    product = _full_product()
    txt = render_text(product)
    assert "BLOS PACE" in txt
    assert "PACE valid: True" in txt
    assert "Failover:" in txt
    assert "P -> A -> C -> E -> A -> P" in txt
    # Resilience block rendered when present.
    assert "Structural resilience: hardened" in txt
    assert "MTTR:" in txt


def test_render_text_shows_violations():
    plan = synth.invalid_pleo()
    product = {"validation": validate(plan), "pathways": [p.to_dict() for p in plan]}
    txt = render_text(product)
    assert "Violations:" in txt
    assert "pLEO" in txt


def test_render_text_backward_compatible_minimal_product():
    # A product without resilience/failover must still render (old shape).
    plan = synth.sample_plan()
    product = {"validation": validate(plan), "pathways": [p.to_dict() for p in plan]}
    txt = render_text(product)
    assert "PACE valid: True" in txt
    assert "Structural resilience" not in txt
    assert "Failover:" not in txt


def test_render_markdown_structure():
    product = _full_product()
    md = render_markdown(product)
    assert md.startswith("# BLOS PACE Communications Assessment")
    assert "## Pathways" in md
    assert "| Tier | Name |" in md
    assert "## Structural resilience" in md
    assert "## Failover simulation" in md
    assert "→" in md  # arrow-joined sequence


def test_render_markdown_violations_section():
    plan = synth.invalid_single_domain()
    product = {"validation": validate(plan), "pathways": [p.to_dict() for p in plan]}
    md = render_markdown(product)
    assert "## Violations" in md
    assert "domain diversity" in md or "single domain" in md


def test_render_markdown_blackout_reported():
    plan = synth.sample_plan()
    alldown = {"meo-satcom", "geo-satcom", "hf", "terrestrial"}
    product = {
        "validation": validate(plan),
        "pathways": [p.to_dict() for p in plan],
        "failover": analyze_failover(plan, [set(), alldown, set()]),
    }
    md = render_markdown(product)
    assert "Blackout steps" in md
    assert "Longest blackout" in md
