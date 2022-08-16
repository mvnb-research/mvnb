.PHONY: format
format:
	hatch run format

.PHONY: check
check:
	hatch run check

.PHONY: clean
clean:
	hatch env prune
	find . -type f -name '*.py[co]' -delete
	find . -type d -name __pycache__ -delete
	rm -rf .coverage coverage.xml
	rm -rf .parcel-cache
	rm -rf .pytest_cache
	rm -rf .vscode
	rm -rf *.egg-info
	rm -rf dist
	rm -rf node_modules

.PHONY: vscode
vscode:
	hatch run vscode
