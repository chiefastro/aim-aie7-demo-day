.PHONY: help install dev test clean run

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	uv sync

dev: ## Install development dependencies
	uv sync --dev

test: ## Run tests
	pytest

clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +

run: ## Run the MCP server
	python -m mcp_restaurant_client --a2a-server-url http://localhost:4001

run-otto: ## Run the MCP server for OTTO Portland
	python -m mcp_restaurant_client --a2a-server-url http://localhost:4001

run-street: ## Run the MCP server for Street Exeter
	python -m mcp_restaurant_client --a2a-server-url http://localhost:4002

run-newicks: ## Run the MCP server for Newick's Lobster House
	python -m mcp_restaurant_client --a2a-server-url http://localhost:4003
