"""Cognis Relay — BLOS PACE communications architecture validator & simulator.

Validates a Primary/Alternate/Contingency/Emergency (PACE) communications plan
for physical-domain diversity, LPI/LPD posture, SWaP-C envelope, and the
challenge's hard constraints (four distinct pathways; not reliant on a single
domain; no pLEO), then simulates automated failover through link outages.

(c) 2026 Cognis Digital LLC (Wyoming, USA). Source-available under COCL-1.0.
"""

__version__ = "0.2.0"
__all__ = ["model", "pace", "failover", "linkbudget", "report", "synth"]
