# SOLIC Challenge Area 7 — Capability Mapping

| Desired capability | Cognis Relay | Module |
|---|---|---|
| Four distinct pathways (P/A/C/E) | Tier-presence validation | `pace` |
| Modality diversity across physical domains | Domain-diversity check (fails 100% single domain) | `pace` |
| Automated failover where possible | Priority failover simulation over outage timeline | `failover` |
| LPI/LPD/LPE consideration | LPI posture in resilience score | `pace` |
| pLEO disqualified | Hard disqualification rule | `pace` |
| Man-portable / SWaP-C envelope | Pathway `man_portable` + SWaP-C metadata | `model` |

## TRL posture (honest)
- **Validation + failover simulation (working, measured):** tested with
  reproducible metrics (`RESULTS.md`) — 1.00 rule-verdict accuracy on labeled
  configs, correct failover sequence, pLEO always disqualified.
- **Prototype scope (post-award):** integrate real link-budget/waveform models,
  ATAK/WINTAK PLI messaging validation, and hardware-in-the-loop SWaP-C
  measurement.
