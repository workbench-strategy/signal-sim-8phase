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

## Intersection leg arrangement (example)

Run the example layout showing phases arranged by legs (1&6 north, 2&5 south, 3&8 east, 7&4 west):

```bash
python scripts/signal_sim_engine.py
```

Expected output format (ASCII layout):

```
      [1: Northbound Left (Protected)]  [6: Northbound Through]
[7: Westbound Through]  [4: Westbound Left (Protected)]      [3: Eastbound Left (Protected)]  [8: Eastbound Through]
      [2: Southbound Left (Protected)]  [5: Southbound Through]
```

## Contributing

See `CONTRIBUTING.md`

![Tests](https://github.com/user/repo/actions/workflows/main.yml/badge.svg)
![License](https://img.shields.io/github/license/user/repo.svg)