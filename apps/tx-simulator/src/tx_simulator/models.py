"""Data models for the Transaction Simulator with privacy protection."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

from pydantic import BaseModel, Field


class CurrencyAmount(BaseModel):
    """Currency and amount representation."""
    currency: str = "USD"
    amount: float = Field(..., ge=0.0)


class PublicReceiptData(BaseModel):
    """Public data for attribution receipts."""
    offer_id: str
    order_id: str
    agent_id: str
    user_id: str
    gor_operator_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str = "reserved"


class PrivateReceiptData(BaseModel):
    """Private data for attribution receipts."""
    bounty_amount: str = Field(..., description="Encrypted bounty amount")
    zk_proof: str = Field(..., description="Zero-knowledge proof of bounty reservation")
    signature: str = Field(..., description="Digital signature")


class AttributionReceipt(BaseModel):
    """Attribution receipt with privacy separation."""
    receipt_id: str = Field(default_factory=lambda: f"rcpt_{uuid4().hex[:8]}")
    public_data: PublicReceiptData
    private_data: PrivateReceiptData


class PublicSettlementData(BaseModel):
    """Public data for settlement postbacks."""
    order_id: str
    status: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PrivateSettlementData(BaseModel):
    """Private data for settlement postbacks."""
    order_amount: str = Field(..., description="Encrypted order amount")
    bounty_split: Dict[str, Dict[str, str]] = Field(..., description="Encrypted bounty split amounts")
    zk_proof: str = Field(..., description="Zero-knowledge proof of fair split")
    signature: str = Field(..., description="Digital signature")


class SettlementPostback(BaseModel):
    """Settlement postback with privacy separation."""
    public_data: PublicSettlementData
    private_data: PrivateSettlementData


class PublicWalletData(BaseModel):
    """Public data for wallets."""
    entity_id: str
    transactions_count: int = 0
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class PrivateWalletData(BaseModel):
    """Private data for wallets."""
    balance: str = Field(..., description="Encrypted balance")
    total_earned: str = Field(..., description="Encrypted total earned")
    zk_proof: str = Field(..., description="Zero-knowledge proof of balance accuracy")


class UserWallet(BaseModel):
    """User wallet with privacy protection."""
    public_data: PublicWalletData
    private_data: PrivateWalletData


class AgentWallet(BaseModel):
    """Agent wallet with privacy protection."""
    public_data: PublicWalletData
    private_data: PrivateWalletData


class GORWallet(BaseModel):
    """GOR operator wallet with privacy protection."""
    public_data: PublicWalletData
    private_data: PrivateWalletData


class MerchantWalletPublicData(BaseModel):
    """Public data for merchant wallets."""
    merchant_id: str
    bounties_paid: int = 0
    transactions_count: int = 0
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class MerchantWalletPrivateData(BaseModel):
    """Private data for merchant wallets."""
    balance: str = Field(..., description="Encrypted balance")
    total_funded: str = Field(..., description="Encrypted total funded")
    total_spent: str = Field(..., description="Encrypted total spent")
    zk_proof: str = Field(..., description="Zero-knowledge proof of balance accuracy")


class MerchantWallet(BaseModel):
    """Merchant wallet with privacy protection."""
    public_data: MerchantWalletPublicData
    private_data: MerchantWalletPrivateData


class PublicTransactionData(BaseModel):
    """Public data for transactions."""
    transaction_id: str = Field(default_factory=lambda: f"txn_{uuid4().hex[:8]}")
    type: str
    order_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PrivateTransactionData(BaseModel):
    """Private data for transactions."""
    transaction_amounts: List[str] = Field(..., description="Encrypted transaction amounts")
    zk_proof: str = Field(..., description="Zero-knowledge proof of transaction accuracy")


class TransactionHistory(BaseModel):
    """Transaction history with privacy protection."""
    public_data: Dict[str, List[PublicTransactionData]]
    private_data: PrivateTransactionData


# Request/Response models for API endpoints
class CreateReceiptRequest(BaseModel):
    """Request to create an attribution receipt."""
    offer_id: str
    order_id: str
    agent_id: str
    user_id: str
    gor_operator_id: str
    bounty_amount: float = Field(..., gt=0.0)


class CreateReceiptResponse(BaseModel):
    """Response for receipt creation."""
    receipt_id: str
    public_data: Dict[str, Any]
    private_data: Dict[str, str]


class ProcessPostbackRequest(BaseModel):
    """Request to process a settlement postback."""
    order_id: str
    status: str
    amount: CurrencyAmount
    # Note: split is calculated automatically by the system
    # This field is kept for API compatibility but not used
    split: Optional[Dict[str, float]] = Field(default=None)


class ProcessPostbackResponse(BaseModel):
    """Response for postback processing."""
    public_data: Dict[str, Any]
    private_data: Dict[str, Union[str, List[str]]]


class WalletResponse(BaseModel):
    """Response for wallet queries."""
    public_data: Dict[str, Any]
    private_data: Dict[str, str]


class ProtocolStats(BaseModel):
    """Public protocol statistics."""
    total_bounties_paid: int
    active_merchants: int
    active_agents: int
    total_users: int
    total_transactions: int
    last_updated: str = Field(..., description="ISO formatted timestamp")
