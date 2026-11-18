# Platform Architecture (Locked Seams)

This document freezes the **high-value shapes** of the ITS lab.
Implementations may grow; these seams should stay stable.

## System context

```
+------------------------------------------------------------------+
|  Playbooks / CLI / GIS / future Northbound API                   |
+-----------------------------+------------------------------------+
                              | intents (domain language)
+-----------------------------v------------------------------------+
|  Policies (experiments)     |  shadow logger (observe/recommend) |
+-----------------------------+------------------------------------+
                              |
+-----------------------------v------------------------------------+
|  Domain adapters                                                 |
|  signals | vms | rwis | cctv | data_station | tunnel | airport   |
+-----------------------------+------------------------------------+
                              |
+-----------------------------v------------------------------------+
|  Protocol drivers                                                |
|  NTCIP (src/ntcip) | ONVIF/stub | HTTP/TMDD stub | other         |
+-----------------------------+------------------------------------+
                              |
+-----------------------------v------------------------------------+
|  Device profiles + captures + MIB/API metadata                   |
+------------------------------------------------------------------+
```

## Package responsibilities

### `src/its/` -- shared platform (domain-agnostic)

| Module | Responsibility |
|--------|----------------|
| `profile.py` | `DeviceProfile` -- sanitized site/device pack model |
| `adapters.py` | `DomainAdapter` protocol -- read/status/act seams |
| `policies/base.py` | `Policy` protocol -- evaluate observations -> recommendations |
| `shadow.py` | `ShadowBus` -- record would-be actions without executing |
| `events.py` | Common event types for logging and replay |
| `registry.py` | In-process registry of adapters by domain + profile id |

### `src/ntcip/` -- NTCIP vertical (Manager-first)

Three layers (do not collapse):

1. **Protocol** -- `SnmpEngine` / `SnmpBackend` (async UDP, timeouts, auth errors)
2. **MIB / objects** -- `MibRegistry`, codecs (DateAndTime), OID -> domain
3. **Business** -- `NtcipManager` + adapters (`get_phase_status`, timing plan)

Signals (ASC 1202) are the first concrete vertical. VMS (1203), ESS/RWIS (1204),
and CCTV (1205) should reuse Layers 1-2 and add Layer 3 adapters -- not fork
the stack.

### Existing signal sim / GIS

`src/cli/`, layout engine, and map tooling remain the **proving ground** for
signal ideas. Prefer consuming `NtcipManager` / `DomainAdapter` snapshots over
duplicating phase logic in the UI.

## Core types (contracts)

### DeviceProfile

Minimal fields every profile must support:

- `profile_id`, `domain`, `display_name`
- `protocol` (`ntcip`, `onvif`, `http`, `mqtt`, `mock`)
- `endpoint` (host/URL pattern; no secrets)
- `identity` (unit id, site code, corridor)
- `capabilities` (list of supported intents)
- `mib_or_api_revision` (string pin)
- `notes` / `quirks`

Stored as YAML/JSON under `profiles/`. Loaded into `DeviceProfile`.

### DomainAdapter

```text
async def probe(profile) -> Health
async def get_status(profile) -> DomainStatus
async def recommend(profile, intent) -> Recommendation   # no side effects
async def apply(profile, intent, *, dry_run=True) -> Result
```

Default `dry_run=True`. Live writes require explicit opt-in at the call site.

### Policy

```text
async def observe(adapter, profile) -> Observation
async def evaluate(observation) -> list[Recommendation]
```

Policies never open sockets directly; they only use adapters.

### ShadowBus

Append-only recommendations:

- timestamp, profile_id, policy_id, intent, reason, payload
- used for ops review and regression fixtures

## Domain expansion pattern (copy this)

When adding VMS / RWIS / CCTV:

1. Add `domains/<name>/README.md` (standards, intents, safety notes)
2. Add `profiles/examples/<name>_demo.yaml`
3. Implement `src/its/domains/<name>_adapter.py` (stub first)
4. If NTCIP: add MIB object module under `src/ntcip/mib/objects/`
5. Add playbook + one test that uses the stub
6. Register adapter in the ITS registry

## Safety boundaries

| Zone | Allowed |
|------|---------|
| `profiles/`, `captures/`, `playbooks/` | Sanitized only |
| `src/its`, `src/ntcip` | No hardcoded credentials |
| `airport_lab/` | Synthetic identities and fake APIs only |
| Live write paths | Behind `dry_run=False` + explicit credentials from env |

## What must not happen

- Business/policy code importing pysnmp or ONVIF client types directly
- OIDs copied into CLI scripts outside Layer 2/3 adapters
- Airport or PACS credentials committed to the repo
- Collapsing NTCIP layers "for speed" in feature branches that merge to main

## Test strategy

| Layer | Test style |
|-------|------------|
| Platform contracts | Unit tests on profile load, shadow bus, policy evaluate |
| NTCIP | Stub backend + DateAndTime / registry / manager tests |
| Domains | Adapter stub tests per domain |
| Captures | Replay fixtures (later) against stub drivers |

See `tests/its/` and `tests/ntcip/`.
