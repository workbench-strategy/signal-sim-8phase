# signal-sim-8phase

8-phase NEMA dual-ring traffic signal controller demo (terminal). Python replicates ring/barrier logic, timing steps, and cabinet output energization traceable to WSDOT standard plans.

## Quick start

```bash
cd signal-sim-8phase
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt pytest

# Presenter demo (auto-step, ~0.8s per tick)
python src/cli/main.py run

# Animated traffic-signal cycle view
python src/cli/main.py animate

# Export a true 2D animated intersection view to HTML
python src/cli/main.py animate2d --output signal-sim-8phase-2d.html

# Manual advance one second at a time
python src/cli/main.py reset
python src/cli/main.py step

# Status and wiring only
python src/cli/main.py status
python src/cli/main.py wiring
```

## Demo commands

| Command | Purpose |
| -------- | -------- |
| `run` | Auto-step full timing plan with intersection + wiring panels |
| `animate` | Same controller loop, presented as an animated traffic-signal cycle |
| `animate2d` | Export a 2D animated intersection as standalone HTML |
| `step` | Advance one tick; state saved in `.controller_demo_state.json` |
| `status` | Ring positions, barriers, step label |
| `wiring` | Energized cabinet outputs with WSDOT refs |
| `wiring-summary` | Grouped first-layer wiring metadata by phase, approach, and head type |
| `layout` | Static ASCII intersection (`--states` for sample colors) |
| `reset` | Clear saved step session |
| `simulate` | Full plan with no sleep (CI / tests) |

Options: `run --no-sleep`, `run --interval 1.5`, `--config path/to/wsdot_8phase.json`

## First-layer wiring model

Each wiring channel in `data/wsdot_8phase.json` carries these first-layer fields:

| Field | Purpose |
| -------- | -------- |
| `phase` | NEMA phase number (1–8) |
| `indication` | green, yellow, or red |
| `head_type` | ball (through) or arrow (protected left) |
| `leg` | north, south, east, or west |
| `approach` | NB, SB, EB, or WB |
| `movement_group` | through or left |
| `street_role` | major or minor |
| `wsdot_ref` | traceability to WSDOT standard plan or DM 1330 |

Inspect the grouped metadata with:

```bash
python src/cli/main.py wiring-summary
```

The 2D animation (`animate2d`) renders ball vs arrow heads and groups signal heads by approach using these fields.

## Configuration

Single source of truth: [data/wsdot_8phase.json](data/wsdot_8phase.json)

- Intersection legs (north 1+6, south 3+8, east 2+7, west 5+4)
- NEMA dual-ring: ring 1 (1-4), ring 2 (5-8), barriers 2\|3 and 6\|7
- Demo timing plan (green / yellow / all-red per step)
- Wiring channels (placeholder OUT-01..OUT-24; transcribe from PDFs)

Traceability: [docs/wsdot_mapping.md](docs/wsdot_mapping.md)  
WSDOT PDFs: [docs/WSDOT_Std_plans/](docs/WSDOT_Std_plans/)

## WSDOT DM 1330 phasing (docs/1330.pdf)

North-south **major** street, phase **2** = northbound through.

**Sum rule:** on each approach, through + left = **7** (major) or **11** (minor).

| Approach | Through | Left | Sum |
| -------- | ------- | ---- | --- |
| NB | 2 | 5 | 7 |
| SB | 6 | 1 | 7 |
| WB | 4 | 7 | 11 |
| EB | 8 | 3 | 11 |

Approach pairs (prot/perm, preemption): [2,5], [1,6], [4,7], [3,8]

Example layout:

```text
               [5: NB Left]  [2: NB Thru]
[7: WB Left]  [4: WB Thru]    [3: EB Left]  [8: EB Thru]
               [1: SB Left]  [6: SB Thru]
```

## Project layout

| Path | Role |
| ---- | ---- |
| `src/controller/` | Dual-ring validation, timing plan runner |
| `src/wiring/` | Cabinet output energization |
| `src/display/` | ASCII intersection + demo frame |
| `src/data/loader.py` | Load wsdot_8phase.json |
| `src/cli/main.py` | CLI entry point |
| `scripts/signal_sim_engine.py` | Compatibility shim |

## Tests

```bash
pytest -vv
```

## Legacy

[data/traffic-signals.json](data/traffic-signals.json) is superseded by `data/wsdot_8phase.json` for the controller demo.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)
