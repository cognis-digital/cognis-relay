# Usage

Task-oriented walkthrough of the `hoplink` CLI and library. All commands run
offline. Invoke either as `hoplink <cmd>` (after `pip install -e .`) or
`python -m hoplink <cmd>` from a checkout.

## 1. Kick the tires

```bash
python -m hoplink demo
```

Validates and simulates the built-in sample plan and prints a resilience block
and a failover trace. Add `--format markdown` or `--format json` to change
output.

## 2. Validate your own plan

Author a plan JSON (see `examples/sample_plan.json` for the schema):

```bash
python -m hoplink validate --plan my_pace.json
python -m hoplink validate --plan my_pace.json --json          # machine output
python -m hoplink validate --plan my_pace.json --resilience    # + SPOF block
```

Exit code is `0` regardless of validity — read `validation.valid` in JSON to
gate automation. Malformed plans raise a clear `ValueError` (e.g. *"pathway #2
is invalid: … unexpected keyword argument"*).

Example JSON output (trimmed):

```json
{
  "validation": {
    "valid": true,
    "violations": [],
    "tiers_present": ["A", "C", "E", "P"],
    "domains": ["geo-satcom", "hf", "meo-satcom", "terrestrial"],
    "resilience_score": 1.0
  }
}
```

## 3. Analyze structural resilience (SPOF)

```bash
python -m hoplink analyze --plan examples/sample_plan.json
```

For each physical domain, Hoplink denies that entire domain and reports the
highest surviving tier:

```
Structural resilience: hardened   single-domain fault tolerant: True
   lose geo-satcom     -> top surviving tier P
   lose hf             -> top surviving tier P
   lose meo-satcom     -> top surviving tier A
   lose terrestrial    -> top surviving tier P
```

Grades: `hardened` (fault tolerant, ≥3 domains), `resilient` (fault tolerant),
`diverse-but-fragile` (≥2 domains but a single domain loss can black out), and
`fragile`.

## 4. Simulate failover over an outage timeline

Author an outage timeline (see `examples/outages.json`) — a list of steps, each
a list of degraded modality/domain strings:

```bash
python -m hoplink simulate --plan examples/sample_plan.json \
    --outages examples/outages.json --format markdown
```

The Markdown report includes the tier sequence, availability, transition count,
blackout steps, longest blackout and mean time to recover (MTTR).

## 5. First-order link budget + ATAK interop

```bash
python -m hoplink linkbudget --dist 2000 --freq 1500
```

Prints per-tier free-space margin (CLOSES/FAILS) and which tiers carry enough
throughput for ATAK/WINTAK CoT position (PLI) messaging. First-order only — see
[LIMITATIONS.md](LIMITATIONS.md).

## Library recipes

```python
from hoplink.model import load_pathways, load_outages
from hoplink.pace import validate
from hoplink.failover import simulate
from hoplink.analysis import (
    single_domain_outages, sequence_metrics, analyze_failover, resilience_report,
)

plan = load_pathways("examples/sample_plan.json")

# Validate
v = validate(plan)
assert v["valid"] and v["resilience_score"] == 1.0

# Structural resilience
r = resilience_report(plan)
assert r["grade"] == "hardened"

# Failover with enriched metrics
timeline = load_outages("examples/outages.json")
run = analyze_failover(plan, timeline)
print(run["sequence"])            # ['P', 'A', 'C', 'E', 'A', 'P']
print(run["metrics"]["mttr_steps"], run["metrics"]["longest_blackout"])

# Metrics straight from a raw sequence
sequence_metrics(["P", None, None, "A"])["longest_blackout"]   # -> 2
```

## Output formats

Every reporting command accepts `--format {text,json,markdown}`. The legacy
`--json` flag is still honored and is equivalent to `--format json`.

- **text** — operator-readable console summary.
- **json** — stable machine contract (see docs/ARCHITECTURE.md).
- **markdown** — paste-ready report for issues, PRs, or run books.
