# Roadmap

Hoplink validates BLOS PACE communications plans, analyzes their resilience, and
simulates automated failover — offline and dependency-free. This roadmap sketches
where it is headed. It is intentionally additive: existing APIs, CLI subcommands,
and output contracts are preserved as the tool grows.

## Guiding principles
- **Offline-first, zero runtime dependencies.** Anything new must still run in an
  air-gapped planning cell with only a Python interpreter.
- **Additive & backward-compatible.** New capability layers on top; published
  signatures and JSON shapes stay stable.
- **Honest fidelity.** First-order models are labeled as such; measured claims are
  gated by the verification harness.
- **Deterministic & testable.** Every feature ships with real assertions and,
  where it makes a verifiable claim, a bench metric.

## Near-term (next release)
- **Probabilistic outage timelines.** Generate outage timelines from per-domain
  availability/MTBF/MTTR parameters and report expected availability with a seed
  for reproducibility.
- **Plan authoring helpers.** `hoplink new-plan` scaffold and a `--schema`
  command emitting the JSON schema for plans and outage timelines.
- **Richer resilience report.** Two-domain (double-fault) SPOF analysis and a
  weakest-link ranking surfaced in text/markdown/JSON.
- **Exit-code gating.** Optional `--strict` flag so `validate`/`analyze` return
  non-zero on invalid or fragile plans for CI/pipeline use.

## Mid-term
- **Throughput-aware failover.** Fold `bandwidth_kbps` and the ATAK PLI gate into
  the failover decision so a tier that is "up" but under-provisioned degrades
  gracefully.
- **Batch mode.** Validate/score a directory of plans and emit a comparison
  matrix (CSV + Markdown) for trade studies.
- **Config-driven scoring.** Externalize resilience-score weights and thresholds
  into an optional config file (defaults unchanged).
- **HTML report export.** A self-contained, offline HTML rendering alongside
  text/json/markdown.

## Long-term
- **Time-continuous degradation model.** Move beyond binary up/down to partial
  link degradation and margin-driven failover, integrating the link-budget layer.
- **Waveform/terrain-aware link budgets.** Optional plug-in models (still
  stdlib-only core) for more realistic BLOS planning.
- **Mission-thread scenarios.** Compose plans + timelines into named scenarios
  with pass/fail objectives for exercise planning.
- **Interoperability adapters.** Import/export to common comms-planning
  interchange formats without adding required runtime dependencies.

## Non-goals
- Transmitting, configuring, or controlling real radios.
- Anything that requires network access at runtime in the core package.
- Removing or breaking existing public APIs or CLI subcommands.

Ideas and RFCs are welcome via GitHub Issues/Discussions.
