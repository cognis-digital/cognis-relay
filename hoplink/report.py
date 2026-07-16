"""Human-readable / JSON / Markdown PACE products."""

from __future__ import annotations

import json


def render_json(product) -> str:
    """Render a PACE product dict as indented JSON."""
    return json.dumps(product, indent=2)


def render_markdown(product) -> str:
    """Render a PACE product dict as a self-contained Markdown report.

    Accepts the same product shape as :func:`render_text` (a dict with
    ``validation`` and ``pathways``, and optionally ``failover`` and
    ``resilience``) and is safe to write to a ``.md`` file or paste into an
    issue/PR.
    """
    v = product["validation"]
    L = []
    L.append("# BLOS PACE Communications Assessment")
    L.append("")
    L.append(f"- **PACE valid:** {v['valid']}")
    L.append(f"- **Resilience score:** {v['resilience_score']}")
    L.append(f"- **Tiers present:** {', '.join(v['tiers_present']) or '—'}")
    L.append(f"- **Physical domains:** {', '.join(v['domains']) or '—'}")
    if v["violations"]:
        L.append("")
        L.append("## Violations")
        for x in v["violations"]:
            L.append(f"- {x}")

    pathways = product.get("pathways") or []
    if pathways:
        L.append("")
        L.append("## Pathways")
        L.append("| Tier | Name | Modality | Domain | kbps | LPI | pLEO |")
        L.append("|---|---|---|---|---|---|---|")
        for p in pathways:
            L.append(
                f"| {p['tier']} | {p['name']} | {p['modality']} | {p['domain']} "
                f"| {p['bandwidth_kbps']} | {p['lpi']} | {p['is_pleo']} |"
            )

    res = product.get("resilience")
    if res:
        L.append("")
        L.append("## Structural resilience")
        L.append(f"- **Grade:** {res['grade']}")
        L.append(f"- **Domain count:** {res['domain_count']}")
        L.append(f"- **Single-domain fault tolerant:** "
                 f"{res['spof']['single_domain_fault_tolerant']}")
        if res["spof"]["per_domain"]:
            L.append("")
            L.append("| Domain lost | Top surviving tier | Surviving tiers |")
            L.append("|---|---|---|")
            for r in res["spof"]["per_domain"]:
                top = r["top_surviving_tier"] or "BLACKOUT"
                surv = ", ".join(r["surviving_tiers"]) or "none"
                L.append(f"| {r['domain']} | {top} | {surv} |")

    fo = product.get("failover")
    if fo:
        L.append("")
        L.append("## Failover simulation")
        L.append(f"- **Sequence:** {' → '.join(str(s) for s in fo['sequence'])}")
        L.append(f"- **Availability:** {fo['availability'] * 100:.0f}%")
        L.append(f"- **Transitions:** {fo['transitions']}")
        if fo.get("blackout_steps"):
            L.append(f"- **Blackout steps:** {fo['blackout_steps']}")
        m = fo.get("metrics")
        if m:
            L.append(f"- **Longest blackout:** {m['longest_blackout']} step(s)")
            L.append(f"- **Mean time to recover:** {m['mttr_steps']} step(s)")
    return "\n".join(L)


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
    res = product.get("resilience")
    if res:
        L.append("")
        L.append(f"Structural resilience: {res['grade']}   "
                 f"single-domain fault tolerant: "
                 f"{res['spof']['single_domain_fault_tolerant']}")
        for r in res["spof"]["per_domain"]:
            top = r["top_surviving_tier"] or "BLACKOUT"
            L.append(f"   lose {r['domain']:14} -> top surviving tier {top}")
    fo = product.get("failover")
    if fo:
        L.append("")
        L.append(f"Failover: {' -> '.join(str(s) for s in fo['sequence'])}")
        L.append(f"Availability: {fo['availability']*100:.0f}%   transitions: {fo['transitions']}"
                 + (f"   BLACKOUT at {fo['blackout_steps']}" if fo["blackout_steps"] else ""))
        m = fo.get("metrics")
        if m:
            L.append(f"Longest blackout: {m['longest_blackout']} step(s)   "
                     f"MTTR: {m['mttr_steps']} step(s)")
    return "\n".join(L)
