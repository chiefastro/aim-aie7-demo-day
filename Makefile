.PHONY: help build up down logs clean test demo setup

help: ## Show this help message
	@echo "ACP Demo - Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Docker operations
build: ## Build all Docker images
	docker-compose build

up: ## Start the core ACP demo stack (GOR + Qdrant)
	docker-compose up -d qdrant gor-api

down: ## Stop all services
	docker-compose down

logs: ## Show logs for all services
	docker-compose logs -f

clean: ## Clean up Docker containers, images, and volumes
	docker-compose down -v --rmi all
	docker system prune -f

# Demo profiles
setup: ## Start setup services (offer scraper + data generation)
	docker-compose --profile setup up -d

demo: ## Start complete demo stack
	docker-compose --profile setup up -d

# Development
dev: ## Start development stack with volume mounts
	docker-compose --profile setup up -d

# Testing
test: ## Run tests for all components
	@echo "🧪 Testing MCP Server..."
	@cd apps/mcp-offers && if command -v python3 >/dev/null 2>&1; then \
		python3 test_mcp_server.py; \
	elif command -v python >/dev/null 2>&1; then \
		python test_mcp_server.py; \
	elif command -v uv >/dev/null 2>&1; then \
		uv run python test_mcp_server.py; \
	else \
		echo "❌ No Python interpreter found in mcp-offers"; \
		exit 1; \
	fi

test-docker: ## Test Docker setup and service health
	@echo "🧪 Testing Docker setup..."
	@if command -v python3 >/dev/null 2>&1 && python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null; then \
		python3 test_docker_setup.py; \
	elif command -v python >/dev/null 2>&1 && python -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null; then \
		python test_docker_setup.py; \
	elif command -v uv >/dev/null 2>&1; then \
		echo "⚠️  Python 3.10+ required for MCP. Using shell script fallback..."; \
		./test_docker_setup.sh; \
	else \
		echo "⚠️  No Python 3.10+ interpreter found, using shell script fallback..."; \
		./test_docker_setup.sh; \
	fi

test-docker-shell: ## Test Docker setup using shell script only
	./test_docker_setup.sh

check-python: ## Check available Python interpreters
	@echo "🐍 Checking available Python interpreters..."
	@if command -v python3 >/dev/null 2>&1; then \
		echo "  ✅ python3: $(python3 --version)"; \
		if python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null; then \
			echo "     ✅ Version 3.10+ (compatible with MCP)"; \
		else \
			echo "     ❌ Version < 3.10 (incompatible with MCP)"; \
		fi; \
	else \
		echo "  ❌ python3: not found"; \
	fi
	@if command -v python >/dev/null 2>&1; then \
		echo "  ✅ python: $(python --version)"; \
		if python -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null; then \
			echo "     ✅ Version 3.10+ (compatible with MCP)"; \
		else \
			echo "     ❌ Version < 3.10 (incompatible with MCP)"; \
		fi; \
	else \
		echo "  ❌ python: not found"; \
	fi
	@if command -v uv >/dev/null 2>&1; then \
		echo "  ✅ uv: $(uv --version)"; \
		echo "     ℹ️  Can manage Python environments"; \
	fi
	@echo ""
	@echo "💡 Note: MCP package requires Python 3.10+"
	@echo "   Use Docker containers to avoid version conflicts: make start"

# Status
status: ## Show status of all services
	docker-compose ps

health: ## Check health of all services
	@echo "🏥 Checking service health..."
	@echo "Qdrant: $(shell curl -s http://localhost:6333/health | jq -r '.status' 2>/dev/null || echo 'unavailable')"
	@echo "GOR API: $(shell curl -s http://localhost:3001/health | jq -r '.status' 2>/dev/null || echo 'unavailable')"
	@echo "MCP Server: $(shell curl -s http://localhost:3002/health 2>/dev/null | jq -r '.status' 2>/dev/null || echo 'unavailable (run manually: cd apps/mcp-offers && make run)')"

# Quick start
start: ## Quick start - build and run core stack
	@echo "🚀 Starting ACP Demo..."
	make build
	make up
	@echo "✅ Core stack started!"
	@echo "📊 GOR API: http://localhost:3001"
	@echo "🔧 MCP Server: http://localhost:3002 (run manually: cd apps/mcp-offers && make run)"
	@echo "🗄️  Qdrant: http://localhost:6333"

# Demo workflow
workflow: ## Run complete demo workflow
	@echo "🎯 Running ACP Demo Workflow..."
	@echo "1. Starting core services..."
	make start
	@echo "2. Waiting for services to be ready..."
	sleep 30
	@echo "3. MCP server ready for manual start: cd apps/mcp-offers && make run"

# Individual service management
gor: ## Start only GOR API and Qdrant
	docker-compose up -d qdrant gor-api

mcp: ## Start MCP server (requires GOR to be running)
	@echo "🔧 Starting MCP server manually..."
	@cd apps/mcp-offers && make run

# Data management
ingest: ## Trigger offer ingestion in GOR
	curl -X POST http://localhost:3001/ingest

scrape: ## Run restaurant data scraping
	docker-compose run --rm offer-scraper npm run batch-scrape

generate: ## Generate ACP documents from scraped data
	docker-compose run --rm offer-scraper npm run generate

# Monitoring
monitor: ## Monitor all services with logs
	docker-compose logs -f --tail=100

# Reset
reset: ## Reset everything and start fresh
	@echo "🔄 Resetting ACP Demo..."
	make clean
	make start
	@echo "✅ Fresh start completed!"
