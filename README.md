# GIS-Based Location Map with Traffic Signal Nodes

Modular Python repo for rapid experimentation.

## Features

- Visualize traffic signal nodes on a map
- Integrate real-time data from APIs
- Save and load traffic signal data from JSON files
- Modular design for easy extension

## Usage

```bash
poetry install
python src/cli/main.py
```

## Features

### Signal Indication Layout

The system displays traffic signal phases arranged by intersection legs in an ASCII cross-shaped layout:

```bash
# Show compact layout (fits 80-column terminal)
python src/cli/main.py layout

# Show full layout with complete descriptions
python src/cli/main.py layout --full

# Show layout with signal states (R=Red, Y=Yellow, G=Green)
python src/cli/main.py layout --states
```

### Signal Cycle Simulation

Run a simulation showing signal phase transitions:

```bash
python src/cli/main.py simulate
```

### Demo Mode

View all available layout demonstrations:

```bash
python src/cli/main.py demo
```

## Intersection Leg Arrangement

Phases are arranged by intersection legs:
- **North leg**: Phases 1 (left) & 6 (through)
- **South leg**: Phases 2 (left) & 5 (through)  
- **East leg**: Phases 3 (left) & 8 (through)
- **West leg**: Phases 7 (through) & 4 (left)

Example compact layout output:

```
                [1: NB Left]  [6: NB Thru]
[7: WB Thru]  [4: WB Left]      [3: EB Left]  [8: EB Thru]
                [2: SB Left]  [5: SB Thru]
```

With signal states:

```
                    [1: NB Left (G)]  [6: NB Thru (G)]
[7: WB Thru (R)]  [4: WB Left (R)]      [3: EB Left (R)]  [8: EB Thru (R)]
                    [2: SB Left (R)]  [5: SB Thru (R)]
```

## Contributing

See `CONTRIBUTING.md`

![Tests](https://github.com/user/repo/actions/workflows/main.yml/badge.svg)
![License](https://img.shields.io/github/license/user/repo.svg)