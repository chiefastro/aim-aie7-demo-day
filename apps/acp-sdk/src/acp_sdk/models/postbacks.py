"""Settlement Postback Models for ACP Protocol

This module defines the standardized models for Settlement Postbacks
that merchants send to confirm order completion and trigger bounty distribution.
"""

from datetime import datetime
from typing import Any, Dict, Union, Optional, List
from pydantic import BaseModel, Field


class CurrencyAmount(BaseModel):
    """Currency and amount representation."""
    currency: str = Field("USD", description="Currency code")
    amount: float = Field(..., ge=0.0, description="Amount in currency units")


class PublicSettlementData(BaseModel):
    """Public data for settlement postbacks."""
    order_id: str = Field(..., description="Order identifier being settled")
    status: str = Field(..., description="Order status (success, failed, cancelled)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Settlement timestamp")


class PrivateSettlementData(BaseModel):
    """Private data for settlement postbacks."""
    order_amount: str = Field(..., description="Encrypted order amount")
    bounty_split: Dict[str, Dict[str, str]] = Field(..., description="Encrypted bounty split amounts")
    zk_proof: str = Field(..., description="Zero-knowledge proof of fair split")
    signature: str = Field(..., description="Digital signature")


class SettlementPostback(BaseModel):
    """Settlement postback with privacy separation."""
    public_data: PublicSettlementData = Field(..., description="Public settlement information")
    private_data: PrivateSettlementData = Field(..., description="Private settlement information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "public_data": {
                    "order_id": "ord_12345",
                    "status": "success",
                    "timestamp": "2025-01-13T12:15:00Z"
                },
                "private_data": {
                    "order_amount": "encrypted_28.00",
                    "bounty_split": {
                        "user": {"amount": "encrypted_1.25", "currency": "USD"},
                        "agent": {"amount": "encrypted_1.00", "currency": "USD"},
                        "gor": {"amount": "encrypted_0.25", "currency": "USD"}
                    },
                    "zk_proof": "zkp_fair_split",
                    "signature": "sig_settlement"
                }
            }
        }


# API Request/Response Models
class ProcessPostbackRequest(BaseModel):
    """Request to process a settlement postback."""
    order_id: str = Field(..., description="Order identifier being settled")
    status: str = Field(..., description="Order status")
    amount: CurrencyAmount = Field(..., description="Order amount")
    # Note: split is calculated automatically by the system
    # This field is kept for API compatibility but not used
    split: Optional[Dict[str, float]] = Field(default=None, description="Legacy split field")


class ProcessPostbackResponse(BaseModel):
    """Response for postback processing."""
    public_data: Dict[str, Any] = Field(..., description="Public settlement data")
    private_data: Dict[str, Union[str, List[str]]] = Field(..., description="Private settlement data")
