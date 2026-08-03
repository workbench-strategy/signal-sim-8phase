"""Example NTCIP MIB object definition modules."""

from ntcip.mib.objects.asc_1202 import (
    PHASE_STATUS_GROUP_GREENS_OID,
    PhaseStatusGroup,
    asc_1202_definitions,
)
from ntcip.mib.objects.global_1201 import (
    UNIT_ID_OID,
    UNIT_LOCATION_OID,
    global_1201_definitions,
)

__all__ = [
    "PHASE_STATUS_GROUP_GREENS_OID",
    "PhaseStatusGroup",
    "UNIT_ID_OID",
    "UNIT_LOCATION_OID",
    "asc_1202_definitions",
    "global_1201_definitions",
]
