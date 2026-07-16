"""PACE pathway model.

Defines the :class:`Pathway` dataclass — one leg of a Primary/Alternate/
Contingency/Emergency plan — plus loaders for plan and outage-timeline JSON.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Set

TIERS = ["P", "A", "C", "E"]
TIER_NAME = {"P": "Primary", "A": "Alternate", "C": "Contingency", "E": "Emergency"}


@dataclass
class Pathway:
    """A single PACE pathway (one communications leg).

    Attributes:
        tier: PACE tier — one of ``P``/``A``/``C``/``E``.
        name: Human-readable pathway name.
        modality: Waveform/terminal, e.g. ``MEO-SATCOM``, ``HF-ALE``.
        domain: Physical domain, e.g. ``meo-satcom``, ``hf``, ``terrestrial``.
        bandwidth_kbps: Sustained throughput in kbps.
        lpi: Low-probability-of-intercept/-detection posture, ``0..1``.
        is_pleo: Whether the pathway relies on a proliferated-LEO constellation.
        man_portable: Whether the terminal is man-portable.
        meta: Free-form SWaP-C / operator metadata.
    """

    tier: str                # P | A | C | E
    name: str
    modality: str            # e.g. MEO-SATCOM, HF-ALE, troposcatter, PLB
    domain: str              # physical domain: geo-satcom | meo-satcom | hf | tropo | terrestrial | pleo
    bandwidth_kbps: float
    lpi: float = 0.5         # 0..1 LPI/LPD/LPE posture
    is_pleo: bool = False
    man_portable: bool = True
    meta: dict = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable view of the pathway."""
        return {"tier": self.tier, "tier_name": TIER_NAME.get(self.tier, self.tier),
                "name": self.name, "modality": self.modality, "domain": self.domain,
                "bandwidth_kbps": self.bandwidth_kbps, "lpi": self.lpi,
                "is_pleo": self.is_pleo, "man_portable": self.man_portable}


def load_pathways(path: str) -> List[Pathway]:
    """Load a PACE plan from a JSON file (a list of pathway objects).

    Raises:
        ValueError: if the JSON is not a list of objects, or a pathway is
            missing a required field / carries an unknown field.
    """
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    if not isinstance(raw, list):
        raise ValueError("plan JSON must be a list of pathway objects")
    pathways: List[Pathway] = []
    for i, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ValueError(f"pathway #{i} must be a JSON object")
        try:
            pathways.append(Pathway(**item))
        except TypeError as e:  # missing/unexpected field -> friendly message
            raise ValueError(f"pathway #{i} is invalid: {e}") from e
    return pathways


def load_outages(path: str) -> List[Set[str]]:
    """Load an outage timeline from a JSON file.

    The file is a list of steps; each step is a list of modality/domain strings
    that are degraded at that step (an empty list means all links up).

    Raises:
        ValueError: if the structure is not a list of lists of strings.
    """
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    if not isinstance(raw, list):
        raise ValueError("outage timeline must be a list of steps")
    timeline: List[Set[str]] = []
    for i, step in enumerate(raw):
        if not isinstance(step, (list, tuple)):
            raise ValueError(f"outage step #{i} must be a list of strings")
        timeline.append({str(x) for x in step})
    return timeline
