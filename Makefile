.PHONY: format
format:
	hatch run format
	yarn install && yarn prettier --write mvnb-gui

.PHONY: check
check:
	hatch run check
	yarn install && yarn prettier --check mvnb-gui

.PHONY: docker
docker:
	docker build -t mvnb .

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
	find mvnb/gui ! -name '.gitignore' -type f -exec rm -f {} +

.PHONY: vscode
vscode:
	hatch run vscode
