# Custom ACP Transaction Simulator

This is a custom transaction simulator that demonstrates how to use the ACP SDK helpers to build ACP-compliant transaction processing services.

## Overview

This simulator shows how third-party settlement providers can use the ACP SDK to build their own transaction processing services with minimal boilerplate code.

## Key Features

- **Uses ACP SDK Helpers**: Leverages `create_tx_simulator_app()` from the ACP SDK
- **Custom Configuration**: Demonstrates custom wallet manager setup
- **Extended Endpoints**: Shows how to add custom endpoints beyond the standard ones
- **Privacy-Aware**: Implements zero-knowledge proofs and encrypted data handling

## Architecture

```
txn-simulator-acp/
├── src/tx_simulator/
│   ├── __init__.py
│   └── main.py              # Simplified main app using ACP SDK
├── pyproject.toml           # Dependencies including ACP SDK
├── Dockerfile              # Container configuration
└── README.md               # This file
```

## How It Works

### 1. ACP SDK Integration

The main application uses the ACP SDK's `create_tx_simulator_app()` helper:

```python
from acp_sdk import create_tx_simulator_app, WalletManager

# Create custom wallet manager
def create_custom_wallet_manager() -> WalletManager:
    wallet_manager = WalletManager()
    wallet_manager._create_user_wallet("custom_user_001", 100.0)
    # ... more custom setup
    return wallet_manager

# Create app with custom configuration
app = create_tx_simulator_app(
    title="Custom ACP Transaction Simulator",
    description="Custom transaction simulator with extended demo data",
    version="1.0.0",
    cors_origins=["http://localhost:3000", "http://localhost:3001"],
    wallet_manager=create_custom_wallet_manager(),
)
```

### 2. Standard Endpoints

The ACP SDK automatically provides all standard endpoints:

- `GET /health` - Health check
- `GET /` - Service information
- `GET /protocol/stats` - Protocol statistics
- `POST /receipts` - Create attribution receipts
- `POST /postbacks` - Process settlement postbacks
- `GET /wallets/{type}/{id}` - Query wallets
- `GET /wallets/{type}/{id}/transactions` - Transaction history

### 3. Custom Extensions

This simulator adds custom endpoints:

- `GET /custom/demo-stats` - Custom demo statistics
- `GET /custom/health` - Extended health check

## Benefits of Using ACP SDK

1. **Reduced Boilerplate**: No need to implement standard endpoints
2. **Consistent API**: All ACP-compliant services have the same interface
3. **Privacy Built-in**: Zero-knowledge proofs and encryption handled automatically
4. **Customizable**: Easy to extend with custom functionality
5. **Maintained**: Core functionality maintained by ACP SDK

## Running the Simulator

### Development

```bash
cd apps/txn-simulator-acp
uv run python -m tx_simulator.main
```

### Docker

```bash
cd apps/txn-simulator-acp
docker build -t txn-simulator-acp .
docker run -p 3003:3003 txn-simulator-acp
```

## API Endpoints

### Standard Endpoints (from ACP SDK)

All standard transaction simulator endpoints are available:

- **Health**: `GET /health`
- **Info**: `GET /`
- **Stats**: `GET /protocol/stats`
- **Receipts**: `POST /receipts`
- **Postbacks**: `POST /postbacks`
- **Wallets**: `GET /wallets/{type}/{id}`
- **Transactions**: `GET /wallets/{type}/{id}/transactions`

### Custom Endpoints

- **Custom Stats**: `GET /custom/demo-stats`
- **Custom Health**: `GET /custom/health`

## Example Usage

### Create a Receipt

```bash
curl -X POST http://localhost:3003/receipts \
  -H "Content-Type: application/json" \
  -d '{
    "offer_id": "ofr_001",
    "order_id": "ord_123",
    "agent_id": "agt_consumer",
    "user_id": "usr_demo",
    "gor_operator_id": "gor_demo",
    "bounty_amount": 2.50
  }'
```

### Get Custom Stats

```bash
curl http://localhost:3003/custom/demo-stats
```

## Customization

To create your own transaction simulator:

1. **Copy this structure** as a starting point
2. **Customize the wallet manager** in `create_custom_wallet_manager()`
3. **Add custom endpoints** as needed
4. **Configure CORS** and other settings
5. **Deploy** your custom simulator

## Dependencies

- **ACP SDK**: Provides core transaction simulator functionality
- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation
- **Cryptography**: Privacy and security features

## License

This is part of the ACP Demo project. See the main project license for details.
