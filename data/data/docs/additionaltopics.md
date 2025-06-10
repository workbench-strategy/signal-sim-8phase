# 🧠 Expanded Best Practices Reference for Professional Python Projects

## 🔁 Version Control

* **Conventional Commits**: e.g., `feat: add patch selector`, `fix: adjust tempo parser`
* **Branching Model**: Use GitHub Flow for simplicity or Git Flow for larger teams
* **PR Process**: Always include linked issue references and require reviewer approval

## 📚 Documentation

* **README.md**: Include badges (CI, coverage), architecture overview, setup, and examples
* **MkDocs/Sphinx**: Generate API documentation automatically from docstrings
* **Examples Folder**: Include real usage scripts with comments
* **Changelog**: Maintain a structured `CHANGELOG.md` using [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

## ✅ Testing

* **Unit + Integration Tests**: Use `pytest`, and organize by module structure
* **Fixtures**: Use `pytest.fixture(scope='module')` for setup/teardown reuse
* **Coverage Enforcement**: Add GitHub Actions checks that fail <90% coverage

## 🧼 Code Quality

* **Black + isort**: Auto-formatting and import sorting
* **Mypy**: Static type checking with `--strict`
* **Pylint/Ruff**: Lightweight analysis for style and performance smells
* **EditorConfig**: Include `.editorconfig` for multi-IDE consistency

## 🧪 Dev Environments

* **Poetry**: Use `poetry.lock` to ensure consistent builds
* **.env / .env.example**: Manage config per environment, load via `python-dotenv`
* **`.vscode/` Folder**: Include launch configs and recommended extensions

## 📦 Dependency Management

* **Security Audits**: Run `pip-audit`, or enable GitHub Dependabot
* **Layered Requirements**: Separate `requirements.txt`, `requirements-dev.txt`, `requirements-prod.txt`

## 🐋 Docker and CI/CD

* **Multi-stage Dockerfiles**: Base on `python:3.11-slim` with poetry installed
* **docker-compose**: Use for local orchestration of services (Postgres, Redis, Pi MIDI simulator)
* **GitHub Actions**:

  * Lint, format, test on push/PR
  * Publish documentation via `mkdocs gh-deploy`
  * Optional deploy to GCP/AWS

## 🔐 Security

* **Secrets**: Use `dotenv`, GitHub Secrets, or GCP Secret Manager
* **Pre-Commit Hook**: Use `detect-secrets` to scan diffs
* **Dependency Check**: Scan for CVEs using Snyk or `safety`

## 🤝 Collaboration & Scaling

* **Code of Conduct**: Use the Contributor Covenant v2
* **CONTRIBUTING.md**: Include setup guide, lint/test commands, PR template
* **Issue Templates**: Use `.github/ISSUE_TEMPLATE/*.yml` for bug reports/feature requests
* **Discussion Board**: Enable GitHub Discussions for feature ideation

## 🧩 Modular Design Principles

* **Single Responsibility**: One module = one purpose (e.g. `tempo.py`, `filter.py`)
* **Contracts First**: Define your expected JSON/YAML schemas first and code to validate them
* **Interface Decoupling**: Treat I/O and processing layers as separable (middleware model)
* **Agent-Based Scripts**: Use `agent_*.py` naming for AI-compatible tools

## 🎯 LLM Prompt Engineering for Coding Agents

* **Provide agent with `.md` docs**: Attach architecture and routing reference
* **Use structured pre-prompts**: See `coder_agent_preprompts.md`
* **Inject runtime config**: e.g., current part assignments, key signature, routing state
* **Use `.json` examples**: Always give 1–2 working examples for schema output

Let me know if you'd like these split into separate markdowns per topic or auto-generated into a MkDocs site.
