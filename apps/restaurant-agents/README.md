# Restaurant Agents (LangGraph)

This directory contains LangGraph-based restaurant agents that handle user interactions and execute transactions via A2A (Agent-to-Agent) protocols.

## Architecture

Each restaurant agent is a LangGraph agent that:
- **Discovers offers** from the restaurant's OSF endpoint
- **Interacts with users** to gather order details
- **Executes transactions** via A2A endpoints
- **Manages order state** through the complete lifecycle

## A2A Protocol Implementation

### Agent Discovery
- **AgentCard**: `/.well-known/agent.json` - Describes agent capabilities and endpoints
- **A2A Envelope**: Standardized message format with authentication
- **Well-known endpoints**: Standardized location for agent discovery

### A2A Endpoints
- `POST /a2a/present_offer` - Present offer details and constraints
- `POST /a2a/initiate_checkout` - Start checkout process
- `POST /a2a/confirm_order` - Confirm and finalize order

### Order State Machine
1. **DISCOVERED** - Offer discovered from OSF
2. **PRESENTED** - Offer presented to user
3. **INTENT** - User expresses buying intent
4. **CREATED** - Order created in restaurant system
5. **CONFIRMED** - Order confirmed by restaurant
6. **SETTLED** - Payment processed and order completed

## Restaurants

1. **OTTO Portland Agent** (Port 4001) - Italian pizza restaurant
2. **Street Exeter Agent** (Port 4002) - International fusion restaurant
3. **Newick's Lobster House Agent** (Port 4003) - Seafood restaurant

## Running the Agents

### Local Development
```bash
# Install dependencies
make install

# Start all agents
make start-all

# Or start individually
make start-otto
make start-street
make start-newicks
```

### Docker Deployment
```bash
# Build and start all agents
make docker-run

# Stop all agents
make docker-stop
```

## Agent Configuration

Each agent is configured with:
- **Restaurant ID**: Unique identifier for the restaurant
- **OSF Endpoint**: URL to the restaurant's OSF feed
- **A2A Endpoints**: URLs for A2A communication
- **Menu Data**: Restaurant menu and pricing
- **Agent Capabilities**: What the agent can do

## Integration Points

- **GOR API**: For offer discovery and validation
- **Mock Restaurant Servers**: For transaction execution
- **Transaction Simulator**: For settlement and receipts
- **Consumer Agents**: For user interaction and intent capture
