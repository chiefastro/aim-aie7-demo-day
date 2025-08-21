.PHONY: start-all start-otto start-street start-newicks stop-all install docker-build docker-run docker-stop start-a2a-all start-a2a-otto start-a2a-street start-a2a-newicks

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

# Test A2A integration
test-a2a:
	uv run python test_a2a_integration.py

# Start A2A servers
start-a2a-all:
	@echo "Starting all A2A restaurant agents..."
	@echo "OTTO Portland A2A Agent: http://localhost:4001"
	@echo "Street Exeter A2A Agent: http://localhost:4002"
	@echo "Newick's Lobster A2A Agent: http://localhost:4003"
	@echo ""
	@echo "Press Ctrl+C to stop all A2A agents"
	@trap 'kill %1 %2 %3' SIGINT; \
	uv run python -m restaurant_agents.a2a_server --restaurant-id otto_portland --port 4001 & \
	uv run python -m restaurant_agents.a2a_server --restaurant-id street_exeter --port 4002 & \
	uv run python -m restaurant_agents.a2a_server --restaurant-id newicks_lobster --port 4003 & \
	wait

# Start individual A2A agents
start-a2a-otto:
	uv run python -m restaurant_agents.a2a_server --restaurant-id otto_portland --port 4001

start-a2a-street:
	uv run python -m restaurant_agents.a2a_server --restaurant-id street_exeter --port 4002

start-a2a-newicks:
	uv run python -m restaurant_agents.a2a_server --restaurant-id newicks_lobster --port 4003

# Docker commands
docker-build:
	docker build -t restaurant-agents .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down
