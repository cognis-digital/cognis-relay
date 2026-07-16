# Hoplink — Verification Results

Reproduce with: `python bench/run_all.py`.

Environment: CPython 3.14.0 on Windows/AMD64.

| Metric | Value |
|---|---|
| PACE rule-verdict accuracy | 1.000 |
| Failover sequence correct | True |
| Failover sequence | P -> A -> C -> E -> A -> P |
| pLEO disqualified | True |
| Determinism | True |

Gated in CI by `tests/test_bench.py`. See `docs/LIMITATIONS.md`.
