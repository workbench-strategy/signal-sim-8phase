# START HERE -- ITS Systems Lab

You are looking at a **personal Intelligent Transportation Systems (ITS) lab**:
a place to learn standards, replicate field systems, and innovate safely.

If you are returning after time away, read in this order:

1. This file (5 minutes)
2. [`docs/ITS_LAB_STRATEGY.md`](docs/ITS_LAB_STRATEGY.md) -- mission, domains, rules
3. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) -- locked platform seams
4. [`docs/ntcip_architecture.md`](docs/ntcip_architecture.md) -- NTCIP vertical (signals first)
5. [`docs/ROADMAP.md`](docs/ROADMAP.md) -- what to do next

## What this repo is (and is not)

| Is | Is not |
|----|--------|
| Multi-domain ITS workbench (VMS, RWIS, CCTV, signals, data stations, tunnel, airport sandbox) | A single-vendor ATMS product |
| Standards-true drivers + device profiles | A place for prod secrets / badge data |
| Shadow-first experimentation | Unsupervised write access to field devices |

## One promotion path (always)

```
capture -> model -> simulate -> shadow -> field
```

Never skip straight from idea to SET/write on a live device.

## Where code lives

| Path | Purpose |
|------|---------|
| `src/its/` | Shared platform: profiles, adapter protocols, policies, shadow log |
| `src/ntcip/` | NTCIP Manager stack (Layer 1-3); first vertical = ASC signals |
| `src/cli/` | Existing signal layout / sim CLI |
| `profiles/` | Sanitized device/site packs (replicate field reality) |
| `captures/` | Anonymized protocol traces for tests and learning |
| `playbooks/` | Ops-language how-tos you wrote after real work |
| `domains/` | Per-asset notes and adapter stubs (vms, rwis, cctv, ...) |
| `policies/` | Experiments and algorithms (fast-moving) |
| `airport_lab/` | Sandbox-only learning for airport security concepts |
| `mibs/` | NTCIP SMI modules (revision-pinned) |

## Quick commands

```bash
# NTCIP Manager demo (stub ASC phase status)
PYTHONPATH=src python -m ntcip

# Signal layout / cycle sim (existing)
python src/cli/main.py layout --states

# Platform + NTCIP tests
PYTHONPATH=src python -m pytest -v tests/its tests/ntcip
```

## Returning after a field touch?

1. Add or update a file under `playbooks/`
2. Add or update a sanitized entry under `profiles/`
3. If you captured traffic, drop an anonymized fixture in `captures/`
4. Only then open `policies/` for an experiment
