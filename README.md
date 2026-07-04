<h1 align="center">🟣 Hoplink</h1>
<p align="center"><b>BLOS PACE communications validator &amp; failover simulator</b><br>
<i>Validate Primary/Alternate/Contingency/Emergency plans and simulate automated failover — self-hosted, offline.</i></p>

<p align="center">
<img alt="license" src="https://img.shields.io/badge/license-COCL--1.0-6D28D9">
<img alt="python" src="https://img.shields.io/badge/python-3.9%2B-6D28D9">
<img alt="deps" src="https://img.shields.io/badge/dependencies-none%20(stdlib)-6D28D9">
<img alt="status" src="https://img.shields.io/badge/status-v0.1.0-6D28D9">
</p>

---

> **Built for:** SOLIC Accelerator / ONIX OTA — **Challenge Area 7: Beyond-Line-of-Sight PACE Communications Architecture Without pLEO.**
> Validate a four-pathway PACE plan for physical-domain diversity, LPI/LPD posture, and the hard constraints (four distinct pathways; not single-domain-reliant; **pLEO disqualified**), then simulate automated failover through link outages.

## What it does

- ✅ **PACE validation** — enforces P/A/C/E presence, domain diversity, no-pLEO; scores resilience.
- 🔁 **Failover simulation** — highest-priority available tier per step across an outage timeline; availability, transitions, blackouts.
- 📊 **Resilience scoring** — tiers × domain diversity × LPI posture, minus violations.
- 🔒 **Offline / zero-dependency** — pure Python stdlib.

## Quick start

```bash
git clone https://github.com/cognis-digital/hoplink
cd hoplink
python -m hoplink demo
python -m hoplink validate --plan my_pace.json --json
```

## Verification & proof

Gated in CI (`python bench/run_all.py` → [`RESULTS.md`](RESULTS.md)):

| Metric | Value |
|---|---|
| PACE rule-verdict accuracy | **1.00** (valid / single-domain / pLEO / missing-tier) |
| Failover sequence correct | ✓ (P→A→C→E→A→P) |
| pLEO disqualified | ✓ |
| Determinism | ✓ |

## License

Source-available under **COCL v1.0** (see [LICENSE](LICENSE)).

<p align="center"><sub>© 2026 Cognis Digital LLC · <a href="https://cognis.digital">cognis.digital</a></sub></p>
