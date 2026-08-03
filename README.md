# ITS Systems Lab

Personal workbench to **learn, replicate, and innovate** across Intelligent
Transportation Systems -- CCTV, data stations, RWIS, VMS, signals, tunnel
crossovers, plus a sandboxed airport learning area.

**Returning to this repo?** Open [`START_HERE.md`](START_HERE.md) first.

| Doc | Why |
|-----|-----|
| [`START_HERE.md`](START_HERE.md) | 5-minute re-entry |
| [`docs/ITS_LAB_STRATEGY.md`](docs/ITS_LAB_STRATEGY.md) | Mission, domains, rules |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Locked platform seams |
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | Ordered next steps |

## Quick demos

```bash
# ITS platform shadow demo (signals adapter + policy)
PYTHONPATH=src python -m its

# NTCIP Manager GET phase status (stub ASC)
PYTHONPATH=src python -m ntcip

# Existing 8-phase layout / sim CLI
python src/cli/main.py layout --states
python src/cli/main.py simulate

# Tests (verbose)
PYTHONPATH=src python -m pytest -v tests/its tests/ntcip
```

## Layout

| Path | Role |
|------|------|
| `src/its/` | Shared platform: profiles, adapters, policies, shadow bus |
| `src/ntcip/` | NTCIP Manager stack (protocol / MIB / business) |
| `src/cli/` | Signal layout and cycle simulation |
| `profiles/` | Sanitized device packs |
| `captures/` | Anonymized traces |
| `playbooks/` | Ops-language runbooks |
| `domains/` | Per-asset notes (vms, rwis, cctv, tunnel, ...) |
| `airport_lab/` | Airport security learning -- synthetic only |
| `mibs/` | NTCIP SMI snippets |

## Promotion path

```
capture -> model -> simulate -> shadow -> field
```

Policies default to **shadow / dry-run**. No production secrets in git.
Airport work stays in `airport_lab/` until you have explicit authority.

## Signal layout (legacy CLI)

Phases by intersection leg:

- North: 1 (left), 6 (through)
- South: 2 (left), 5 (through)
- East: 3 (left), 8 (through)
- West: 7 (through), 4 (left)

```bash
python src/cli/main.py layout --full
python src/cli/main.py layout --states
python src/cli/main.py demo
```

## Contributing

See `CONTRIBUTING.md`. Prefer playbooks + profiles after field work; keep
drivers boring and experiments in policies.
