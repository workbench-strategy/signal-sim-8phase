"""Tests for MIB registry and mapper."""

from __future__ import annotations

import pytest

from ntcip.exceptions import OidMismatchError, OidNotFoundError
from ntcip.mib.date_and_time import NtcipDateAndTime
from ntcip.mib.mapper import DefaultMibObjectMapper
from ntcip.mib.objects.asc_1202 import PHASE_STATUS_GROUP_GREENS_OID, PhaseStatusGroup
from ntcip.mib.objects.global_1201 import UNIT_ID_OID, UNIT_LOCATION_OID
from ntcip.mib.registry import build_default_ntcip_registry
from ntcip.protocol.models import SnmpVarBind


def test_default_registry_contains_1201_and_1202():
    registry = build_default_ntcip_registry()
    assert UNIT_ID_OID in registry
    assert UNIT_LOCATION_OID in registry
    assert PHASE_STATUS_GROUP_GREENS_OID in registry
    unit = registry.get_by_name("unitID")
    assert unit.standard == "NTCIP 1201"
    phase = registry.get_by_name("phaseStatusGroupGreens")
    assert phase.standard == "NTCIP 1202"


def test_mapper_decodes_phase_status():
    mapper = DefaultMibObjectMapper(build_default_ntcip_registry())
    vb = SnmpVarBind(
        oid=PHASE_STATUS_GROUP_GREENS_OID,
        value=bytes([0b00010010]),
        asn1_type="OCTET STRING",
    )
    domain = mapper.to_domain_as(vb, PhaseStatusGroup)
    assert domain.active_phases() == [2, 5]


def test_mapper_decodes_date_and_time():
    mapper = DefaultMibObjectMapper(build_default_ntcip_registry())
    raw = NtcipDateAndTime(2026, 8, 3, 12, 0, 0, 0).to_octets()
    vb = SnmpVarBind(
        oid="1.3.6.1.4.1.1206.4.2.6.3.2.0",
        value=raw,
        asn1_type="DateAndTime",
    )
    value = mapper.to_domain_as(vb, NtcipDateAndTime)
    assert value.year == 2026 and value.month == 8


def test_oid_not_found():
    registry = build_default_ntcip_registry()
    with pytest.raises(OidNotFoundError):
        registry.get_by_oid("1.2.3.4.5")


def test_oid_type_mismatch():
    mapper = DefaultMibObjectMapper(build_default_ntcip_registry())
    with pytest.raises(OidMismatchError):
        mapper.validate_type(UNIT_ID_OID, "INTEGER")
