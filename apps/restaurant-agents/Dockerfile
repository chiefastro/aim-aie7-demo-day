FROM python:3.11-slim

# Set Python version explicitly for uv
ENV PYTHON_VERSION=3.11

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy pyproject.toml
COPY apps/restaurant-agents/pyproject.toml ./

# Copy ACP SDK
COPY apps/acp-sdk/ ./acp-sdk/

# Install dependencies (create lock file if it doesn't exist)
RUN uv sync

# Install ACP SDK in development mode
RUN cd acp-sdk && uv pip install -e .

# Copy restaurant agents code
COPY apps/restaurant-agents/restaurant_agents/ ./restaurant_agents/

# Copy test files
COPY apps/restaurant-agents/test_*.py ./

# Copy environment file (if it exists)
COPY apps/restaurant-agents/.env* ./

# Expose ports
EXPOSE 4001 4002 4003

# Default command (will be overridden by docker-compose)
CMD ["uv", "run", "python", "-m", "restaurant_agents.a2a_server", "--restaurant-id", "otto_portland", "--port", "4001"]
