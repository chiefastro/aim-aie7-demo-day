FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml ./
COPY src/ ./src/

# Install uv and dependencies
RUN pip install uv
RUN uv sync --verbose

# Expose port
EXPOSE 3002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import asyncio; from mcp_offers.gor_client import GORClient; asyncio.run(GORClient().health_check())" || exit 1

# Run the MCP server
CMD ["uv", "run", "python", "-m", "mcp_offers"]
