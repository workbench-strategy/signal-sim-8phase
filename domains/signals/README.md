# Domain: Signals (ASC)

- **Standards:** NTCIP 1201 (global), NTCIP 1202 (ASC)
- **Adapter:** `its.domains.signals_adapter.SignalsNtcipAdapter`
- **Stack:** `src/ntcip/` Layers 1-3
- **Demo profile:** `profiles/examples/signals_demo.json`

## Intents

| Intent | Mode |
|--------|------|
| get_phase_status | read |
| get_unit_identity | read |
| set_timing_plan | write (dry-run default) |

## Expand next

- Pattern/split tables with DB transactions
- Detector status
- Hook `src/cli` layout states to adapter snapshots
