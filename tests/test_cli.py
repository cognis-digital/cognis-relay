"""End-to-end CLI tests driving hoplink.cli.main via argv."""

import json

import pytest

from hoplink import synth
from hoplink.cli import build_parser, main


def _write_plan(tmp_path):
    keys = ["tier", "name", "modality", "domain", "bandwidth_kbps",
            "lpi", "is_pleo", "man_portable"]
    plan = [{k: p.to_dict()[k] for k in keys} for p in synth.sample_plan()]
    f = tmp_path / "plan.json"
    f.write_text(json.dumps(plan), encoding="utf-8")
    return str(f)


def _write_outages(tmp_path):
    timeline, _ = synth.sample_outages()
    f = tmp_path / "outages.json"
    f.write_text(json.dumps([sorted(s) for s in timeline]), encoding="utf-8")
    return str(f)


def test_parser_requires_subcommand():
    with pytest.raises(SystemExit):
        build_parser().parse_args([])


def test_demo_text(capsys):
    rc = main(["demo"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "BLOS PACE" in out
    assert "Failover:" in out


def test_demo_markdown(capsys):
    rc = main(["demo", "--format", "markdown"])
    out = capsys.readouterr().out
    assert rc == 0
    assert out.startswith("# BLOS PACE Communications Assessment")


def test_validate_text(tmp_path, capsys):
    rc = main(["validate", "--plan", _write_plan(tmp_path)])
    out = capsys.readouterr().out
    assert rc == 0
    assert "PACE valid: True" in out


def test_validate_legacy_json_flag(tmp_path, capsys):
    rc = main(["validate", "--plan", _write_plan(tmp_path), "--json"])
    out = capsys.readouterr().out
    assert rc == 0
    parsed = json.loads(out)  # legacy --json still yields JSON
    assert parsed["validation"]["valid"] is True


def test_validate_format_json_equivalent(tmp_path, capsys):
    rc = main(["validate", "--plan", _write_plan(tmp_path), "--format", "json"])
    out = capsys.readouterr().out
    assert rc == 0
    assert json.loads(out)["validation"]["valid"] is True


def test_validate_with_resilience(tmp_path, capsys):
    rc = main(["validate", "--plan", _write_plan(tmp_path),
               "--resilience", "--format", "json"])
    out = capsys.readouterr().out
    parsed = json.loads(out)
    assert rc == 0
    assert parsed["resilience"]["grade"] == "hardened"


def test_simulate_json(tmp_path, capsys):
    rc = main(["simulate", "--plan", _write_plan(tmp_path),
               "--outages", _write_outages(tmp_path), "--format", "json"])
    out = capsys.readouterr().out
    parsed = json.loads(out)
    assert rc == 0
    assert parsed["failover"]["sequence"] == ["P", "A", "C", "E", "A", "P"]
    assert "metrics" in parsed["failover"]


def test_analyze_json(tmp_path, capsys):
    rc = main(["analyze", "--plan", _write_plan(tmp_path), "--format", "json"])
    out = capsys.readouterr().out
    parsed = json.loads(out)
    assert rc == 0
    assert parsed["resilience"]["spof"]["single_domain_fault_tolerant"] is True


def test_linkbudget_runs(capsys):
    rc = main(["linkbudget", "--dist", "1500", "--freq", "1200"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "link-budget @ 1500" in out
    assert "ATAK/WINTAK PLI capable tiers" in out


def test_bundled_example_files_are_valid(tmp_path, capsys):
    # The committed examples/ files must work with the real commands.
    import os
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    plan = os.path.join(root, "examples", "sample_plan.json")
    outs = os.path.join(root, "examples", "outages.json")
    rc = main(["simulate", "--plan", plan, "--outages", outs, "--format", "json"])
    out = capsys.readouterr().out
    assert rc == 0
    assert json.loads(out)["failover"]["sequence"] == ["P", "A", "C", "E", "A", "P"]
