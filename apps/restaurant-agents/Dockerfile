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
COPY pyproject.toml ./

# Install dependencies (create lock file if it doesn't exist)
RUN uv sync

# Copy shared code
COPY shared/ ./shared/

# Copy restaurant agents code
COPY restaurant_agents/ ./restaurant_agents/

# Copy environment file
COPY .env ./

# Expose ports
EXPOSE 4001 4002 4003

# Default command (will be overridden by docker-compose)
CMD ["uv", "run", "python", "-m", "restaurant_agents.otto_portland"]
