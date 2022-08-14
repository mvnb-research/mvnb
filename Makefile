PYTHON := python3

override src = mvnb

override venv = venv

override bin = $(venv)/bin

override pip = $(bin)/pip

override python = $(bin)/python

override installed = $(venv)/.installed

# -----------------------------------------------------------------------------
.PHONY: setup
setup: install

.PHONY: setup-dev
setup-dev: setup $(bin)/flake8 vscode

.PHONY: check
check: isort black flake8 coverage

.PHONY: format
format: isort-apply black-apply

.PHONY: clean
clean: $(shell grep -o '^clean-[^:]*' Makefile)
	rm -rf $(venv)

.PHONY: clean-pyc
clean-pyc:
	find . -type f -name '*.py[co]' -delete
	find . -type d -name __pycache__ -delete

# install ---------------------------------------------------------------------
.PHONY: install
install: $(installed)

.PHONY: clean-install
clean-install:
	rm -rf $(installed) build *.egg-info

$(installed): $(pip)
	$< install -e . && touch $@

$(pip): $(python)
	curl -sfS https://bootstrap.pypa.io/get-pip.py | $<

$(python):
	$(PYTHON) -m venv $(venv) --without-pip

# test/coverage ---------------------------------------------------------------
.PHONY: test
test: $(bin)/pytest $(installed)
	$<

.PHONY: coverage
coverage: $(bin)/pytest $(installed)
	$< --cov $(src) --cov-report=term --cov-report=html --cov-report=xml

.PHONY: clean-test
clean-test:
	rm -rf .pytest_cache

.PHONY: clean-coverage
clean-coverage:
	rm -rf .coverage coverage.xml htmlcov

$(bin)/pytest: $(pip)
	$< install pytest-cov pytest-asyncio pytest-timeout

# flake8 ----------------------------------------------------------------------
.PHONY: flake8
flake8: $(bin)/flake8 $(installed)
	$< setup.py $(src) test

$(bin)/flake8: $(pip)
	$< install flake8 flake8-black flake8-tidy-imports

# black -----------------------------------------------------------------------
.PHONY: black
black: $(bin)/black $(installed)
	$< --quiet --check setup.py $(src) test

.PHONY: black-apply
black-apply: $(bin)/black $(installed)
	$< --quiet setup.py $(src) test

$(bin)/black: $(pip)
	$< install black

# isort -----------------------------------------------------------------------
.PHONY: isort
isort: $(bin)/isort $(installed)
	$< --check-only setup.py $(src) test

.PHONY: isort-apply
isort-apply: $(bin)/isort $(installed)
	$< setup.py $(src) test

$(bin)/isort: $(pip)
	$< install isort

# vscode ----------------------------------------------------------------------
.PHONY: vscode
vscode: .vscode/.gitignore .vscode/settings.json

.PHONY: clean-vscode
clean-vscode:
	rm -rf .vscode

.vscode:
	mkdir -p $@

.vscode/.gitignore: | .vscode
	echo '*' > $@

.vscode/settings.json: | .vscode
	echo '{' > $@
	echo '  "python.linting.flake8Enabled": true,' >> $@
	echo '  "python.defaultInterpreterPath": "$(python)",' >> $@
	echo '  "explorer.excludeGitIgnore": true' >> $@
	echo '}' >> $@
