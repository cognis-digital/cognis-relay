<h1 align="center">🟣 Hoplink</h1>
<p align="center"><b>BLOS PACE communications validator &amp; failover simulator</b><br>
<i>Validate Primary/Alternate/Contingency/Emergency plans, analyze single-point-of-failure resilience, and simulate automated failover — self-hosted, offline, zero-dependency.</i></p>

<p align="center">
<img alt="license" src="https://img.shields.io/badge/license-COCL--1.0-6D28D9">
<img alt="python" src="https://img.shields.io/badge/python-3.9%2B-6D28D9">
<img alt="deps" src="https://img.shields.io/badge/dependencies-none%20(stdlib)-6D28D9">
<img alt="status" src="https://img.shields.io/badge/status-v0.3.0-6D28D9">
</p>

---

> **Built for:** SOLIC Accelerator / ONIX OTA — **Challenge Area 7: Beyond-Line-of-Sight PACE Communications Architecture Without pLEO.**
> Validate a four-pathway PACE plan for physical-domain diversity, LPI/LPD posture, and the hard constraints (four distinct pathways; not single-domain-reliant; **pLEO disqualified**), analyze how it holds up when any one domain is denied, then simulate automated failover through an outage timeline.

## Overview

Hoplink is a planning and assessment tool for **beyond-line-of-sight (BLOS)
PACE** communications architectures. Give it a plan — a set of pathways tagged
Primary / Alternate / Contingency / Emergency, each with a physical domain,
modality, throughput and LPI posture — and it answers three questions:

1. **Is the plan valid?** Four distinct tiers present, diversity across physical
   domains, and no proliferated-LEO dependence.
2. **How resilient is it structurally?** For every physical domain, what happens
   if that domain is denied? Is the plan *single-domain fault tolerant*?
3. **How does it behave under a real outage timeline?** Which tier is live at
   each step, how often does it transition, and does it ever black out?

It is pure-Python **stdlib only** — no network, no external packages — so it
runs fully offline in a disconnected planning environment.

## What it does

- ✅ **PACE validation** — enforces P/A/C/E presence, physical-domain diversity, no-pLEO; scores resilience (`pace`).
- 🧭 **Resilience / SPOF analysis** — per-domain single-point-of-failure test and a plan grade (`analysis`).
- 🔁 **Failover simulation** — highest-priority available tier per step across an outage timeline; availability, transitions, blackouts, MTTR, longest-blackout (`failover` + `analysis`).
- 📡 **RF link-budget + ATAK/WINTAK interop** — first-order free-space path-loss margin and CoT PLI throughput check (`linkbudget`).
- 📤 **Three output formats** — human `text`, machine `json`, and shareable `markdown`.
- 🔒 **Offline / zero-dependency** — pure Python stdlib.

## Architecture

```
                 ┌────────────┐
   plan.json ──► │  model     │  Pathway dataclass + JSON loaders
                 └─────┬──────┘
                       │ list[Pathway]
        ┌──────────────┼───────────────┬────────────────┐
        ▼              ▼               ▼                ▼
   ┌─────────┐   ┌───────────┐   ┌───────────┐   ┌─────────────┐
   │  pace   │   │ failover  │   │ analysis  │   │ linkbudget  │
   │ validate│   │ simulate  │   │ SPOF/MTTR │   │ FSPL/ATAK   │
   └────┬────┘   └─────┬─────┘   └─────┬─────┘   └──────┬──────┘
        └──────────────┴───────┬───────┴────────────────┘
                               ▼
                        ┌────────────┐        ┌──────┐
                        │  report    │ ─────► │ CLI  │  text / json / markdown
                        └────────────┘        └──────┘
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the module-by-module tour
and data contracts, and [docs/USAGE.md](docs/USAGE.md) for a task-oriented
walkthrough.

## Install

```bash
git clone https://github.com/cognis-digital/hoplink
cd hoplink
pip install -e .          # installs the `hoplink` console script (no runtime deps)
```

Or run straight from a checkout without installing:

```bash
python -m hoplink demo
```

Requires Python 3.9+.

## Quick start

```bash
# Validate + simulate the built-in sample plan (includes resilience analysis)
python -m hoplink demo

# Validate your own plan, with SPOF resilience analysis, as JSON
python -m hoplink validate --plan examples/sample_plan.json --resilience --json

# Structural single-point-of-failure analysis
python -m hoplink analyze --plan examples/sample_plan.json

# Simulate failover over an outage timeline, rendered as Markdown
python -m hoplink simulate --plan examples/sample_plan.json \
    --outages examples/outages.json --format markdown

