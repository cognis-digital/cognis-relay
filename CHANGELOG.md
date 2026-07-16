# Changelog

Adheres to [Semantic Versioning](https://semver.org/).

## [0.3.0] — 2026-07-16

### Added
- **Resilience analytics** (`analysis.py`): single-point-of-failure analysis
  (`single_domain_outages`), failover figures of merit (`sequence_metrics` —
  MTTR, longest blackout, degradation/recovery counts, tier occupancy),
  `analyze_failover` (simulate output + enriched metrics), and a one-call
  structural `resilience_report` with a plan grade.
- **New CLI subcommands**: `simulate` (failover over an outage-timeline JSON) and
  `analyze` (structural SPOF resilience).
- **Output formats**: `--format {text,json,markdown}` on all reporting commands,
  including a new Markdown report renderer (`report.render_markdown`). The legacy
  `--json` flag remains and maps to `--format json`.
- **JSON loaders**: `model.load_outages` and hardened `model.load_pathways` with
  friendly validation errors.
- **Examples**: runnable `examples/sample_plan.json` and `examples/outages.json`.
- **Docs**: overhauled README; new `docs/ARCHITECTURE.md`, `docs/USAGE.md`, and
  `ROADMAP.md`.
- **CI/lint**: Ruff lint job and `pip install -e .` in CI; expanded test suite
  (model, validation scoring, failover edges, analytics, renderers, CLI).

### Changed
- Added type hints and docstrings across modules (no behavior change).

## [0.2.0] — 2026-07-03

### Added
- **RF link-budget model** (`linkbudget.py`): free-space path loss + received-power
  margin to check whether each PACE pathway closes at range, plus an ATAK/WINTAK
  interoperability check (throughput sufficient for CoT PLI). CLI `linkbudget`.
  First-order model — documented as such.

## [0.1.0] — 2026-07-01

Initial public release.

### Added
- PACE pathway model — `model`.
- PACE plan validation (four tiers, physical-domain diversity, no-pLEO) with
  resilience scoring — `pace`.
- Automated failover simulation across outage timelines — `failover`.
- Sample plans (valid / single-domain / pLEO / missing-tier) and outage
  scenarios with expected results — `synth`.
- CLI (`hoplink`): `demo`, `validate`.
- Verification harness: PACE rule-verdict accuracy + failover correctness;
  results in `RESULTS.md`. 6 tests. CI across Python 3.9–3.13.
