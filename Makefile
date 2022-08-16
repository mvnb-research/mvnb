.PHONY: format
format:
	hatch run format

.PHONY: check
check:
	hatch run check

.PHONY: clean
clean:
	find . -type f -name '*.py[co]' -delete
	find . -type d -name __pycache__ -delete
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .coverage coverage.xml
	rm -rf .vscode
	hatch env prune

.PHONY: vscode
vscode:
	hatch run vscode