# First-order RF link-budget + ATAK interop for the sample plan
python -m hoplink linkbudget --dist 2000 --freq 1500
```

Runnable sample inputs live in [`examples/`](examples/).

## Usage detail

### Plan format (`examples/sample_plan.json`)

A plan is a JSON list of pathway objects:

```json
[
  {"tier": "P", "name": "MEO-SATCOM terminal", "modality": "MEO-SATCOM",
   "domain": "meo-satcom", "bandwidth_kbps": 2048, "lpi": 0.6},
  {"tier": "A", "name": "GEO TSAT", "modality": "GEO-SATCOM",
   "domain": "geo-satcom", "bandwidth_kbps": 1024, "lpi": 0.5},
  {"tier": "C", "name": "HF-ALE", "modality": "HF-ALE",
   "domain": "hf", "bandwidth_kbps": 9.6, "lpi": 0.7},
  {"tier": "E", "name": "PLB distress beacon", "modality": "PLB-SATCOM",
   "domain": "terrestrial", "bandwidth_kbps": 0.05, "lpi": 0.8}
]
```

| Field | Required | Meaning |
|---|---|---|
| `tier` | ✅ | PACE tier: `P` / `A` / `C` / `E` |
| `name` | ✅ | Human-readable pathway name |
| `modality` | ✅ | Waveform/terminal, e.g. `HF-ALE` |
| `domain` | ✅ | Physical domain, e.g. `meo-satcom`, `hf`, `terrestrial` |
| `bandwidth_kbps` | ✅ | Sustained throughput (kbps) |
| `lpi` | — | LPI/LPD/LPE posture `0..1` (default `0.5`) |
| `is_pleo` | — | Proliferated-LEO dependence (default `false`) |
| `man_portable` | — | Terminal is man-portable (default `true`) |
| `meta` | — | Free-form SWaP-C / operator metadata |

### Outage timeline format (`examples/outages.json`)

A list of steps; each step lists the modality **or** domain strings that are
degraded at that step (empty = all links up):

```json
[[], ["meo-satcom"], ["meo-satcom", "geo-satcom"],
 ["meo-satcom", "geo-satcom", "hf"], ["meo-satcom"], []]
```

At each step the simulator picks the highest-priority tier (P > A > C > E) whose
modality and domain are both up.

### Programmatic API

```python
from hoplink.model import load_pathways
from hoplink.pace import validate
from hoplink.analysis import resilience_report, analyze_failover

plan = load_pathways("examples/sample_plan.json")

validate(plan)["resilience_score"]              # -> 1.0
resilience_report(plan)["grade"]                # -> "hardened"
analyze_failover(plan, [set(), {"meo-satcom"}]) # -> sequence + metrics
```

## Configuration reference

| Command | Flag | Default | Purpose |
|---|---|---|---|
| all output cmds | `--format {text,json,markdown}` | `text` | output format |
| all output cmds | `--json` | off | legacy shorthand for `--format json` |
| `validate` | `--plan PATH` | — | plan JSON (required) |
| `validate` / `simulate` | `--resilience` | off | include SPOF resilience block |
| `simulate` | `--outages PATH` | — | outage-timeline JSON (required) |
| `analyze` | `--plan PATH` | — | plan JSON (required) |
| `linkbudget` | `--dist KM` | `2000.0` | link range (km) |
| `linkbudget` | `--freq MHZ` | `1500.0` | frequency (MHz) |

## Verification & proof

Gated in CI (`python bench/run_all.py` → [`RESULTS.md`](RESULTS.md)):

| Metric | Value |
|---|---|
| PACE rule-verdict accuracy | **1.00** (valid / single-domain / pLEO / missing-tier) |
| Failover sequence correct | ✓ (P→A→C→E→A→P) |
| pLEO disqualified | ✓ |
| Determinism | ✓ |

The test suite (`python -m pytest -q`) covers the model, validation, failover,
resilience analytics, report renderers, and every CLI subcommand.

## FAQ

**Does Hoplink transmit or configure radios?** No. It is a planning/assessment
tool that reasons about *plan structure and failover logic*. It never touches a
link. See [docs/LIMITATIONS.md](docs/LIMITATIONS.md).

**Is the link budget authoritative?** No — it is a first-order free-space model
for sanity-checking. Operational planning needs terrain, fading, and waveform
specifics.

**What does "single-domain fault tolerant" mean?** For every physical domain in
the plan, deny that entire domain and confirm at least one pathway still works.
A plan that survives every such test earns the `resilient`/`hardened` grade.

**Why no dependencies?** So it runs in an air-gapped planning cell with just a
Python interpreter.

## Roadmap

Near/mid/long-term direction is tracked in [ROADMAP.md](ROADMAP.md).

## License

Source-available under **COCL v1.0** (see [LICENSE](LICENSE)).

<p align="center"><sub>© 2026 Cognis Digital LLC · <a href="https://cognis.digital">cognis.digital</a></sub></p>
