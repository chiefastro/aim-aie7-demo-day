.PHONY: help build up down logs clean test demo setup

help: ## Show this help message
	@echo "ACP Demo - Available commands:"
	@echo ""
	@echo "🚀 Quick Start Commands:"
	@echo "  make up          - Start complete ACP demo stack (all services)"
	@echo "  make start       - Build and start complete demo stack"
	@echo "  make down        - Stop all services"
	@echo ""
	@echo "🧪 Testing Commands:"
	@echo "  make status-all   - Show detailed status of all services"
	@echo ""
	@echo "📋 All Available Commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Docker operations
build: ## Build all Docker images
	docker-compose build

up: ## Start the complete ACP demo stack (GOR + Qdrant + Transaction Simulator + Mock Restaurants + Restaurant Agents + Demo Server)
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## Show logs for all services
	docker-compose logs -f

clean: ## Clean up Docker containers, images, and volumes
	docker-compose down -v --rmi all
	docker system prune -f
	# remove all uv.lock files
	find . -name "uv.lock" -type f -delete
	# remove all .venv directories
	find . -name ".venv" -type d -exec rm -rf {} +

# Demo profiles
setup: ## Start setup services (offer scraper + data generation)
	docker-compose --profile setup up -d

demo: ## Start complete demo stack
	docker-compose --profile setup up -d

# Development
dev: ## Start development stack with volume mounts
	docker-compose --profile setup up -d

# Status
status: ## Show status of all services
	docker-compose ps

status-all: ## Show detailed status of all services with health checks
	@echo "🏥 ACP Demo Service Status:"
	@echo ""
	@echo "📊 Core Services:"
	@echo "  Qdrant: $(shell curl -s http://localhost:6333/health 2>/dev/null | jq -r '.status' 2>/dev/null || echo '❌ unavailable')"
	@echo "  GOR API: $(shell curl -s http://localhost:3001/health 2>/dev/null | jq -r '.status' 2>/dev/null || echo '❌ unavailable')"
	@echo ""
	@echo "💰 Transaction Services:"
	@echo "  ACP Transaction Simulator: $(shell curl -s http://localhost:3003/health 2>/dev/null | jq -r '.status' 2>/dev/null || echo '❌ unavailable')"
	@echo ""
	@echo "🍕 Mock Restaurants:"
	@echo "  OTTO Portland: $(shell curl -s http://localhost:8001/health 2>/dev/null | jq -r '.status' 2>/dev/null || echo '❌ unavailable')"
	@echo "  Street Exeter: $(shell curl -s http://localhost:8002/health 2>/dev/null | jq -r '.status' 2>/dev/null || echo '❌ unavailable')"
	@echo "  Newick's Lobster: $(shell curl -s http://localhost:8003/health 2>/dev/null | jq -r '.status' 2>/dev/null || echo '❌ unavailable')"
	@echo ""
	@echo "🤖 Restaurant Agents:"
	@echo "  OTTO Agent: $(shell curl -s http://localhost:4001/.well-known/agent.json 2>/dev/null | jq -r '.status' 2>/dev/null || echo '❌ unavailable')"
	@echo "  Street Agent: $(shell curl -s http://localhost:4002/.well-known/agent.json 2>/dev/null | jq -r '.status' 2>/dev/null || echo '❌ unavailable')"
	@echo "  Newick's Agent: $(shell curl -s http://localhost:4003/.well-known/agent.json 2>/dev/null | jq -r '.status' 2>/dev/null || echo '❌ unavailable')"
	@echo ""
	@echo "🌐 Demo Server:"
	@echo "  Offer Scraper: $(shell curl -s http://localhost:3000/demo 2>/dev/null | jq -r '.status' 2>/dev/null || echo '❌ unavailable')"

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
	@echo "ACP Transaction Simulator: $(shell curl -s http://localhost:3003/health | jq -r '.status' 2>/dev/null || echo 'unavailable')"
	@echo "OTTO Portland: $(shell curl -s http://localhost:8001/health 2>/dev/null | jq -r '.status' 2>/dev/null || echo 'unavailable')"
	@echo "Street Exeter: $(shell curl -s http://localhost:8002/health 2>/dev/null | jq -r '.status' 2>/dev/null || echo 'unavailable')"
	@echo "Newick's Lobster: $(shell curl -s http://localhost:8003/health 2>/dev/null | jq -r '.status' 2>/dev/null || echo 'unavailable')"
	@echo "OTTO Agent: $(shell curl -s http://localhost:4001/health | jq -r '.status' 2>/dev/null || echo 'unavailable')"
	@echo "Street Agent: $(shell curl -s http://localhost:4002/health | jq -r '.status' 2>/dev/null || echo 'unavailable')"
	@echo "Newick's Agent: $(shell curl -s http://localhost:4003/health | jq -r '.status' 2>/dev/null || echo 'unavailable')"

# Quick start
start: ## Quick start - build and run complete ACP demo stack
	@echo "🚀 Starting Complete ACP Demo..."
	make build
	make up
	@echo "✅ Complete ACP demo stack started!"
	@echo "📊 GOR API: http://localhost:3001"
	@echo "🗄️  Qdrant: http://localhost:6333"
	@echo "💰 ACP Transaction Simulator: http://localhost:3003"
	@echo "🍕 Mock Restaurants: http://localhost:8001-8003"
	@echo "🤖 Restaurant Agents: http://localhost:4001-4003"
	@echo "🌐 Demo Server: http://localhost:3000"

# Individual service management
gor: ## Start only GOR API and Qdrant
	docker-compose up -d qdrant gor-api

# Mock Restaurant Servers (Day 4)
restaurants: ## Start all mock restaurant servers
	docker-compose up -d otto-portland toast-street-exeter newicks-lobster-house

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
ingest: ## Trigger offer ingestion in GOR
	@echo "🔄 Waiting for GOR API to be healthy..."
	@until curl -s -f http://localhost:3001/health > /dev/null 2>&1; do \
		echo "⏳ GOR API not ready yet, waiting 5 seconds..."; \
		sleep 5; \
	done
	@echo "✅ GOR API is healthy, proceeding with ingestion..."
	curl -X POST http://localhost:3001/ingest

scrape: ## Run restaurant data scraping
	docker-compose run --rm offer-scraper npm run batch-scrape

generate: ## Generate ACP documents from scraped data
	docker-compose run --rm offer-scraper npm run generate

# Reset
reset: ## Reset everything and start fresh
	@echo "🔄 Resetting ACP Demo..."
	make clean
	make start
	make ingest
	@echo "✅ Fresh start completed!"
