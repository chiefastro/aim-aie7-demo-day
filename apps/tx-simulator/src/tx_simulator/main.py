"""Main FastAPI application for the Transaction Simulator."""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from acp_sdk.models.receipts import (
    CreateReceiptRequest,
    CreateReceiptResponse,
)
from acp_sdk.models.postbacks import (
    ProcessPostbackRequest,
    ProcessPostbackResponse,
)
from acp_sdk.models.wallets import (
    ProtocolStats,
    WalletResponse,
)
from .wallet_manager import wallet_manager

# Create FastAPI app
app = FastAPI(
    title="ACP Transaction Simulator",
    description="Privacy-aware Transaction Simulator for Agentic Commerce Protocol",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Demo only - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "transaction-simulator"}


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "ACP Transaction Simulator",
        "version": "0.1.0",
        "description": "Privacy-aware transaction processing for ACP",
        "endpoints": {
            "health": "/health",
            "protocol_stats": "/protocol/stats",
            "receipts": "/receipts",
            "postbacks": "/postbacks",
            "wallets": {
                "users": "/wallets/users/{user_id}",
                "agents": "/wallets/agents/{agent_id}",
                "gor": "/wallets/gor/{gor_id}",
                "merchants": "/wallets/merchants/{merchant_id}",
            },
            "transactions": {
                "users": "/wallets/users/{user_id}/transactions",
                "agents": "/wallets/agents/{agent_id}/transactions",
                "gor": "/wallets/gor/{gor_id}/transactions",
                "merchants": "/wallets/merchants/{merchant_id}/transactions",
            },
        },
    }


@app.get("/protocol/stats", response_model=ProtocolStats)
async def get_protocol_stats():
    """Get public protocol statistics."""
    stats = wallet_manager.get_protocol_stats()
    return ProtocolStats(**stats)


@app.post("/receipts", response_model=CreateReceiptResponse)
async def create_receipt(request: CreateReceiptRequest):
    """Create an attribution receipt."""
    try:
        receipt = wallet_manager.create_receipt(request)
        
        return CreateReceiptResponse(
            receipt_id=receipt.receipt_id,
            public_data={
                "status": receipt.public_data.status,
                "timestamp": receipt.public_data.timestamp.isoformat(),
            },
            private_data={
                "bounty_reserved": receipt.private_data.bounty_amount,
                "zk_proof": receipt.private_data.zk_proof,
            },
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@app.post("/postbacks", response_model=ProcessPostbackResponse)
async def process_postback(request: ProcessPostbackRequest):
    """Process a settlement postback."""
    try:
        settlement = wallet_manager.process_settlement(request)
        
        return ProcessPostbackResponse(
            public_data={
                "status": settlement.public_data.status,
                "timestamp": settlement.public_data.timestamp.isoformat(),
            },
            private_data={
                "wallets_updated": [
                    "user_wallet",
                    "agent_wallet", 
                    "gor_wallet",
                    "merchant_wallet",
                ],
                "zk_proof": settlement.private_data.zk_proof,
            },
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@app.get("/wallets/users/{user_id}", response_model=WalletResponse)
async def get_user_wallet(user_id: str):
    """Get user wallet."""
    wallet = wallet_manager.get_user_wallet(user_id)
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User wallet not found: {user_id}",
        )
    
    return WalletResponse(
        public_data={
            "user_id": wallet.public_data.entity_id,
            "transactions_count": wallet.public_data.transactions_count,
            "last_updated": wallet.public_data.last_updated.isoformat(),
        },
        private_data={
            "balance": wallet.private_data.balance,
            "total_earned": wallet.private_data.total_earned,
            "zk_proof": wallet.private_data.zk_proof,
        },
    )


@app.get("/wallets/agents/{agent_id}", response_model=WalletResponse)
async def get_agent_wallet(agent_id: str):
    """Get agent wallet."""
    wallet = wallet_manager.get_agent_wallet(agent_id)
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent wallet not found: {agent_id}",
        )
    
    return WalletResponse(
        public_data={
            "agent_id": wallet.public_data.entity_id,
            "transactions_count": wallet.public_data.transactions_count,
            "last_updated": wallet.public_data.last_updated.isoformat(),
        },
        private_data={
            "balance": wallet.private_data.balance,
            "total_earned": wallet.private_data.total_earned,
            "zk_proof": wallet.private_data.zk_proof,
        },
    )


