# Simple Makefile for developer convenience
# Usage: make <target>

DOCKER_REPO ?= ghcr.io/your-org/ai-dev
PNPM ?= pnpm
PY ?= python

.PHONY: install dev ui-build api-build build docker-build docker-build-ui compose-up compose-down test lint wheel ci-check

install:
	@echo "Installing JS dependencies (pnpm workspaces)"
	$(PNPM) -w install

dev:
	@echo "Starting both services via turbo"
	$(PNPM) dev

ui-build:
	@echo "Building UI"
	$(PNPM) --filter portal-ui... build

api-build:
	@echo "Building API (Docker or other configured build)"
	$(PNPM) --filter portal-python... build

build: ui-build api-build
	@echo "Built UI and API"

docker-build:
	@echo "Building backend image (local tag)"
	docker build -t $(DOCKER_REPO)/portal-python:local ./apps/portal-python

docker-build-ui:
	@echo "Building UI image (local tag)"
	docker build -t $(DOCKER_REPO)/portal-ui:local ./apps/portal-ui

compose-up:
	@echo "Starting docker-compose dev"
	docker compose -f docker-compose.dev.yml up --build

compose-down:
	@echo "Stopping docker-compose dev"
	docker compose -f docker-compose.dev.yml down

test:
	@echo "Running Python tests"
	cd apps/portal-python && $(PY) -m pytest -q

lint:
	@echo "Running frontend & backend linters"
	$(PNPM) --filter portal-ui... lint
	cd apps/portal-python && $(PY) -m ruff check .

wheel:
	@echo "Build Python wheel"
	cd apps/portal-python && $(PY) -m build --wheel --no-isolation

ci-check: install lint test wheel
	@echo "CI pre-checks complete"
