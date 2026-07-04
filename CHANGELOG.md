# Changelog

Adheres to [Semantic Versioning](https://semver.org/).

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
