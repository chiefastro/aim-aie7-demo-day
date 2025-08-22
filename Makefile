.PHONY: help build up down logs clean test demo setup

help: ## Show this help message
	@echo "ACP Demo - Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Docker operations
build: ## Build all Docker images
	docker-compose build

up: ## Start the core ACP demo stack (offer scraper)
	docker-compose up -d offer-scraper

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
	@echo "🧪 Testing ACP SDK..."
	@cd apps/acp-sdk && if command -v python3 >/dev/null 2>&1; then \
		python3 -m pytest; \
	elif command -v python >/dev/null 2>&1; then \
		python -m pytest; \
	elif command -v uv >/dev/null 2>&1; then \
		uv run pytest; \
	else \
		echo "❌ No Python interpreter found"; \
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

# Quick start commands
start: ## Start all services (GOR, MCP, mock restaurants, restaurant agents, transaction simulator)
	@echo "🚀 Starting all ACP demo services..."
	docker-compose up -d

start-agents: ## Start only restaurant agents
	@echo "🤖 Starting restaurant agents..."
	make agents

start-restaurants: ## Start only mock restaurants
	@echo "🍕 Starting mock restaurants..."
	make restaurants

health: ## Check health of all services
	@echo "🏥 Checking service health..."
	@echo "Qdrant: $(shell curl -s http://localhost:6333/health | jq -r '.status' 2>/dev/null || echo 'unavailable')"
	@echo "GOR API: $(shell curl -s http://localhost:3001/health | jq -r '.status' 2>/dev/null || echo 'unavailable')"
	@echo "Transaction Simulator: $(shell curl -s http://localhost:3003/health | jq -r '.status' 2>/dev/null || echo 'unavailable')"
	@echo "ACP Transaction Simulator: $(shell curl -s http://localhost:3004/health | jq -r '.status' 2>/dev/null || echo 'unavailable')"
	@echo "OTTO Portland: $(shell curl -s http://localhost:8001/health 2>/dev/null | jq -r '.status' 2>/dev/null || echo 'unavailable')"
	@echo "Street Exeter: $(shell curl -s http://localhost:8002/health 2>/dev/null | jq -r '.status' 2>/dev/null || echo 'unavailable')"
	@echo "Newick's Lobster: $(shell curl -s http://localhost:8003/health 2>/dev/null | jq -r '.status' 2>/dev/null || echo 'unavailable')"
	@echo "OTTO Agent: $(shell curl -s http://localhost:4001/health | jq -r '.status' 2>/dev/null || echo 'unavailable')"
	@echo "Street Agent: $(shell curl -s http://localhost:4002/health | jq -r '.status' 2>/dev/null || echo 'unavailable')"
	@echo "Newick's Agent: $(shell curl -s http://localhost:4003/health | jq -r '.status' 2>/dev/null || echo 'unavailable')"

# Quick start
start: ## Quick start - build and run core stack
	@echo "🚀 Starting ACP Demo..."
	make build
	make up
	@echo "✅ Core stack started!"
	@echo "📊 GOR API: http://localhost:3001"
	@echo "🗄️  Qdrant: http://localhost:6333"
	@echo "💰 Transaction Simulator: http://localhost:3003"
	@echo "💰 ACP Transaction Simulator: http://localhost:3004"
	@echo "🍕 Mock Restaurants: http://localhost:8001-8003 (run: make restaurants)"

# Demo workflow
workflow: ## Run complete demo workflow
	@echo "🎯 Running ACP Demo Workflow..."
	@echo "1. Starting core services..."
	make start
	@echo "2. Waiting for services to be ready..."
	sleep 30
	@echo "3. MCP server ready for manual start: cd apps/acp-sdk && uv run python -m acp_sdk.mcp.acp_mcp"

# Individual service management
gor: ## Start only offer scraper (legacy GOR functionality now in ACP SDK)
	docker-compose up -d offer-scraper

mcp: ## Start MCP server (requires offer scraper to be running)
	@echo "🔧 Starting MCP server manually..."
	@cd apps/acp-sdk && uv run python -m acp_sdk.mcp.acp_mcp

# Mock Restaurant Servers (Day 4)
restaurants: ## Start all mock restaurant servers
	docker-compose up -d otto-portland toast-street-exeter newicks-lobster-house

restaurants-local: ## Start mock restaurants locally (requires uv)
	@echo "🍕 Starting mock restaurants locally..."
	@cd apps/mock-restaurants && make start-all

restaurants-build: ## Build mock restaurant Docker images
	@echo "🏗️ Building mock restaurant images..."
	@cd apps/mock-restaurants && make docker-build

# Restaurant Agents (Day 4)
agents: ## Start all restaurant agents
	docker-compose up -d restaurant-agent-otto restaurant-agent-street restaurant-agent-newicks

agents-stop: ## Stop all restaurant agents
	docker-compose stop restaurant-agent-otto restaurant-agent-street restaurant-agent-newicks

agents-build: ## Build restaurant agent Docker images
	docker-compose build restaurant-agent-otto restaurant-agent-street restaurant-agent-newicks

agents-restart: ## Restart all restaurant agents
	docker-compose restart restaurant-agent-otto restaurant-agent-street restaurant-agent-newicks

agents-logs: ## Show logs for all restaurant agents
	docker-compose logs -f restaurant-agent-otto restaurant-agent-street restaurant-agent-newicks

agents-local: ## Start restaurant agents locally (requires uv)
	@echo "🤖 Starting restaurant agents locally..."
	@cd apps/restaurant-agents && make start-all

# Transaction Simulator (Day 5)
tx-simulator: ## Start Transaction Simulator
	docker-compose up -d tx-simulator

tx-simulator-stop: ## Stop Transaction Simulator
	docker-compose stop tx-simulator

tx-simulator-build: ## Build Transaction Simulator Docker image
	docker-compose build tx-simulator

tx-simulator-restart: ## Restart Transaction Simulator
	docker-compose restart tx-simulator

tx-simulator-logs: ## Show logs for Transaction Simulator
	docker-compose logs -f tx-simulator

tx-simulator-local: ## Start Transaction Simulator locally (requires uv)
	@echo "💰 Starting Transaction Simulator locally..."
	@cd apps/tx-simulator && uv run python -m src.tx_simulator.main

# ACP Transaction Simulator (Day 5)
txn-simulator-acp: ## Start ACP Transaction Simulator
	docker-compose up -d txn-simulator-acp

txn-simulator-acp-stop: ## Stop ACP Transaction Simulator
	docker-compose stop txn-simulator-acp

txn-simulator-acp-build: ## Build ACP Transaction Simulator Docker image
	docker-compose build txn-simulator-acp

txn-simulator-acp-restart: ## Restart ACP Transaction Simulator
	docker-compose restart txn-simulator-acp

txn-simulator-acp-logs: ## Show logs for ACP Transaction Simulator
	docker-compose logs -f txn-simulator-acp

txn-simulator-acp-local: ## Start ACP Transaction Simulator locally (requires uv)
	@echo "💰 Starting ACP Transaction Simulator locally..."
	@cd apps/txn-simulator-acp && uv run python -m src.txn_simulator_acp.main

txn-simulator-acp-test: ## Test ACP Transaction Simulator setup
	@echo "🧪 Testing ACP Transaction Simulator setup..."
	@cd apps/txn-simulator-acp && uv run python test_setup.py

# Data management
ingest: ## Trigger offer ingestion (now handled by ACP SDK)
	@echo "📥 Offer ingestion now handled by ACP SDK discovery module"

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
