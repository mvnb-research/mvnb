# Multiverse Notebook

A Notebook Environment for Safe and Efficient Exploration

## Build and run Multiverse Notebook

### With Docker

Requirement: Docker

```sh
# Build a docker image
docker build -t mvnb .

# Run Multiverse Notebook in a container
docker run --rm -p 8000:8000 -it mvnb

# Open http://localhost:8000 in your browser
```

### Without Docker

Requirements: Python3.10, NPM, Make

```sh
# Build Multiverse Notebook
make

# Run Multiverse Notebook
./.venv/bin/mvnb

# Open http://localhost:8000 in your browser
```

## Usage

![usage](./doc/mvnb-screenshot.png)

See also [this demo video](https://youtu.be/gNphOyG-o2Y)
