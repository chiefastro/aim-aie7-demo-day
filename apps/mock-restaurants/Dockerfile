FROM python:3.11-slim

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

# Copy restaurant data and code
COPY otto-portland/ ./otto-portland/
COPY toast-street-exeter/ ./toast-street-exeter/
COPY newicks-lobster-house/ ./newicks-lobster-house/

# Expose ports
EXPOSE 8001 8002 8003

# Default command (will be overridden by docker-compose)
CMD ["uv", "run", "python", "otto-portland/main.py"]
