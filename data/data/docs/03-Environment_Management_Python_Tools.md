# Environment Management with Python Tools

Environment Setup

This guide explains how to set up a Python development environment for modular projects.

## Steps

1. **Install Python**:
   - Use Python 3.9+ for compatibility with modern libraries.
   - Install via [python.org](https://www.python.org/downloads/) or a package manager like `brew` (macOS) or `choco` (Windows).

2. **Create a Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate     # Windows
## Recommended Tool: Poetry

Poetry simplifies dependency and virtualenv management:
```bash
poetry init
poetry add requests
poetry shell
```

This generates:
- `pyproject.toml`: Modern config/dependencies
- `poetry.lock`: Exact versions for reproducibility

## Compatibility Tips

- Generate `requirements.txt` for Docker:
```bash
poetry export -f requirements.txt --without-hashes > requirements.txt
```

## Alternative: Hatch

Hatch supports similar workflows and additional environment profiles (dev/test/prod).

## Virtual Envs

Avoid polluting global Python:
- Use `.venv` locally
- Activate via Poetry or manually:
```bash
python -m venv .venv
source .venv/bin/activate
```
