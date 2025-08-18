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
RUN uv sync --no-dev

# Set environment variables for demo
ENV MCP_HOST=mcp-offers
ENV MCP_PORT=3002
ENV GOR_BASE_URL=http://gor-api:3001

# Run the consumer agent CLI
CMD ["uv", "run", "python", "-m", "consumer_agent"]
