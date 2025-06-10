# Project Overview and Best Practices

This document outlines the foundational philosophy and technical best practices for building modular Python repositories.

## Philosophy

- **Fast iteration without sacrificing quality**
- **Clear boundaries between modules**
- **Keep configuration declarative where possible**

## Expert-Level Best Practices

- Use `src/` layout to prevent import ambiguity
- Prefer `pyproject.toml` for unified configuration
- Embrace static typing with `mypy`
- Automate all formatting, linting, and testing with `pre-commit` and CI
- Mirror source layout in tests
- Use `.env.example` for safe env propagation
- Add Docker and GCP compatibility for scale and deployment

This repo structure is built for projects that scale: from Raspberry Pi apps to full GCP deployments, all in one clean and maintainable scaffold.
