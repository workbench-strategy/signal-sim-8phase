# Dependency Management

## Canonical Source: pyproject.toml

Use `pyproject.toml` to define:

- Project name, version, authors
- Dependencies (and dev-dependencies)
- Tool configs (`black`, `mypy`, `isort`...)

## Docker/CI Compatibility

Generate requirements:
```bash
poetry export -f requirements.txt --without-hashes > requirements.txt
```

## Syncing

To avoid drift:
- Lock dependencies locally (`poetry.lock`)
- Export for CI (`requirements.txt`)
- Use `Makefile` targets:
```makefile
requirements.txt: pyproject.toml
	poetry export -f requirements.txt --without-hashes > requirements.txt
```
