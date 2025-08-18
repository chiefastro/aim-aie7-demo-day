.PHONY: help install dev install-dev run test clean lint format

help: ## Show this help message
	@echo "MCP Offers Server - Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	uv sync --no-dev

install-dev: ## Install development dependencies
	uv sync

dev: install-dev ## Install dev dependencies and run in development mode
	uv run python -m mcp_offers

run: ## Run the MCP server
	uv run python -m mcp_offers

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

publish: ## Publish to PyPI (if configured)
	uv publish
