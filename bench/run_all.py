"""Run verification; write bench/results.json and RESULTS.md."""

from __future__ import annotations

import json
import os
import platform
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bench import evaluate  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def render_md(a, env) -> str:
    L = []
    L.append("# Hoplink — Verification Results\n")
    L.append("Reproduce with: `python bench/run_all.py`.\n")
    L.append(f"Environment: {env['implementation']} {env['python']} on {env['system']}/{env['machine']}.\n")
    L.append("| Metric | Value |")
    L.append("|---|---|")
    L.append(f"| PACE rule-verdict accuracy | {a['rule_accuracy']:.3f} |")
    L.append(f"| Failover sequence correct | {a['failover_correct']} |")
    L.append(f"| Failover sequence | {' -> '.join(str(s) for s in a['failover_sequence'])} |")
    L.append(f"| pLEO disqualified | {a['pleo_disqualified']} |")
    L.append(f"| Determinism | {a['determinism']} |")
    L.append("")
    L.append("Gated in CI by `tests/test_bench.py`. See `docs/LIMITATIONS.md`.\n")
    return "\n".join(L)


def main():
    a = evaluate.evaluate()
    env = {"python": platform.python_version(), "implementation": platform.python_implementation(),
           "system": platform.system(), "machine": platform.machine()}
    with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as f:
        json.dump({"accuracy": a, "environment": env}, f, indent=2)
    with open(os.path.join(ROOT, "RESULTS.md"), "w", encoding="utf-8") as f:
        f.write(render_md(a, env))
    print("[+] wrote bench/results.json and RESULTS.md")
    print(render_md(a, env))


if __name__ == "__main__":
    main()
