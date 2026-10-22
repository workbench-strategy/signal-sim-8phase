"""
Example mappings from NTCIP 1201 -- Global Object Definitions.

OID tree (NTCIP 8004 / NEMA enterprise)::

    1.3.6.1.4.1.1206.4.2.6   -- global (NTCIP 1201)
      .1                     -- globalConfiguration
      .3                     -- globalTime
      .4                     -- unit (identification / location parameters)

The ``unitID`` and ``unitLocation`` objects below follow the common NTCIP
1201 unit-parameter layout used by ASC and DMS field devices. Exact leaf
numbers can vary slightly by MIB revision; treat these as scaffold defaults
and align with your vendor's compiled MIB under ``mibs/``.
"""

from __future__ import annotations

from typing import List

from ntcip.mib.date_and_time import decode_date_and_time, encode_date_and_time
from ntcip.mib.types import Asn1Type, MibObjectDefinition

# profiles.global.unit
_UNIT_BASE = "1.3.6.1.4.1.1206.4.2.6.4"

UNIT_ID_OID = f"{_UNIT_BASE}.3.0"
"""unitID -- unique controller identifier (DisplayString)."""

UNIT_LOCATION_OID = f"{_UNIT_BASE}.7.0"
"""unitLocation -- human-readable intersection / cabinet location."""

# profiles.global.globalTime.globalLocalTimeBase (DateAndTime)
GLOBAL_LOCAL_TIME_OID = "1.3.6.1.4.1.1206.4.2.6.3.2.0"
"""global local time -- NTCIP DateAndTime (8 octets)."""

# profiles.global.globalConfiguration.globalSetIDParameter
GLOBAL_SET_ID_OID = "1.3.6.1.4.1.1206.4.2.6.1.1.0"
"""Database set identifier for configuration consistency checks."""


def global_1201_definitions() -> List[MibObjectDefinition]:
    """Return scaffold definitions for selected NTCIP 1201 objects."""
    return [
        MibObjectDefinition(
            oid=UNIT_ID_OID,
            name="unitID",
            asn1_type=Asn1Type.DISPLAY_STRING,
            standard="NTCIP 1201",
            domain_type=str,
            description="Unique identification of the field unit / controller.",
        ),
        MibObjectDefinition(
            oid=UNIT_LOCATION_OID,
            name="unitLocation",
            asn1_type=Asn1Type.DISPLAY_STRING,
            standard="NTCIP 1201",
            domain_type=str,
            description="Physical or logical location description of the unit.",
        ),
        MibObjectDefinition(
            oid=GLOBAL_LOCAL_TIME_OID,
            name="globalLocalTime",
            asn1_type=Asn1Type.DATE_AND_TIME,
            standard="NTCIP 1201",
            description="Controller local time as NTCIP DateAndTime (8 octets).",
            decoder=decode_date_and_time,
            encoder=encode_date_and_time,
        ),
        MibObjectDefinition(
            oid=GLOBAL_SET_ID_OID,
            name="globalSetIDParameter",
            asn1_type=Asn1Type.INTEGER,
            standard="NTCIP 1201",
            domain_type=int,
            description="Configuration set ID parameter (globalConfiguration).",
        ),
    ]
