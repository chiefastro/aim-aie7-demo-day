# ACP MCP Server

Universal commerce MCP server for ACP-compliant merchants.

## Overview

The ACP MCP Server provides standardized commerce tools that work with any ACP-compliant merchant agent, enabling universal commerce integration. This server acts as a bridge between consumer agents and ACP-compliant merchants through the A2A protocol.

## Features

- **Merchant Discovery**: Find ACP-compliant merchants by query, location, or cuisine type
- **Food Ordering**: Place orders with any ACP-compliant merchant
- **Offer Validation**: Validate offers and discounts
- **Payment Processing**: Process payments through merchant agents
- **Menu Retrieval**: Get menus and item information
- **Order Tracking**: Track order status and updates

## Installation

```bash
# Install dependencies
uv sync

# Run the server
uv run python -m acp_mcp
```

## Usage

The ACP MCP Server provides the following tools:

### `discover_merchants`
Discover ACP-compliant merchants by search criteria.

**Parameters:**
- `query` (optional): Search query for merchants (e.g., 'pizza', 'sushi')
- `lat` (optional): Latitude for location-based search
- `lng` (optional): Longitude for location-based search
- `radius_m` (optional): Search radius in meters
- `cuisine_type` (optional): Filter by cuisine type

### `order_food`
Place a food order with an ACP-compliant merchant.

**Parameters:**
- `merchant_id`: Merchant identifier
- `items`: List of items to order
- `offer_id` (optional): Offer to apply
- `pickup` (optional): Whether this is pickup (default: true)
- `delivery_address` (optional): Delivery address if not pickup
- `special_instructions` (optional): Special order instructions

### `validate_offer`
Validate an offer with an ACP-compliant merchant.

**Parameters:**
- `merchant_id`: Merchant identifier
- `offer_id`: Offer to validate
- `items`: Items to validate against

### `process_payment`
Process payment with an ACP-compliant merchant.

**Parameters:**
- `merchant_id`: Merchant identifier
- `order_id`: Order to pay for
- `amount`: Amount to charge
- `payment_method`: Payment method to use
- `payment_details` (optional): Payment method specific details

### `get_menu`
Get menu from an ACP-compliant merchant.

**Parameters:**
- `merchant_id`: Merchant identifier
- `category` (optional): Menu category filter

### `track_order`
Track order status with an ACP-compliant merchant.

**Parameters:**
- `merchant_id`: Merchant identifier
- `order_id`: Order to track

## Architecture

The ACP MCP Server consists of:

1. **FastMCP Server**: Provides the MCP interface with async tool handlers
2. **ACP Client**: Handles communication with ACP-compliant merchants via A2A protocol
3. **Data Models**: Standardized request/response structures for commerce operations

## Development

```bash
# Install development dependencies
uv sync --extra dev

# Run tests
uv run pytest

# Format code
uv run black src/
uv run isort src/
```

## License

MIT License
