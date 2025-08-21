# Restaurant A2A Setup Guide

This guide explains how to set up and run the restaurant agents with A2A (Agent-to-Agent) protocol support, along with an MCP (Model Context Protocol) client that can communicate with these agents.

## Architecture Overview

The system consists of three main components:

1. **Mock Restaurant Servers** (`apps/mock-restaurants/`): Web servers that simulate restaurant backends with OSF and A2A endpoints
2. **Restaurant A2A Agents** (`apps/restaurant-agents/`): A2A protocol servers that wrap restaurant agent logic
3. **MCP Restaurant Client** (`apps/mcp-restaurant-client/`): MCP server that wraps an A2A client for Cursor integration

## Quick Start

### 1. Start Mock Restaurant Servers

```bash
cd apps/mock-restaurants
make start-all
```

This starts three mock restaurant servers:
- OTTO Portland: http://localhost:8001
- Street Exeter: http://localhost:8002  
- Newick's Lobster House: http://localhost:8003

### 2. Start Restaurant A2A Agents

```bash
cd apps/restaurant-agents
make install
make start-a2a-all
```

This starts three A2A agents:
- OTTO Portland A2A Agent: http://localhost:4001
- Street Exeter A2A Agent: http://localhost:4002
- Newick's Lobster A2A Agent: http://localhost:4003

### 3. Start MCP Restaurant Client

```bash
cd apps/mcp-restaurant-client
make install
make run
```

This starts the MCP server that can communicate with the A2A agents.

## Detailed Setup

### Mock Restaurant Servers

The mock restaurant servers provide:
- OSF (Open Source Food) endpoints at `/.well-known/osf.json`
- A2A protocol endpoints for offer presentation, checkout, and order confirmation
- Menu and order management functionality

**Endpoints:**
- `GET /.well-known/osf.json` - Restaurant offers
- `POST /a2a/present_offer` - Present offers via A2A
- `POST /a2a/initiate_checkout` - Start checkout process
- `POST /a2a/confirm_order` - Confirm orders
- `GET /a2a/menu` - Restaurant menu

### Restaurant A2A Agents

The A2A agents provide:
- A2A protocol compliance with agent discovery
- Integration with restaurant agent logic
- Well-known endpoint at `/.well-known/agents.json`

**Key Files:**
- `a2a_server.py` - Main A2A server implementation
- `a2a_executor.py` - A2A protocol executor
- `config.py` - Restaurant configurations
- `shared/agent_template.py` - Restaurant agent logic

**A2A Endpoints:**
- `GET /.well-known/agents.json` - Agent discovery
- `POST /tasks` - Create A2A tasks
- `GET /tasks/{task_id}` - Get task status
- `GET /tasks/{task_id}/artifacts` - Get task results

### MCP Restaurant Client

The MCP client provides:
- MCP protocol compliance for Cursor integration
- A2A client functionality wrapped in MCP tools
- Restaurant interaction tools

**Available Tools:**
1. `discover_restaurant` - Discover restaurant information
2. `present_offer` - Present restaurant offers
3. `initiate_checkout` - Start checkout process
4. `confirm_order` - Confirm orders
5. `validate_offer` - Validate offer applicability
6. `chat_with_restaurant` - Chat with restaurant agents

## Configuration

### Restaurant Configurations

Each restaurant has a configuration in `apps/restaurant-agents/restaurant_agents/config.py`:

```python
"otto_portland": RestaurantConfig(
    restaurant_id="otto_portland",
    name="OTTO Portland",
    description="Italian pizza restaurant serving authentic Neapolitan-style pizzas",
    osf_endpoint="http://localhost:8001/.well-known/osf.json",
    a2a_endpoints={...},
    menu_endpoint="http://localhost:8001/a2a/menu",
    well_known_endpoint="http://localhost:4001/.well-known/agents.json",
    agent_capabilities=[...],
    default_policies={...}
)
```

### MCP Client Configuration

The MCP client can be configured via command line:

```bash
python -m mcp_restaurant_client \
  --host localhost \
  --port 3000 \
  --a2a-server-url http://localhost:4001
```

## Integration with Cursor

To integrate with Cursor, add the following to your Cursor configuration:

```json
{
  "mcpServers": {
    "restaurant-client": {
      "command": "python",
      "args": [
        "-m", 
        "mcp_restaurant_client", 
        "--a2a-server-url", 
        "http://localhost:4001"
      ]
    }
  }
}
```

## Testing

### Test Mock Restaurants

```bash
cd apps/mock-restaurants
python test_restaurants.py
```

### Test A2A Agents

```bash
cd apps/restaurant-agents
# Start an A2A agent
make start-a2a-otto

# In another terminal, test the agent
curl http://localhost:4001/.well-known/agents.json
```

### Test MCP Client

```bash
cd apps/mcp-restaurant-client
python test_mcp_client.py
```

## Development

### Adding New Restaurants

1. Add restaurant configuration to `config.py`
2. Create restaurant-specific agent file (optional)
3. Update mock restaurant server
4. Add to Makefile targets

### Adding New A2A Capabilities

1. Add capability to `AgentCapability` enum in `shared/models.py`
2. Update `a2a_executor.py` to handle the capability
3. Add corresponding method in `a2a_client.py`
4. Add MCP tool definition in `server.py`

### Adding New MCP Tools

1. Add tool definition in `server.py` `handle_list_tools()`
2. Add tool handler in `server.py` `handle_call_tool()`
3. Add corresponding method in `a2a_client.py`

## Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 8001-8003 and 4001-4003 are available
2. **Dependencies**: Run `make install` in each directory
3. **A2A server not responding**: Check if mock restaurants are running
4. **MCP client errors**: Verify A2A server URL is correct

### Logs

- Mock restaurants: Check terminal output
- A2A agents: Check terminal output with logging
- MCP client: Check terminal output with logging

### Health Checks

```bash
# Check mock restaurants
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health

# Check A2A agents
curl http://localhost:4001/.well-known/agents.json
curl http://localhost:4002/.well-known/agents.json
curl http://localhost:4003/.well-known/agents.json
```

## Example Workflow

1. **Discover Restaurant**: Use MCP tool to discover OTTO Portland
2. **Present Offer**: Show available offers from the restaurant
3. **Initiate Checkout**: Start ordering process with selected items
4. **Confirm Order**: Finalize the order
5. **Chat**: Interact with restaurant agent for questions

This creates a complete A2A-enabled restaurant ordering system that can be accessed through Cursor via the MCP protocol.
