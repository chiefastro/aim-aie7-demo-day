.PHONY: help install dev install-dev run test clean lint format

help: ## Show this help message
	@echo "Consumer Agent CLI - Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	uv sync --no-dev

install-dev: ## Install development dependencies
	uv sync

dev: install-dev ## Install dev dependencies and run in development mode
	uv run python -m consumer_agent

run: ## Run the consumer agent CLI
	uv run python -m consumer_agent

demo: ## Run with demo defaults
	uv run python -m consumer_agent --host localhost --port 3002

test: ## Run tests
	uv run pytest

clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache

lint: ## Run linting
	uv run black --check src/
	uv run isort --check-only src/

format: ## Format code
	uv run black src/
	uv run isort src/

check: lint test ## Run linting and tests

build: ## Build the package
	uv build
