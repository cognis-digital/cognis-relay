"""Hoplink CLI."""

from __future__ import annotations

import argparse
import sys

from . import __version__, synth
from .failover import simulate
from .model import load_pathways
from .pace import validate
from .report import render_json, render_text


def _product(pathways, outages=None):
    product = {"validation": validate(pathways),
               "pathways": [p.to_dict() for p in pathways]}
    if outages is not None:
        product["failover"] = simulate(pathways, outages)
    return product


def cmd_demo(args):
    plan = synth.sample_plan()
    timeline, _ = synth.sample_outages()
    print(render_text(_product(plan, timeline)))
    return 0


def cmd_validate(args):
    plan = load_pathways(args.plan)
    print(render_json(_product(plan)) if args.json else render_text(_product(plan)))
    return 0


def cmd_linkbudget(args):
    from . import synth
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


def build_parser():
    p = argparse.ArgumentParser(prog="hoplink",
                                description="Hoplink — BLOS PACE validator & failover simulator")
    p.add_argument("--version", action="version", version=f"hoplink {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    d = sub.add_parser("demo", help="validate + simulate the sample PACE plan")
    d.set_defaults(func=cmd_demo)

    v = sub.add_parser("validate", help="validate a PACE plan JSON")
    v.add_argument("--plan", required=True)
    v.add_argument("--json", action="store_true")
    v.set_defaults(func=cmd_validate)

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
