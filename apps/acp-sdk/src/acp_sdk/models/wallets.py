"""Wallet Models for ACP Protocol

This module defines the standardized models for wallet operations
including user, agent, GOR operator, and merchant wallets.
"""

from datetime import datetime
from typing import Any, Dict, List
from uuid import uuid4
from pydantic import BaseModel, Field


class PublicWalletData(BaseModel):
    """Public data for wallets."""
    entity_id: str = Field(..., description="Entity identifier")
    transactions_count: int = Field(0, description="Number of transactions")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")


class PrivateWalletData(BaseModel):
    """Private data for wallets."""
    balance: str = Field(..., description="Encrypted balance")
    total_earned: str = Field(..., description="Encrypted total earned")
    zk_proof: str = Field(..., description="Zero-knowledge proof of balance accuracy")


class UserWallet(BaseModel):
    """User wallet with privacy protection."""
    public_data: PublicWalletData = Field(..., description="Public wallet information")
    private_data: PrivateWalletData = Field(..., description="Private wallet information")


class AgentWallet(BaseModel):
    """Agent wallet with privacy protection."""
    public_data: PublicWalletData = Field(..., description="Public wallet information")
    private_data: PrivateWalletData = Field(..., description="Private wallet information")


class GORWallet(BaseModel):
    """GOR operator wallet with privacy protection."""
    public_data: PublicWalletData = Field(..., description="Public wallet information")
    private_data: PrivateWalletData = Field(..., description="Private wallet information")


class MerchantWalletPublicData(BaseModel):
    """Public data for merchant wallets."""
    merchant_id: str = Field(..., description="Merchant identifier")
    bounties_paid: int = Field(0, description="Number of bounties paid")
    transactions_count: int = Field(0, description="Number of transactions")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")


class MerchantWalletPrivateData(BaseModel):
    """Private data for merchant wallets."""
    balance: str = Field(..., description="Encrypted balance")
    total_funded: str = Field(..., description="Encrypted total funded")
    total_spent: str = Field(..., description="Encrypted total spent")
    zk_proof: str = Field(..., description="Zero-knowledge proof of balance accuracy")


class MerchantWallet(BaseModel):
    """Merchant wallet with privacy protection."""
    public_data: MerchantWalletPublicData = Field(..., description="Public merchant wallet information")
    private_data: MerchantWalletPrivateData = Field(..., description="Private merchant wallet information")


# Transaction History Models
class PublicTransactionData(BaseModel):
    """Public data for transactions."""
    transaction_id: str = Field(
        default_factory=lambda: f"txn_{uuid4().hex[:8]}", 
        description="Unique transaction identifier"
    )
    type: str = Field(..., description="Transaction type")
    order_id: str = Field(..., description="Order identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Transaction timestamp")


class PrivateTransactionData(BaseModel):
    """Private data for transactions."""
    transaction_amounts: List[str] = Field(..., description="Encrypted transaction amounts")
    zk_proof: str = Field(..., description="Zero-knowledge proof of transaction accuracy")


class TransactionHistory(BaseModel):
    """Transaction history with privacy protection."""
    public_data: Dict[str, List[PublicTransactionData]] = Field(..., description="Public transaction data")
    private_data: PrivateTransactionData = Field(..., description="Private transaction data")


# API Response Models
class WalletResponse(BaseModel):
    """Response for wallet queries."""
    public_data: Dict[str, Any] = Field(..., description="Public wallet data")
    private_data: Dict[str, str] = Field(..., description="Private wallet data")


class ProtocolStats(BaseModel):
    """Public protocol statistics."""
    total_bounties_paid: int = Field(..., description="Total bounties paid")
    active_merchants: int = Field(..., description="Number of active merchants")
    active_agents: int = Field(..., description="Number of active agents")
    total_users: int = Field(..., description="Total number of users")
    total_transactions: int = Field(..., description="Total number of transactions")
    last_updated: str = Field(..., description="ISO formatted timestamp")
