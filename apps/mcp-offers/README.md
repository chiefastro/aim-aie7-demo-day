# MCP Offers Server

A Model Context Protocol (MCP) server that provides semantic search capabilities for the Agentic Commerce Protocol (ACP) offers. This server wraps the Global Offer Registry (GOR) API and exposes it through standardized MCP tools.

## Features

- **Semantic Search**: Search offers using natural language queries
- **Geographic Search**: Find offers near specific locations
- **Label Filtering**: Filter offers by tags and categories
- **Real-time Data**: Connects to live GOR API for up-to-date offer information

## MCP Tools

### `offers.search`
Search for offers using semantic query with optional geo and label filters.

**Parameters:**
- `query` (optional): Search query text (e.g., "pizza", "delivery near Boston")
- `lat` (optional): Latitude for geo search
- `lng` (optional): Longitude for geo search
- `radius_m` (optional): Search radius in meters (default: 50000)
- `labels` (optional): Labels to filter by (e.g., ["pizza", "delivery"])
- `limit` (optional): Maximum number of results (default: 20)

**Example:**
```json
{
  "query": "pizza delivery",
  "lat": 42.3601,
  "lng": -71.0589,
  "radius_m": 25000,
  "labels": ["pizza", "delivery"]
}
```

### `offers.getById`
Get a specific offer by its ID.

**Parameters:**
- `offer_id` (required): Offer ID to retrieve

**Example:**
```json
{
  "offer_id": "ofr_001"
}
```

### `offers.nearby`
Find offers near a specific location.

**Parameters:**
- `lat` (required): Latitude for geo search
- `lng` (required): Longitude for geo search
- `radius_m` (optional): Search radius in meters (default: 50000)
- `limit` (optional): Maximum number of results (default: 20)

**Example:**
```json
{
  "lat": 42.3601,
  "lng": -71.0589,
  "radius_m": 10000
}
```

## Quick Start

> **Note**: This MCP server runs directly on your host machine (not in Docker). Make sure you have the GOR API running in Docker first.

### Prerequisites
- Python 3.9+
- GOR API running on `http://localhost:3001` (start with `make up` from project root)
- `uv` package manager

### Installation

1. **Install dependencies:**
   ```bash
   cd apps/mcp-offers
   uv sync
   ```

2. **Run the server:**
   ```bash
   uv run python -m mcp_offers
   ```

### Configuration

The server can be configured using environment variables:

```bash
# GOR API configuration
export GOR_BASE_URL="http://localhost:3001"

# MCP Server configuration
export MCP_HOST="localhost"
export MCP_PORT="3002"

# Search defaults
export DEFAULT_SEARCH_RADIUS_M="50000"
export DEFAULT_SEARCH_LIMIT="20"

# Logging
export LOG_LEVEL="INFO"
```

Or create a `.env` file in the project root:

```env
GOR_BASE_URL=http://localhost:3001
MCP_HOST=localhost
MCP_PORT=3002
DEFAULT_SEARCH_RADIUS_M=50000
DEFAULT_SEARCH_LIMIT=20
LOG_LEVEL=INFO
```

## Development

### Available Commands

```bash
make help          # Show available commands
make install       # Install production dependencies
make install-dev   # Install development dependencies
make dev           # Run in development mode
make test          # Run tests
make lint          # Run linting
make format        # Format code
make clean         # Clean up generated files
```

### Project Structure

```
src/mcp_offers/
├── __init__.py          # Package initialization
├── __main__.py          # CLI entry point
├── config.py            # Configuration management
├── models.py            # Data models
├── gor_client.py        # GOR API client
└── server.py            # MCP server implementation
```

## Integration

This MCP server is designed to work with:

1. **GOR API**: The Global Offer Registry that indexes ACP offers
2. **Consumer Agents**: AI agents that use MCP tools to discover offers
3. **ACP Ecosystem**: The broader Agentic Commerce Protocol infrastructure

## Example Usage

### Consumer Agent Integration

A consumer agent can use this MCP server to:

1. **Discover offers** using natural language queries
2. **Find nearby restaurants** based on location
3. **Get detailed offer information** for decision making
4. **Filter offers** by cuisine type, delivery options, etc.

### Sample Agent Workflow

```python
# Agent discovers pizza offers near Boston
offers = await mcp.call_tool("offers.search", {
    "query": "pizza",
    "lat": 42.3601,
    "lng": -71.0589,
    "radius_m": 25000,
    "labels": ["pizza", "delivery"]
})

# Agent gets details for a specific offer
offer_details = await mcp.call_tool("offers.getById", {
    "offer_id": "ofr_001"
})

# Agent finds all offers in a specific area
nearby_offers = await mcp.call_tool("offers.nearby", {
    "lat": 42.3601,
    "lng": -71.0589,
    "radius_m": 10000
})
```

## Testing

Run the test suite:

```bash
make test
```

Or run specific tests:

```bash
uv run pytest tests/ -v
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting: `make check`
5. Submit a pull request

## License

This project is part of the ACP Demo and follows the same licensing terms.
