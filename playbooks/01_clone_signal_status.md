# Playbook: Clone signal phase status

- **Domain:** signals
- **Profile:** `profiles/examples/signals_demo.json`
- **Last field touch:** lab scaffold
- **Risk:** read-only

## Goal

Read ASC red/yellow/green status groups through the ITS adapter and NTCIP Manager
(stub backend offline; same path later against a real cabinet).

## Preconditions

- Repo checked out; `PYTHONPATH=src`
- Demo profile present

## Steps

```bash
# Platform shadow demo (policy + adapter)
PYTHONPATH=src python -m its

# Direct NTCIP Manager demo
PYTHONPATH=src python -m ntcip

# Signal layout view (existing sim CLI)
python src/cli/main.py layout --states
```

## Expected result

- Green phases `[2, 5]` from stub data
- Unit identity `ASC-DEMO-001` at Main St & 1st Ave
- Shadow demo may emit `operator_verify_intersection` if expected greens differ

## Captures / tests

- `tests/ntcip/business/test_manager.py`
- `tests/its/test_signals_adapter.py`

## Gotchas

- Do not hardcode OIDs in scripts; use `NtcipManager` / `SignalsNtcipAdapter`
- Live SNMP requires implementing `PysnmpBackend` and env-based credentials

## Next innovation idea (optional)

- Policy that compares stub/live greens to time-of-day plan expectations
