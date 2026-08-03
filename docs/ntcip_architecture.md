# NTCIP Stack Architecture

> Broader lab mission: see [`ITS_LAB_STRATEGY.md`](ITS_LAB_STRATEGY.md) and
> [`ARCHITECTURE.md`](ARCHITECTURE.md). NTCIP is the first protocol vertical
> inside the multi-domain ITS lab (`src/its/` + `src/ntcip/`).

## Tech choices (scaffold defaults)

| Concern | Choice |
|---------|--------|
| Language | Python 3.9+ |
| Concurrency | `asyncio` (non-blocking UDP I/O) |
| Preferred SNMP library | **pysnmp** (pluggable via `SnmpBackend`) |
| Demo / tests | `StubSnmpBackend` (no live cabinet required) |

Placeholders in the original brief were filled to match this repository's
existing Python traffic-signal toolchain.

## Layers

```
+------------------------------------------------------+
| Layer 3: Business Logic Adapter                      |
|   NtcipManager, PhaseStatusAdapter, intents          |
+---------------------------+--------------------------+
                            | typed domain objects
+---------------------------v--------------------------+
| Layer 2: NTCIP Object & MIB                          |
|   MibRegistry, MibObjectMapper, DateAndTime, OIDs    |
+---------------------------+--------------------------+
                            | SnmpVarBind / OIDs
+---------------------------v--------------------------+
| Layer 1: Protocol Engine                             |
|   SnmpEngine / AsyncSnmpEngine -> SnmpBackend        |
|   (pysnmp | stub | future Net-SNMP)                  |
+------------------------------------------------------+
```

## Roles

- **Manager (Central System)** -- implemented by `NtcipManager` (GET/SET focus).
- **Agent (Field Device)** -- same Layer 1/2; future facade can expose Agent MIB.

## Standards referenced

- NTCIP 1103 -- Transportation Management Protocols
- NTCIP 1201 -- Global Object Definitions (`unitID`, `unitLocation`, DateAndTime)
- NTCIP 1202 -- ASC (`phaseStatusGroupGreens`, etc.)
- NTCIP 8004 -- Structure and Identification of Management Information

## Quick start

```bash
# Demo (stub backend)
PYTHONPATH=src python -m ntcip

# Tests
PYTHONPATH=src pytest -v tests/ntcip
```
