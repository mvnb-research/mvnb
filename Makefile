PYTHON := python3

DOCKER := docker

NPM := npm

override srcs = mvnb test setup.py

override venv = .venv

override yarn = .yarn

export PATH := $(CURDIR)/$(yarn)/node_modules/.bin:$(PATH)

.PHONY: setup
setup: $(venv)/bin/mvnb vscode

.PHONY: format
format: black isort

.PHONY: check
check: lint coverage

.PHONY: lint
lint: black-check isort-check flake8

.PHONY: black
black: $(venv)/bin/black
	$(venv)/bin/black -q $(srcs)

.PHONY: isort
isort: $(venv)/bin/isort
	$(venv)/bin/isort $(srcs)

.PHONY: black-check
black-check: $(venv)/bin/black
	$(venv)/bin/black -q --check $(srcs)

.PHONY: isort-check
isort-check: $(venv)/bin/isort
	$(venv)/bin/isort -c $(srcs)

.PHONY: flake8
flake8: $(venv)/bin/flake8
	$(venv)/bin/flake8 $(srcs)

.PHONY: test
test: $(venv)/bin/pytest $(venv)/bin/mvnb
	$(venv)/bin/pytest

.PHONY: coverage
coverage: $(venv)/bin/pytest $(venv)/bin/mvnb
	$(venv)/bin/pytest --cov --cov-report=term --cov-report=xml

.PHONY: build
build: $(yarn)/node_modules/.bin/yarn $(venv)/bin/pyproject-build
	$(venv)/bin/pyproject-build

.PHONY: build-docker
build-docker:
	$(DOCKER) build -t mvnb .

.PHONY: vscode
vscode: .vscode/settings.json

# clean tasks -----------------------------------------------------------------
.PHONY: clean
clean: $(shell grep -o '^clean-[^:]*' Makefile)

.PHONY: clean-venv
clean-venv:
	rm -rf .venv .yarn

.PHONY: clean-pyc
clean-pyc:
	find . -type f -name '*.py[co]' -delete
	find . -type d -name __pycache__ -delete

.PHONY: clean-gui
clean-gui:
	rm -rf mvnb-gui/.parcel-cache mvnb-gui/node_modules
	rm -rf mvnb/gui

.PHONY: clean-test
clean-test:
	rm -rf .pytest_cache

.PHONY: clean-coverage
clean-coverage: clean-test
	rm -rf .coverage coverage.xml

.PHONY: clean-build
clean-build: clean-gui
	rm -rf dist mvnb.egg-info

.PHONY: clean-vscode
clean-vscode:
	rm -rf .vscode

# venv creation ---------------------------------------------------------------
$(venv)/bin/python $(venv)/bin/pip:
	$(PYTHON) -m venv $(venv) --clear --upgrade-deps

$(venv)/bin/mvnb: $(yarn)/node_modules/.bin/yarn $(venv)/bin/pip
	$(venv)/bin/pip install -e .

# builder installation --------------------------------------------------------
$(yarn)/node_modules/.bin/yarn:
	mkdir -p $(yarn)
	echo '{}' > $(yarn)/package.json
	cd $(yarn) && $(NPM) install --no-package-lock yarn

$(venv)/bin/pyproject-build: $(venv)/bin/pip
	$(venv)/bin/pip install -I build

# checker installation --------------------------------------------------------
$(venv)/bin/black: $(venv)/bin/pip
	$(venv)/bin/pip install -I black

$(venv)/bin/isort: $(venv)/bin/pip
	$(venv)/bin/pip install -I isort

$(venv)/bin/flake8: $(venv)/bin/pip
	$(venv)/bin/pip install -I flake8 flake8-black flake8-tidy-imports

$(venv)/bin/pytest: $(venv)/bin/pip
	$(venv)/bin/pip install -I pytest pytest-asyncio pytest-timeout pytest-cov

# editor setting generation ---------------------------------------------------
.vscode/settings.json:
	mkdir -p .vscode
	echo '{'                                                         > .vscode/settings.json
	echo '  "coverage-gutters.showLineCoverage": true,'             >> .vscode/settings.json
	echo '  "python.linting.flake8Enabled": true,'                  >> .vscode/settings.json
	echo '  "python.testing.pytestEnabled": true,'                  >> .vscode/settings.json
	echo '  "python.defaultInterpreterPath": "$(venv)/bin/python",' >> .vscode/settings.json
	echo '}'                                                        >> .vscode/settings.json
