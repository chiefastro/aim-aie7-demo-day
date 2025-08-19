.PHONY: start-all start-otto start-street start-newicks stop-all install docker-build docker-run docker-stop

# Install dependencies using uv
install:
	uv sync

# Start all agents
start-all:
	@echo "Starting all restaurant agents..."
	@echo "OTTO Portland Agent: http://localhost:4001"
	@echo "Street Exeter Agent: http://localhost:4002"
	@echo "Newick's Lobster Agent: http://localhost:4003"
	@echo ""
	@echo "Press Ctrl+C to stop all agents"
	@trap 'kill %1 %2 %3' SIGINT; \
	uv run python -m restaurant_agents.otto_portland & \
	uv run python -m restaurant_agents.street_exeter & \
	uv run python -m restaurant_agents.newicks_lobster & \
	wait

# Start individual agents
start-otto:
	uv run python -m restaurant_agents.otto_portland

start-street:
	uv run python -m restaurant_agents.street_exeter

start-newicks:
	uv run python -m restaurant_agents.newicks_lobster

# Stop all agents (if running in background)
stop-all:
	pkill -f "restaurant_agents" || true

# Docker commands
docker-build:
	docker build -t restaurant-agents .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down
