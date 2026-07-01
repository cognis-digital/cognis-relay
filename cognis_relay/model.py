"""PACE pathway model."""

from __future__ import annotations

import json
from dataclasses import dataclass, field

TIERS = ["P", "A", "C", "E"]
TIER_NAME = {"P": "Primary", "A": "Alternate", "C": "Contingency", "E": "Emergency"}


@dataclass
class Pathway:
    tier: str                # P | A | C | E
    name: str
    modality: str            # e.g. MEO-SATCOM, HF-ALE, troposcatter, PLB
    domain: str              # physical domain: geo-satcom | meo-satcom | hf | tropo | terrestrial | pleo
    bandwidth_kbps: float
    lpi: float = 0.5         # 0..1 LPI/LPD/LPE posture
    is_pleo: bool = False
    man_portable: bool = True
    meta: dict = field(default_factory=dict)

    def to_dict(self):
        return {"tier": self.tier, "tier_name": TIER_NAME.get(self.tier, self.tier),
                "name": self.name, "modality": self.modality, "domain": self.domain,
                "bandwidth_kbps": self.bandwidth_kbps, "lpi": self.lpi,
                "is_pleo": self.is_pleo, "man_portable": self.man_portable}


def load_pathways(path: str) -> list:
    with open(path, "r", encoding="utf-8") as f:
        return [Pathway(**p) for p in json.load(f)]
