# Architecture

Hoplink is a small, layered, pure-stdlib Python package. Every layer has a
single responsibility and a stable data contract, so pieces compose cleanly and
are independently testable.

```
model  ─►  pace ─┐
        ─► failover ─┐
        ─► analysis ─┼─►  report  ─►  cli
        ─► linkbudget┘
```

## Layers

### `hoplink.model` — data & I/O
- `Pathway` dataclass: one PACE leg (`tier`, `name`, `modality`, `domain`,
  `bandwidth_kbps`, `lpi`, `is_pleo`, `man_portable`, `meta`).
- `load_pathways(path)` — parse a plan JSON (list of pathway objects) into
  `list[Pathway]`, with friendly `ValueError`s for malformed input.
- `load_outages(path)` — parse an outage timeline JSON (list of steps, each a
  list of degraded modality/domain strings) into `list[set[str]]`.
- `TIERS`, `TIER_NAME` — canonical PACE tier constants.

**Contract:** the rest of the package consumes `list[Pathway]` and never reads
files itself.

### `hoplink.pace` — validation & scoring
- `validate(pathways) -> dict` with keys `valid`, `violations`,
  `tiers_present`, `domains`, `resilience_score`.
- Hard rules: all four tiers present; ≥2 physical domains; no `is_pleo` pathway.
- `resilience_score` (0..1) rewards tier completeness, domain diversity and
  average LPI posture, and penalizes each violation.

### `hoplink.failover` — discrete-event failover
- `simulate(pathways, outages) -> dict` with `sequence`, `availability`,
  `transitions`, `blackout_steps`.
- At each step, choose the highest-priority tier (`ORDER = P<A<C<E`) whose
  `modality` and `domain` are both absent from that step's down-set.

### `hoplink.analysis` — resilience analytics (additive layer)
Composes `pace` + `failover` into higher-order products:
- `single_domain_outages(pathways)` — deny each physical domain in turn; report
  surviving tiers and whether the plan is *single-domain fault tolerant*.
- `sequence_metrics(sequence)` — MTTR, longest blackout, blackout-interval
  count, degradation/recovery transitions, per-tier occupancy.
- `analyze_failover(pathways, outages)` — `simulate` output verbatim plus a
  `metrics` sub-dict (never mutates the base keys).
- `resilience_report(pathways)` — domain depth + SPOF + a plan `grade`
  (`hardened` / `resilient` / `diverse-but-fragile` / `fragile`).

### `hoplink.linkbudget` — first-order RF sanity check
- `fspl_db`, `link_margin`, `assess_pathway`, `atak_summary` — free-space path
  loss, received-power margin, and an ATAK/WINTAK CoT PLI throughput gate.
  Documented as first-order (see `docs/LIMITATIONS.md`).

### `hoplink.report` — rendering
- `render_json`, `render_text`, `render_markdown` all accept the same *product*
  dict (`validation` + `pathways`, optionally `resilience` and `failover`) and
  render defensively — missing sections are simply omitted, so old and new
  product shapes both render.

### `hoplink.cli` — command surface
- Subcommands: `demo`, `validate`, `simulate`, `analyze`, `linkbudget`.
- `_product()` assembles the product dict; `_emit()` dispatches on format;
  `_resolve_format()` maps the legacy `--json` flag onto `--format json`.

## Product dict contract

```jsonc
{
  "validation": { "valid": true, "violations": [], "tiers_present": [...],
                  "domains": [...], "resilience_score": 1.0 },
  "pathways":   [ { "tier": "P", ... }, ... ],
  "resilience": { "grade": "hardened", "domain_count": 4, "spof": {...} },   // optional
  "failover":   { "sequence": [...], "availability": 1.0, "transitions": 3,
                  "blackout_steps": [], "metrics": {...} }                    // optional
}
```

## Verification harness (`bench/`)
`bench/evaluate.py` scores rule-verdict accuracy on labeled configs and failover
correctness against a planted expected sequence; `bench/run_all.py` writes
`bench/results.json` and `RESULTS.md`. Gated in CI.

## Design principles
- **Additive:** new capability is layered on top; existing signatures/outputs
  are preserved.
- **Zero runtime dependencies:** stdlib only, offline-first.
- **Deterministic:** same inputs → same outputs (asserted in the bench).
