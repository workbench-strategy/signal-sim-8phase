# Code Style and Linting

Consistency is king. Use the following tools:

## Formatters

- **Black**: Code formatter (`black src tests`)
- **isort**: Import sorter (`isort src tests`)

## Linters

- **flake8**: Code linting (`flake8 src tests`)
- **mypy**: Type checker (`mypy src`)

## Integration with Pre-Commit

Use `.pre-commit-config.yaml` to enforce standards before every commit.

Install and run:
```bash
pip install pre-commit
pre-commit run --all-files
```

Configure line lengths, ignores, and strictness in `pyproject.toml` or `.flake8`, `mypy.ini`.
