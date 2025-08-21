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

# Copy ACP SDK first
COPY apps/acp-sdk/ ./acp-sdk/

# Install dependencies (create lock file if it doesn't exist)
RUN uv sync

# Copy shared code
COPY apps/restaurant-agents/shared/ ./shared/

# Copy restaurant agents code
COPY apps/restaurant-agents/restaurant_agents/ ./restaurant_agents/

# Copy environment file
COPY apps/restaurant-agents/.env ./

# Expose ports
EXPOSE 4001 4002 4003

# Default command (will be overridden by docker-compose)
CMD ["uv", "run", "python", "-m", "restaurant_agents.otto_portland"]
