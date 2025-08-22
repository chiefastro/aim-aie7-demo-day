"""Main FastAPI application for the Transaction Simulator using ACP SDK.

This demonstrates how to create a transaction simulator using the ACP SDK
boilerplate helpers with custom configurations and extensions.
"""

import uvicorn
from acp_sdk import create_txn_simulator_app, WalletManager
from acp_sdk.txns.privacy import PrivacyManager

# Example customizations for this specific transaction simulator
def create_custom_wallet_manager() -> WalletManager:
    """Create a custom wallet manager with demo data."""
    wallet_manager = WalletManager()
    
    # Add custom demo wallets
    wallet_manager._create_user_wallet("custom_user_001", 100.0)
    wallet_manager._create_user_wallet("custom_user_002", 250.0)
    wallet_manager._create_agent_wallet("custom_agent_001", 500.0)
    wallet_manager._create_merchant_wallet("custom_merchant_001", 1000.0)
    
    return wallet_manager

# Create the FastAPI app using ACP SDK helpers
app = create_txn_simulator_app(
    title="Custom ACP Transaction Simulator",
    description="Custom transaction simulator with extended demo data",
    version="1.0.0",
    cors_origins=["http://localhost:3000", "http://localhost:3001"],  # Custom CORS
    wallet_manager=create_custom_wallet_manager(),  # Custom wallet manager
)

# Example: Add custom endpoints specific to this simulator
@app.get("/custom/demo-stats")
async def get_custom_demo_stats():
    """Get custom demo statistics."""
    return {
        "custom_users": 2,
        "custom_agents": 1,
        "custom_merchants": 1,
        "total_custom_balance": 1850.0,
        "simulator_type": "custom-demo"
    }

@app.get("/custom/health")
async def get_custom_health():
    """Get custom health check with additional info."""
    return {
        "status": "healthy",
        "service": "custom-transaction-simulator",
        "sdk_version": "1.0.0",
        "features": ["custom_wallets", "extended_demo_data", "custom_endpoints"]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3003)
