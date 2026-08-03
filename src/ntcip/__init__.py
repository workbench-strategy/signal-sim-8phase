"""
NTCIP-compliant Intelligent Transportation Systems stack.

Layered architecture (bottom-up):

1. ``ntcip.protocol``  - SNMPv1/v2c/v3 engine abstraction (async UDP)
2. ``ntcip.mib``       - OID registry, ASN.1 BER types, domain objects
3. ``ntcip.business``  - Manager/Agent facade and business intents

References:
    - NTCIP 1103: Transportation Management Protocols
    - NTCIP 1201: Global Object Definitions
    - NTCIP 1202: Object Definitions for ASC
    - NTCIP 8004: Structure and Identification of Management Information
"""

from ntcip.business.manager import NtcipManager
from ntcip.mib.date_and_time import NtcipDateAndTime
from ntcip.mib.registry import MibRegistry
from ntcip.protocol.async_engine import AsyncSnmpEngine

__all__ = [
    "AsyncSnmpEngine",
    "MibRegistry",
    "NtcipDateAndTime",
    "NtcipManager",
]

__version__ = "0.1.0"
