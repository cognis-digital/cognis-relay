"""Cognis Relay CLI."""

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


def build_parser():
    p = argparse.ArgumentParser(prog="cognis-relay",
                                description="Cognis Relay — BLOS PACE validator & failover simulator")
    p.add_argument("--version", action="version", version=f"cognis-relay {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    d = sub.add_parser("demo", help="validate + simulate the sample PACE plan")
    d.set_defaults(func=cmd_demo)

    v = sub.add_parser("validate", help="validate a PACE plan JSON")
    v.add_argument("--plan", required=True)
    v.add_argument("--json", action="store_true")
    v.set_defaults(func=cmd_validate)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
