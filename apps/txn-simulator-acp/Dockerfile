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
COPY apps/txn-simulator-acp/pyproject.toml ./

# Copy ACP SDK first
COPY apps/acp-sdk/ ./acp-sdk/

# Install dependencies (create lock file if it doesn't exist)
RUN uv sync

# Copy txn simulator code
COPY apps/txn-simulator-acp/src/ ./src/

# Copy test files
COPY apps/txn-simulator-acp/test_setup.py ./

# Expose port
EXPOSE 3003

# Default command (will be overridden by docker-compose)
CMD ["uv", "run", "uvicorn", "src.txn_simulator_acp.main:app", "--host", "0.0.0.0", "--port", "3003"]
