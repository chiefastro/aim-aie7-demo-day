# MCP Restaurant Client

An MCP (Model Context Protocol) server that wraps an A2A (Agent-to-Agent) client for restaurant interactions. This allows Cursor and other MCP clients to communicate with restaurant A2A servers to discover offers, initiate checkout, and complete orders.

## Features

- **Restaurant Discovery**: Discover restaurant information and available offers
- **Offer Presentation**: Present specific offers from restaurants
- **Checkout Initiation**: Start the checkout process for orders
- **Order Confirmation**: Confirm and finalize orders
- **Offer Validation**: Validate if offers can be applied to orders
- **Restaurant Chat**: Chat directly with restaurant agents

## Installation

```bash
cd apps/mcp-restaurant-client
uv sync
```

## Usage

### Starting the MCP Server

```bash
# Start the MCP server
python -m mcp_restaurant_client --a2a-server-url http://localhost:4001
```

### Configuration

The MCP server can be configured with the following options:

- `--host`: Host to bind the MCP server to (default: localhost)
- `--port`: Port to bind the MCP server to (default: 3000)
- `--a2a-server-url`: URL of the A2A server to connect to (default: http://localhost:4001)

### Available Tools

The MCP server provides the following tools:

1. **discover_restaurant**
   - Description: Discover restaurant information and available offers
   - Parameters: `restaurant_id` (string)

2. **present_offer**
   - Description: Present a specific offer from a restaurant
   - Parameters: `offer_id` (string), `restaurant_id` (string)

3. **initiate_checkout**
   - Description: Initiate checkout process for an order
   - Parameters: `offer_id` (string), `items` (array), `restaurant_id` (string), `pickup` (boolean, optional)

4. **confirm_order**
   - Description: Confirm an order
   - Parameters: `order_id` (string), `restaurant_id` (string)

5. **validate_offer**
   - Description: Validate if an offer can be applied to an order
   - Parameters: `offer_id` (string), `items` (array, optional), `restaurant_id` (string)

6. **chat_with_restaurant**
   - Description: Chat with a restaurant agent
   - Parameters: `message` (string), `restaurant_id` (string)

## Integration with Cursor

To use this MCP server with Cursor:

1. Add the following to your Cursor configuration:

```json
{
  "mcpServers": {
    "restaurant-client": {
      "command": "python",
      "args": ["-m", "mcp_restaurant_client", "--a2a-server-url", "http://localhost:4001"]
    }
  }
}
```

2. Restart Cursor to load the new MCP server

3. You can now use the restaurant tools in your conversations with Cursor

## Example Usage

Here are some example interactions:

### Discovering a Restaurant
```
Use the discover_restaurant tool to get information about OTTO Portland
```

### Presenting an Offer
```
Use the present_offer tool to show me the "lunch_special" offer from OTTO Portland
```

### Initiating Checkout
```
Use the initiate_checkout tool to start an order with the "dinner_deal" offer, 
including 2 pizzas and a salad, for pickup
```

### Confirming an Order
```
Use the confirm_order tool to confirm order "order_123" from OTTO Portland
```

## Architecture

The MCP Restaurant Client consists of:

1. **MCP Server** (`server.py`): Handles MCP protocol communication and tool definitions
2. **A2A Client** (`a2a_client.py`): Communicates with A2A servers using the A2A protocol
3. **Main Entry Point** (`__main__.py`): CLI interface for starting the server

The client acts as a bridge between MCP clients (like Cursor) and A2A servers (like the restaurant agents), translating MCP tool calls into A2A protocol requests.

## Development

### Running Tests

```bash
pytest
```

### Adding New Tools

To add new tools:

1. Add the tool definition in `server.py` in the `handle_list_tools` function
2. Add the tool handler in `server.py` in the `handle_call_tool` function
3. Add the corresponding method in `a2a_client.py`

### Dependencies

- `mcp`: Model Context Protocol server implementation
- `a2a`: Agent-to-Agent protocol client
- `httpx`: HTTP client for async requests
- `pydantic`: Data validation
- `click`: CLI interface

## License

This project is part of the AIE7 Demo Day showcase.
