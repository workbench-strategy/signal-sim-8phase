# Policies (experiments)

Fast-moving ideas. Implementations preferred under `src/its/policies/` so
they are importable and tested.

| Policy | Purpose |
|--------|---------|
| `phase_green_monitor` | Flag unexpected ASC greens (shadow recommend) |

New policy checklist:

1. Implement `Policy` protocol
2. Unit test with stub adapter
3. Default path records to `ShadowBus` only
4. Document in a playbook before any dry_run=False usage
