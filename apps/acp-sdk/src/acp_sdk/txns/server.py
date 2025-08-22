"""Transaction Simulator Server Helpers

This module provides boilerplate FastAPI server setup and endpoint helpers
for building ACP-compliant transaction simulators.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional

from ..models.receipts import (
    CreateReceiptRequest,
    CreateReceiptResponse,
)
from ..models.postbacks import (
    ProcessPostbackRequest,
    ProcessPostbackResponse,
)
from ..models.wallets import (
    ProtocolStats,
    WalletResponse,
)
from .wallet_manager import WalletManager


def create_txn_simulator_app(
    title: str = "ACP Transaction Simulator",
    description: str = "Privacy-aware Transaction Simulator for Agentic Commerce Protocol",
    version: str = "0.1.0",
    cors_origins: Optional[list] = None,
    wallet_manager: Optional[WalletManager] = None,
) -> FastAPI:
    """Create a FastAPI app with transaction simulator boilerplate.
    
    Args:
        title: App title
        description: App description  
        version: App version
        cors_origins: CORS origins (defaults to ["*"] for demo)
        wallet_manager: Wallet manager instance (creates default if None)
    
    Returns:
        Configured FastAPI app with transaction simulator endpoints
    """
    
    # Create FastAPI app
    app = FastAPI(
        title=title,
        description=description,
        version=version,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins or ["*"],  # Demo only - restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize wallet manager if not provided
    if wallet_manager is None:
        wallet_manager = WalletManager()
    
    # Add standard endpoints
    add_health_endpoint(app)
    add_root_endpoint(app, title, version)
    add_protocol_endpoints(app, wallet_manager)
    add_receipt_endpoints(app, wallet_manager)
    add_postback_endpoints(app, wallet_manager)
    add_wallet_endpoints(app, wallet_manager)
    add_transaction_endpoints(app, wallet_manager)
    
    return app


def add_health_endpoint(app: FastAPI) -> None:
    """Add health check endpoint."""
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": "transaction-simulator"}


def add_root_endpoint(app: FastAPI, title: str, version: str) -> None:
    """Add root endpoint with service information."""
    
    @app.get("/")
    async def root():
        """Root endpoint with service information."""
        return {
            "service": title,
            "version": version,
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


def add_protocol_endpoints(app: FastAPI, wallet_manager: WalletManager) -> None:
    """Add protocol statistics endpoint."""
    
    @app.get("/protocol/stats", response_model=ProtocolStats)
    async def get_protocol_stats():
        """Get public protocol statistics."""
        stats = wallet_manager.get_protocol_stats()
        return ProtocolStats(**stats)


def add_receipt_endpoints(app: FastAPI, wallet_manager: WalletManager) -> None:
    """Add receipt creation endpoint."""
    
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


def add_postback_endpoints(app: FastAPI, wallet_manager: WalletManager) -> None:
    """Add settlement postback endpoint."""
    
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


def add_wallet_endpoints(app: FastAPI, wallet_manager: WalletManager) -> None:
    """Add wallet query endpoints."""
    
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


def add_transaction_endpoints(app: FastAPI, wallet_manager: WalletManager) -> None:
    """Add transaction history endpoints."""
    
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
