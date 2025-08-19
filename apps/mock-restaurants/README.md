# Mock Restaurant Web Servers

This directory contains mock web servers for 3 example restaurants that simulate real restaurant websites with A2A (Agent-to-Agent) endpoints for transaction processing.

## Structure

Each restaurant has its own subdirectory with:
- `main.py` - FastAPI application with all endpoints
- `data/` - Restaurant-specific offer documents and OSF files
- `models.py` - Pydantic models for request/response schemas
- `transaction_logic.py` - Mock transaction processing logic

## Restaurants

1. **OTTO Portland** (Port 8001) - Italian pizza restaurant
2. **Toast Street Exeter** (Port 8002) - British pub
3. **Newick's Lobster House** (Port 8003) - Seafood restaurant

## Running the Servers

### Local Development (using uv)

```bash
# Install dependencies
make install

# Start all servers
make start-all

# Or start individually
make start-otto
make start-toast
make start-newicks
```

### Docker Deployment

```bash
# Build and start all servers in containers
make docker-run

# Or manually
docker-compose up -d

# Stop all containers
make docker-stop

# Or manually
docker-compose down
```

## Endpoints

Each restaurant server exposes:

### OSF Endpoints
- `GET /.well-known/osf.json` - Open Source Food specification
- `GET /.well-known/offers/{offer_id}.json` - Individual offer documents

### A2A Endpoints
- `POST /a2a/order/create` - Create new order
- `GET /a2a/order/{order_id}` - Get order status
- `POST /a2a/order/{order_id}/confirm` - Confirm order
- `POST /a2a/order/{order_id}/settle` - Settle payment
- `GET /a2a/menu` - Get restaurant menu
- `POST /a2a/validate-offer` - Validate offer applicability

### Transaction Flow
1. **CREATED** - Order is created with items and offer
2. **CONFIRMED** - Order is confirmed by restaurant
3. **SETTLED** - Payment is processed and order completed

## URLs

- OTTO Portland: http://localhost:8001
- Toast Street Exeter: http://localhost:8002  
- Newick's Lobster House: http://localhost:8003
