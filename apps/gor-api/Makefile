.PHONY: help dev test clean up down build logs ingest shell run

# Default target
help:
	@echo "GOR API Development Commands"
	@echo "============================"
	@echo ""
	@echo "Local Development:"
	@echo "  dev         Start development server"
	@echo "  test        Run tests"
	@echo "  clean       Clean up generated files"
	@echo ""
	@echo "Docker Commands:"
	@echo "  up   Start Qdrant and GOR API with Docker Compose"
	@echo "  down Stop and remove Docker containers"
	@echo "  build Build GOR API Docker image"
	@echo "  logs Show Docker container logs"
	@echo ""
	@echo "Data Management:"
	@echo "  ingest      Ingest offers from demo server"
	@echo ""
	@echo "Container Commands:"
	@echo "  shell       Open shell in GOR API container"
	@echo "  run         Run arbitrary command in container"
	@echo ""

# Start development server
dev:
	@echo "🚀 Starting development server..."
	@echo "📡 Starting GOR API in development mode..."
	docker-compose up gor-api

# Run tests
test:
	@echo "🧪 Running tests..."
	@echo "🧪 Running tests in Docker container..."
	docker-compose run --rm gor-api uv run python -m pytest tests/ -v

# Clean up
clean:
	@echo "🧹 Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf .coverage
	@echo "✅ Cleanup complete"

# Docker commands
up:
	@echo "🐳 Starting services with Docker Compose..."
	@if ! command -v docker &> /dev/null; then \
		echo "❌ Docker is not installed or not in PATH"; \
		exit 1; \
	fi
	@if ! docker info &> /dev/null; then \
		echo "❌ Docker daemon is not running. Please start Docker first."; \
		exit 1; \
	fi
	docker-compose up -d
	@echo "✅ Services started. GOR API available at http://localhost:3001"

down:
	@echo "🐳 Stopping Docker services..."
	docker-compose down
	@echo "✅ Services stopped"

build:
	@echo "🔨 Building Docker image..."
	docker-compose build gor-api
	@echo "✅ Docker image built"

logs:
	@echo "📋 Showing Docker logs..."
	docker-compose logs -f

# Ingest offers
ingest:
	@echo "🔄 Ingesting offers from demo server..."
	@echo "🔄 Running ingestion in Docker container..."
	docker-compose run --rm gor-api uv run python ingest_offers.py

# Container shell access
shell:
	@echo "🐚 Opening shell in GOR API container..."
	docker-compose run --rm gor-api /bin/bash

# Run arbitrary command in container
run:
	@echo "🚀 Running command in GOR API container..."
	@if [ -z "$(CMD)" ]; then \
		echo "❌ Usage: make run CMD='your command here'"; \
		echo "   Example: make run CMD='uv run python -c \"print(\\\"Hello\\\")\"'"; \
		exit 1; \
	fi
	docker-compose run --rm gor-api $(CMD)
