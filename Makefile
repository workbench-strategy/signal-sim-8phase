# Developer automation and workflow
.PHONY: install install-dev lint format test clean build run docs precommit

install:
	poetry install --no-root

install-dev:
	poetry install

lint:
	flake8 src tests && mypy src

format:
	isort src tests && black src tests

precommit:
	pre-commit run --all-files

test:
	pytest --cov=src --cov-report=term-missing

clean:
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov build dist *.egg-info

build:
	python -m build

run:
	python src/cli/main.py --name "Make User"

docs:
	$(MAKE) -C docs html
