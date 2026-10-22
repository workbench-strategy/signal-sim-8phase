"""
Layer 3: Business Logic Adapter.

Translates high-level ITS intents (e.g. read phase status, set timing plan)
into NTCIP GET/SET operations via the Manager facade.
"""

from ntcip.business.intents import PhaseStatusSnapshot, SetSignalTimingPlan
from ntcip.business.manager import NtcipManager

__all__ = [
    "NtcipManager",
    "PhaseStatusSnapshot",
    "SetSignalTimingPlan",
]
