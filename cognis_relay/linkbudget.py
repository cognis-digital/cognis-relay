"""RF link-budget & interoperability analysis for PACE pathways.

A first-order link budget (free-space path loss + margin) to sanity-check whether
each pathway closes at a given range, and an ATAK/WINTAK interoperability check
(does the pathway carry enough throughput for CoT position/data messaging).

First-order model — real planning needs terrain, fading, and waveform specifics.
See docs/COMPLIANCE.md.
"""

from __future__ import annotations

import math

# Minimum sustained throughput to carry ATAK CoT PLI + light data (kbps).
ATAK_PLI_MIN_KBPS = 2.4


def fspl_db(freq_mhz: float, dist_km: float) -> float:
    """Free-space path loss (dB). FSPL = 32.44 + 20log10(d_km) + 20log10(f_MHz)."""
    return 32.44 + 20 * math.log10(max(dist_km, 1e-6)) + 20 * math.log10(max(freq_mhz, 1e-6))


def link_margin(tx_dbm: float, tx_gain_dbi: float, rx_gain_dbi: float,
                freq_mhz: float, dist_km: float, rx_sens_dbm: float,
                extra_loss_db: float = 3.0) -> dict:
    """Received power and margin over receiver sensitivity."""
    eirp = tx_dbm + tx_gain_dbi
    fspl = fspl_db(freq_mhz, dist_km)
    prx = eirp - fspl - extra_loss_db + rx_gain_dbi
    margin = prx - rx_sens_dbm
    return {"eirp_dbm": round(eirp, 2), "fspl_db": round(fspl, 2),
            "prx_dbm": round(prx, 2), "margin_db": round(margin, 2),
            "closes": margin > 0}


def assess_pathway(pathway, geometry: dict) -> dict:
    """geometry: {tx_dbm, tx_gain_dbi, rx_gain_dbi, freq_mhz, dist_km, rx_sens_dbm}"""
    lb = link_margin(**{k: geometry[k] for k in
                        ("tx_dbm", "tx_gain_dbi", "rx_gain_dbi", "freq_mhz",
                         "dist_km", "rx_sens_dbm")})
    atak = pathway.bandwidth_kbps >= ATAK_PLI_MIN_KBPS
    return {"tier": pathway.tier, "name": pathway.name, "link_budget": lb,
            "atak_capable": atak, "man_portable": pathway.man_portable}


def atak_summary(pathways: list) -> dict:
    """Which PACE tiers can carry ATAK/WINTAK PLI given their throughput."""
    capable = [p.tier for p in pathways if p.bandwidth_kbps >= ATAK_PLI_MIN_KBPS]
    return {"atak_min_kbps": ATAK_PLI_MIN_KBPS, "capable_tiers": sorted(set(capable)),
            "all_tiers_capable": len(set(capable)) >= len({p.tier for p in pathways})}
