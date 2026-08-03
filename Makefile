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
	PYTHONPATH=src python -m pytest -v --tb=short tests

test-cov:
	PYTHONPATH=src python -m pytest -v --tb=short --cov=src --cov-report=term-missing tests

test-ntcip:
	PYTHONPATH=src python -m pytest -v --tb=long tests/ntcip

test-its:
	PYTHONPATH=src python -m pytest -v --tb=long tests/its

test-lab:
	PYTHONPATH=src python -m pytest -v --tb=long tests/its tests/ntcip

clean:
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov build dist *.egg-info

build:
	python -m build

run:
	python src/cli/main.py --name "Make User"

docs:
	$(MAKE) -C docs html
