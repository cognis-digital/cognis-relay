"""Human-readable / JSON PACE products."""

from __future__ import annotations

import json


def render_json(product) -> str:
    return json.dumps(product, indent=2)


def render_text(product) -> str:
    v = product["validation"]
    L = []
    L.append("=" * 68)
    L.append("  COGNIS RELAY  |  BLOS PACE Communications Assessment")
    L.append("  Cognis Digital LLC")
    L.append("=" * 68)
    L.append(f"PACE valid: {v['valid']}   resilience score: {v['resilience_score']}")
    L.append(f"Tiers: {','.join(v['tiers_present'])}   domains: {', '.join(v['domains'])}")
    if v["violations"]:
        L.append("Violations:")
        for x in v["violations"]:
            L.append(f"   ! {x}")
    fo = product.get("failover")
    if fo:
        L.append("")
        L.append(f"Failover: {' -> '.join(str(s) for s in fo['sequence'])}")
        L.append(f"Availability: {fo['availability']*100:.0f}%   transitions: {fo['transitions']}"
                 + (f"   BLACKOUT at {fo['blackout_steps']}" if fo["blackout_steps"] else ""))
    return "\n".join(L)