@app.get("/wallets/gor/{gor_id}", response_model=WalletResponse)
async def get_gor_wallet(gor_id: str):
    """Get GOR operator wallet."""
    wallet = wallet_manager.get_gor_wallet(gor_id)
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"GOR operator wallet not found: {gor_id}",
        )
    
    return WalletResponse(
        public_data={
            "gor_operator_id": wallet.public_data.entity_id,
            "transactions_count": wallet.public_data.transactions_count,
            "last_updated": wallet.public_data.last_updated.isoformat(),
        },
        private_data={
            "balance": wallet.private_data.balance,
            "total_earned": wallet.private_data.total_earned,
            "zk_proof": wallet.private_data.zk_proof,
        },
    )


@app.get("/wallets/merchants/{merchant_id}", response_model=WalletResponse)
async def get_merchant_wallet(merchant_id: str):
    """Get merchant wallet."""
    wallet = wallet_manager.get_merchant_wallet(merchant_id)
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Merchant wallet not found: {merchant_id}",
        )
    
    return WalletResponse(
        public_data={
            "merchant_id": wallet.public_data.merchant_id,
            "bounties_paid": wallet.public_data.bounties_paid,
            "last_updated": wallet.public_data.last_updated.isoformat(),
        },
        private_data={
            "balance": wallet.private_data.balance,
            "total_funded": wallet.private_data.total_funded,
            "total_spent": wallet.private_data.total_spent,
            "zk_proof": wallet.private_data.zk_proof,
        },
    )


@app.get("/wallets/users/{user_id}/transactions")
async def get_user_transactions(user_id: str):
    """Get user transaction history."""
    transactions = wallet_manager.get_transaction_history(user_id)
    
    return {
        "public_data": {
            "transactions": [
                {
                    "transaction_id": t.transaction_id,
                    "type": t.type,
                    "order_id": t.order_id,
                    "timestamp": t.timestamp.isoformat(),
                }
                for t in transactions
            ]
        },
        "private_data": {
            "transaction_amounts": ["encrypted_amounts"],  # Demo - would be real encrypted amounts
            "zk_proof": "zk_proof_transaction_accuracy_demo",
        },
    }


@app.get("/wallets/agents/{agent_id}/transactions")
async def get_agent_transactions(agent_id: str):
    """Get agent transaction history."""
    transactions = wallet_manager.get_transaction_history(agent_id)
    
    return {
        "public_data": {
            "transactions": [
                {
                    "transaction_id": t.transaction_id,
                    "type": t.type,
                    "order_id": t.order_id,
                    "timestamp": t.timestamp.isoformat(),
                }
                for t in transactions
            ]
        },
        "private_data": {
            "transaction_amounts": ["encrypted_amounts"],  # Demo - would be real encrypted amounts
            "zk_proof": "zk_proof_transaction_accuracy_demo",
        },
    }


@app.get("/wallets/gor/{gor_id}/transactions")
async def get_gor_transactions(gor_id: str):
    """Get GOR operator transaction history."""
    transactions = wallet_manager.get_transaction_history(gor_id)
    
    return {
        "public_data": {
            "transactions": [
                {
                    "transaction_id": t.transaction_id,
                    "type": t.type,
                    "order_id": t.order_id,
                    "timestamp": t.timestamp.isoformat(),
                }
                for t in transactions
            ]
        },
        "private_data": {
            "transaction_amounts": ["encrypted_amounts"],  # Demo - would be real encrypted amounts
            "zk_proof": "zk_proof_transaction_accuracy_demo",
        },
    }


@app.get("/wallets/merchants/{merchant_id}/transactions")
async def get_merchant_transactions(merchant_id: str):
    """Get merchant transaction history."""
    transactions = wallet_manager.get_transaction_history(merchant_id)
    
    return {
        "public_data": {
            "transactions": [
                {
                    "transaction_id": t.transaction_id,
                    "type": t.type,
                    "order_id": t.order_id,
                    "timestamp": t.timestamp.isoformat(),
                }
                for t in transactions
            ]
        },
        "private_data": {
            "transaction_amounts": ["encrypted_amounts"],  # Demo - would be real encrypted amounts
            "zk_proof": "zk_proof_transaction_accuracy_demo",
        },
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(app, host="0.0.0.0", port=3003)
