# Directory Structure Guide

This outlines each major directory and its intended contents.

## Root Structure

```
my_project/
├── src/              # All actual source code lives here
├── tests/            # Mirrors `src/`, contains unit/integration tests
├── notebooks/        # Optional: for data exploration, analysis
├── docker/           # Dockerfiles, one for dev, one for RPi if needed
├── gcp/              # Cloud Functions, Run, Terraform configs
├── rpi/              # Scripts & configs specific to Raspberry Pi deployments
├── scripts/          # General-purpose automation/deployment scripts
├── .vscode/          # Editor settings
├── .github/          # GitHub Actions workflows
```

## Inside `src/`

- `core/`: General logic shared across features
- `llm/`: LLM wrappers and interfaces
- `midi/`: MIDI processing tools
- `traffic/`: Traffic system simulators
- `cli/`: Command line interface utilities
