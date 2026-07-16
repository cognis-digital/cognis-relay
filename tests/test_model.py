"""Tests for the pathway model and JSON loaders."""

import json

import pytest

from hoplink.model import (
    TIER_NAME,
    TIERS,
    Pathway,
    load_outages,
    load_pathways,
)


def test_pathway_defaults():
    p = Pathway("P", "x", "SAT", "geo-satcom", 100.0)
    assert p.lpi == 0.5
    assert p.is_pleo is False
    assert p.man_portable is True
    assert p.meta == {}


def test_pathway_to_dict_shape_and_tier_name():
    p = Pathway("E", "beacon", "PLB", "terrestrial", 0.05, lpi=0.9)
    d = p.to_dict()
    assert d["tier_name"] == "Emergency"
    assert d["tier_name"] == TIER_NAME["E"]
    assert set(d) == {
        "tier", "tier_name", "name", "modality", "domain",
        "bandwidth_kbps", "lpi", "is_pleo", "man_portable",
    }
    # meta is intentionally not serialized in the public dict view.
    assert "meta" not in d


def test_tiers_constant():
    assert TIERS == ["P", "A", "C", "E"]


def test_load_pathways_roundtrip(tmp_path):
    src = [
        {"tier": "P", "name": "meo", "modality": "MEO", "domain": "meo-satcom",
         "bandwidth_kbps": 2048},
        {"tier": "A", "name": "hf", "modality": "HF", "domain": "hf",
         "bandwidth_kbps": 9.6, "lpi": 0.7},
    ]
    f = tmp_path / "plan.json"
    f.write_text(json.dumps(src), encoding="utf-8")
    plan = load_pathways(str(f))
    assert len(plan) == 2
    assert isinstance(plan[0], Pathway)
    assert plan[1].lpi == 0.7


def test_load_pathways_rejects_non_list(tmp_path):
    f = tmp_path / "bad.json"
    f.write_text('{"tier": "P"}', encoding="utf-8")
    with pytest.raises(ValueError, match="list of pathway"):
        load_pathways(str(f))


def test_load_pathways_rejects_non_object_item(tmp_path):
    f = tmp_path / "bad.json"
    f.write_text("[1, 2, 3]", encoding="utf-8")
    with pytest.raises(ValueError, match="#0 must be a JSON object"):
        load_pathways(str(f))


def test_load_pathways_rejects_unknown_field(tmp_path):
    f = tmp_path / "bad.json"
    f.write_text(json.dumps([{"tier": "P", "name": "x", "modality": "m",
                              "domain": "d", "bandwidth_kbps": 1, "bogus": 5}]),
                 encoding="utf-8")
    with pytest.raises(ValueError, match="#0 is invalid"):
        load_pathways(str(f))


def test_load_pathways_rejects_missing_required(tmp_path):
    f = tmp_path / "bad.json"
    f.write_text(json.dumps([{"tier": "P"}]), encoding="utf-8")
    with pytest.raises(ValueError, match="#0 is invalid"):
        load_pathways(str(f))


def test_load_outages_parses_steps(tmp_path):
    f = tmp_path / "out.json"
    f.write_text(json.dumps([[], ["hf"], ["hf", "meo-satcom"]]), encoding="utf-8")
    timeline = load_outages(str(f))
    assert timeline == [set(), {"hf"}, {"hf", "meo-satcom"}]
    assert all(isinstance(s, set) for s in timeline)


def test_load_outages_rejects_non_list(tmp_path):
    f = tmp_path / "out.json"
    f.write_text('"nope"', encoding="utf-8")
    with pytest.raises(ValueError, match="list of steps"):
        load_outages(str(f))


def test_load_outages_rejects_non_list_step(tmp_path):
    f = tmp_path / "out.json"
    f.write_text(json.dumps([[], "hf"]), encoding="utf-8")
    with pytest.raises(ValueError, match="#1 must be a list"):
        load_outages(str(f))
