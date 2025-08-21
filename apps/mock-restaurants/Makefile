.PHONY: start-all start-otto start-toast start-newicks stop-all install docker-build docker-run docker-stop

# Install dependencies using uv
install:
	uv sync

# Start all servers
start-all:
	@echo "Starting all mock restaurant servers..."
	@echo "OTTO Portland: http://localhost:8001"
	@echo "Toast Street Exeter: http://localhost:8002"
	@echo "Newick's Lobster House: http://localhost:8003"
	@echo ""
	@echo "Press Ctrl+C to stop all servers"
	@trap 'kill %1 %2 %3' SIGINT; \
	cd otto-portland && uv run python main.py & \
	cd toast-street-exeter && uv run python main.py & \
	cd newicks-lobster-house && uv run python main.py & \
	wait

# Start individual servers
start-otto:
	cd otto-portland && uv run python main.py

start-toast:
	cd toast-street-exeter && uv run python main.py

start-newicks:
	cd newicks-lobster-house && uv run python main.py

# Stop all servers (if running in background)
stop-all:
	pkill -f "python main.py" || true

# Testing
test: ## Test all restaurant servers
	@echo "🧪 Testing mock restaurant servers..."
	@uv run python test_restaurants.py

# Docker commands
docker-build:
	docker build -t mock-restaurants .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down
