# Consumer Agent CLI

An interactive command-line interface that demonstrates how AI agents can use the Model Context Protocol (MCP) to discover and interact with ACP offers. This CLI simulates a consumer agent that leverages MCP tools to search for restaurant offers, get detailed information, and make intelligent decisions.

## Features

- **Interactive CLI**: Beautiful, user-friendly command-line interface built with Rich
- **MCP Integration**: Demonstrates MCP tool usage for offer discovery
- **Semantic Search**: Search offers using natural language queries
- **Geographic Search**: Find offers near specific locations
- **Demo Workflow**: Complete end-to-end ACP workflow demonstration
- **Session Management**: Track and display session information

## Quick Start

### Prerequisites
- Python 3.9+
- MCP Offers server running (see `apps/mcp-offers/`)
- `uv` package manager

### Installation

1. **Install dependencies:**
   ```bash
   cd apps/consumer-agent-cli
   uv sync
   ```

2. **Run the CLI:**
   ```bash
   uv run python -m consumer_agent
   ```

### Demo Mode

For a quick demonstration with default settings:

```bash
make demo
```

## Usage

### Main Menu

The CLI provides an interactive menu with the following options:

1. **🔍 Search for offers** - Search using semantic queries with optional geo filters
2. **📍 Find nearby offers** - Discover offers near a specific location
3. **📋 Get offer details** - Retrieve detailed information about a specific offer
4. **🎯 Demo workflow** - Run a complete ACP workflow demonstration
5. **📊 Show session info** - Display current session information
6. **🚪 Exit** - Close the application

### Search for Offers

Search for offers using natural language queries:

```
🔍 Search for Offers
Enter search query: pizza
Include location search? (y/n): y
Latitude: 42.3601
Longitude: -71.0589
Radius (meters): 50000
Filter by labels? (y/n): y
Enter labels (comma-separated): pizza,delivery
Maximum results: 10
```

### Find Nearby Offers

Discover offers in a specific geographic area:

```
📍 Find Nearby Offers
Latitude: 42.3601
Longitude: -71.0589
Radius (meters): 25000
Maximum results: 10
```

### Get Offer Details

Retrieve comprehensive information about a specific offer:

```
📋 Get Offer Details
Enter offer ID: ofr_001
```

### Demo Workflow

The demo workflow demonstrates a complete ACP interaction:

1. **Search for pizza offers** near Boston
2. **Get detailed information** about a selected offer
3. **Show AI agent decision process** and reasoning
4. **Display next steps** in the ACP workflow

## Configuration

The CLI can be configured using environment variables:

```bash
# MCP Server configuration
export MCP_HOST="localhost"
export MCP_PORT="3002"

# GOR API configuration
export GOR_BASE_URL="http://localhost:3001"

# Search defaults
export DEFAULT_SEARCH_RADIUS_M="50000"
export DEFAULT_SEARCH_LIMIT="10"

# Demo defaults
export DEMO_LAT="42.3601"
export DEMO_LNG="-71.0589"
export DEMO_RADIUS_M="50000"

# Logging
export LOG_LEVEL="INFO"
```

Or create a `.env` file in the project root:

```env
MCP_HOST=localhost
MCP_PORT=3002
GOR_BASE_URL=http://localhost:3001
DEFAULT_SEARCH_RADIUS_M=50000
DEFAULT_SEARCH_LIMIT=10
DEMO_LAT=42.3601
DEMO_LNG=-71.0589
DEMO_RADIUS_M=50000
LOG_LEVEL=INFO
```

## Command Line Options

```bash
# Basic usage
python -m consumer_agent

# Custom MCP server
python -m consumer_agent --host localhost --port 3002

# Enable debug mode
python -m consumer_agent --debug

# Show help
python -m consumer_agent --help
```

## Development

### Available Commands

```bash
make help          # Show available commands
make install       # Install production dependencies
make install-dev   # Install development dependencies
make dev           # Run in development mode
make demo          # Run with demo defaults
make test          # Run tests
make lint          # Run linting
make format        # Format code
make clean         # Clean up generated files
```

### Project Structure

```
src/consumer_agent/
├── __init__.py          # Package initialization
├── __main__.py          # CLI entry point
├── config.py            # Configuration management
├── mcp_client.py        # MCP client implementation
└── cli.py               # Main CLI interface
```

## MCP Integration

This CLI demonstrates how AI agents can use MCP tools to:

1. **Discover offers** using semantic search
2. **Filter results** by location, labels, and other criteria
3. **Get detailed information** for decision making
4. **Make intelligent choices** based on offer data

### MCP Tools Used

- `offers.search` - Semantic search with geo and label filters
- `offers.getById` - Retrieve specific offer details
- `offers.nearby` - Location-based offer discovery

## Example Workflow

### 1. Agent Discovers Offers

```python
# Agent searches for pizza offers near Boston
offers = await mcp.call_tool("offers.search", {
    "query": "pizza",
    "lat": 42.3601,
    "lng": -71.0589,
    "radius_m": 50000,
    "labels": ["pizza", "delivery"]
})
```

### 2. Agent Analyzes Results

```python
# Agent gets details for a specific offer
offer_details = await mcp.call_tool("offers.getById", {
    "offer_id": "ofr_001"
})
```

### 3. Agent Makes Decision

The agent evaluates offers based on:
- **Relevance** to user query
- **Geographic proximity** to user location
- **Bounty amount** and revenue potential
- **Merchant reputation** and reliability
- **Offer validity** and terms

### 4. Agent Takes Action

Based on the analysis, the agent:
1. **Presents the offer** to the user
2. **Initiates checkout** process
3. **Handles order confirmation**
4. **Processes attribution receipt**

## Mock Data

For demonstration purposes, the CLI includes mock data that simulates:

- **Real restaurant offers** from the ACP demo
- **Geographic coordinates** for New Hampshire restaurants
- **Bounty amounts** and revenue splits
- **Merchant information** and locations
- **Offer terms** and validity periods

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

## Next Steps

This CLI demonstrates the **semantic layer** of ACP. The next phases will include:

- **Restaurant Agents** (Day 4) - A2A endpoints for order processing
- **Transaction Simulator** (Day 5) - Attribution receipts and settlement
- **End-to-End Integration** (Day 6) - Complete ACP workflow
- **Hardening & Documentation** (Day 7) - Production readiness
