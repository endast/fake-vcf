#* Variables
SHELL := /usr/bin/env bash
PYTHON := python
PYTHONPATH := `pwd`

#* Poetry
.PHONY: poetry-download
poetry-download:
	curl -sSL https://install.python-poetry.org | $(PYTHON) -

.PHONY: poetry-remove
poetry-remove:
	curl -sSL https://install.python-poetry.org | $(PYTHON) - --uninstall

#* Installation
.PHONY: install
install:
	poetry lock -n && poetry export --without-hashes > requirements.txt
	poetry install -n

#* Installation
.PHONY: install-all
install-all:
	poetry lock -n && poetry export --without-hashes > requirements.txt
	poetry install -n --with bgzip

.PHONY: pre-commit-install
pre-commit-install:
	poetry run pre-commit install

#* Formatters
.PHONY: codestyle
codestyle:
	poetry run pyupgrade --exit-zero-even-if-changed --py38-plus **/*.py
	poetry run isort --settings-path pyproject.toml ./
	poetry run black --config pyproject.toml ./

.PHONY: formatting
formatting: codestyle

#* Linting
.PHONY: test
test:
	PYTHONPATH=$(PYTHONPATH) poetry run pytest -c pyproject.toml --random-order --cov-report=html --cov=fake_vcf tests/
	poetry run coverage-badge -o assets/images/coverage.svg -f

#* Linting
.PHONY: test-xdist
test-xdist:
	PYTHONPATH=$(PYTHONPATH) poetry run pytest -n auto --random-order -c pyproject.toml --cov-report=html --cov=fake_vcf tests/
	poetry run coverage-badge -o assets/images/coverage.svg -f


.PHONY: check-codestyle
check-codestyle:
	poetry run isort --diff --check-only --settings-path pyproject.toml ./
	poetry run black --diff --check --config pyproject.toml ./
	poetry run darglint --verbosity 2 fake_vcf tests

.PHONY: check-safety
check-safety:
	poetry check
	poetry run bandit -ll --recursive fake_vcf tests

.PHONY: lint
lint: test check-codestyle check-safety

.PHONY: update-dev-deps
update-dev-deps:
	poetry add  --group dev bandit@latest darglint@latest "isort[colors]@latest" pydocstyle@latest pylint@latest pytest@latest pyupgrade@latest safety@latest coverage@latest coverage-badge@latest pytest-html@latest pytest-cov@latest
	poetry add  --group dev black@latest

#* Cleaning
.PHONY: pycache-remove
pycache-remove:
	find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf

.PHONY: dsstore-remove
dsstore-remove:
	find . | grep -E ".DS_Store" | xargs rm -rf

.PHONY: ipynbcheckpoints-remove
ipynbcheckpoints-remove:
	find . | grep -E ".ipynb_checkpoints" | xargs rm -rf

.PHONY: pytestcache-remove
pytestcache-remove:
	find . | grep -E ".pytest_cache" | xargs rm -rf

.PHONY: build-remove
build-remove:
	rm -rf build/

.PHONY: cleanup
cleanup: pycache-remove dsstore-remove  ipynbcheckpoints-remove pytestcache-remove
