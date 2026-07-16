"""Hoplink CLI.

Subcommands:

* ``demo``       — validate + simulate the built-in sample PACE plan.
* ``validate``   — validate a PACE plan JSON (text / json / markdown output).
* ``simulate``   — run a failover simulation of a plan over an outage timeline.
* ``analyze``    — structural resilience / single-point-of-failure analysis.
* ``linkbudget`` — first-order RF link-budget + ATAK interop for the sample plan.
"""

from __future__ import annotations

import argparse
import sys

from . import __version__, synth
from .analysis import analyze_failover, resilience_report
from .model import load_outages, load_pathways
from .pace import validate
from .report import render_json, render_markdown, render_text


def _product(pathways, outages=None, resilience=False):
    """Assemble a PACE product dict from a plan and optional extras."""
    product = {"validation": validate(pathways),
               "pathways": [p.to_dict() for p in pathways]}
    if resilience:
        product["resilience"] = resilience_report(pathways)
    if outages is not None:
        product["failover"] = analyze_failover(pathways, outages)
    return product


def _emit(product, fmt: str) -> None:
    """Print a product in the requested format (text / json / markdown)."""
    if fmt == "json":
        print(render_json(product))
    elif fmt == "markdown":
        print(render_markdown(product))
    else:
        print(render_text(product))


def _resolve_format(args, default="text") -> str:
    """Resolve output format, honoring the legacy ``--json`` flag."""
    fmt = getattr(args, "format", None)
    if fmt:
        return fmt
    if getattr(args, "json", False):
        return "json"
    return default


def cmd_demo(args):
    plan = synth.sample_plan()
    timeline, _ = synth.sample_outages()
    _emit(_product(plan, timeline, resilience=True), _resolve_format(args))
    return 0


def cmd_validate(args):
    plan = load_pathways(args.plan)
    _emit(_product(plan, resilience=args.resilience), _resolve_format(args))
    return 0


def cmd_simulate(args):
    plan = load_pathways(args.plan)
    outages = load_outages(args.outages)
    _emit(_product(plan, outages, resilience=args.resilience), _resolve_format(args))
    return 0


def cmd_analyze(args):
    plan = load_pathways(args.plan)
    _emit(_product(plan, resilience=True), _resolve_format(args))
    return 0


def cmd_linkbudget(args):
    from .linkbudget import assess_pathway, atak_summary
    plan = synth.sample_plan()
    # illustrative geometry: dismounted team to a BLOS relay ~2000 km
    geom = {"tx_dbm": 43.0, "tx_gain_dbi": 3.0, "rx_gain_dbi": 30.0,
            "freq_mhz": args.freq, "dist_km": args.dist, "rx_sens_dbm": -110.0}
    print(f"COGNIS RELAY | link-budget @ {args.dist} km, {args.freq} MHz")
    for p in plan:
        a = assess_pathway(p, geom)
        lb = a["link_budget"]
        print(f"  {p.tier} {p.name:26} margin {lb['margin_db']:+.1f} dB "
              f"{'CLOSES' if lb['closes'] else 'FAILS '}  ATAK:{'yes' if a['atak_capable'] else 'no'}")
    s = atak_summary(plan)
    print(f"ATAK/WINTAK PLI capable tiers: {','.join(s['capable_tiers'])} "
          f"(need >= {s['atak_min_kbps']} kbps)")
    return 0


def _add_format_flags(parser) -> None:
    """Attach the shared output-format flags to a subparser."""
    parser.add_argument("--format", choices=["text", "json", "markdown"],
                        help="output format (default: text)")
    parser.add_argument("--json", action="store_true",
                        help="shorthand for --format json (kept for compatibility)")


def build_parser():
    p = argparse.ArgumentParser(prog="hoplink",
                                description="Hoplink — BLOS PACE validator & failover simulator")
    p.add_argument("--version", action="version", version=f"hoplink {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    d = sub.add_parser("demo", help="validate + simulate the sample PACE plan")
    _add_format_flags(d)
    d.set_defaults(func=cmd_demo)

    v = sub.add_parser("validate", help="validate a PACE plan JSON")
    v.add_argument("--plan", required=True)
    v.add_argument("--resilience", action="store_true",
                   help="include single-point-of-failure resilience analysis")
    _add_format_flags(v)
    v.set_defaults(func=cmd_validate)

    s = sub.add_parser("simulate", help="simulate failover of a plan over an outage timeline")
    s.add_argument("--plan", required=True)
    s.add_argument("--outages", required=True,
                   help="JSON file: list of steps, each a list of down modality/domain strings")
    s.add_argument("--resilience", action="store_true",
                   help="also include single-point-of-failure resilience analysis")
    _add_format_flags(s)
    s.set_defaults(func=cmd_simulate)

    a = sub.add_parser("analyze", help="structural resilience / single-point-of-failure analysis")
    a.add_argument("--plan", required=True)
    _add_format_flags(a)
    a.set_defaults(func=cmd_analyze)

    lb = sub.add_parser("linkbudget", help="RF link-budget + ATAK interop for the sample plan")
    lb.add_argument("--dist", type=float, default=2000.0, help="range (km)")
    lb.add_argument("--freq", type=float, default=1500.0, help="frequency (MHz)")
    lb.set_defaults(func=cmd_linkbudget)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
