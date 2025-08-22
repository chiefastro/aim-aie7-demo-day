"""Attribution Receipt Models for ACP Protocol

This module defines the standardized models for Attribution Receipts
that are created when consumers initiate checkout with offers.
"""

from datetime import datetime
from typing import Any, Dict
from uuid import uuid4
from pydantic import BaseModel, Field


class PublicReceiptData(BaseModel):
    """Public data for attribution receipts."""
    offer_id: str = Field(..., description="ID of the offer being attributed")
    order_id: str = Field(..., description="Unique order identifier")
    agent_id: str = Field(..., description="ID of the agent that initiated checkout")
    user_id: str = Field(..., description="ID of the user making the purchase")
    gor_operator_id: str = Field(..., description="ID of the GOR operator")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Receipt creation timestamp")
    status: str = Field("reserved", description="Receipt status")


class PrivateReceiptData(BaseModel):
    """Private data for attribution receipts."""
    bounty_amount: str = Field(..., description="Encrypted bounty amount")
    zk_proof: str = Field(..., description="Zero-knowledge proof of bounty reservation")
    signature: str = Field(..., description="Digital signature")


class AttributionReceipt(BaseModel):
    """Attribution receipt with privacy separation."""
    receipt_id: str = Field(
        default_factory=lambda: f"rcpt_{uuid4().hex[:8]}", 
        description="Unique receipt identifier"
    )
    public_data: PublicReceiptData = Field(..., description="Public receipt information")
    private_data: PrivateReceiptData = Field(..., description="Private receipt information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "receipt_id": "rcpt_a1b2c3d4",
                "public_data": {
                    "offer_id": "ofr_001",
                    "order_id": "ord_12345",
                    "agent_id": "agt_consumer_demo",
                    "user_id": "usr_demo",
                    "gor_operator_id": "gor_demo",
                    "timestamp": "2025-01-13T12:00:00Z",
                    "status": "reserved"
                },
                "private_data": {
                    "bounty_amount": "encrypted_2.50",
                    "zk_proof": "zkp_bounty_reservation",
                    "signature": "sig_attribution"
                }
            }
        }


# API Request/Response Models
class CreateReceiptRequest(BaseModel):
    """Request to create an attribution receipt."""
    offer_id: str = Field(..., description="ID of the offer being attributed")
    order_id: str = Field(..., description="Unique order identifier")
    agent_id: str = Field(..., description="ID of the agent that initiated checkout")
    user_id: str = Field(..., description="ID of the user making the purchase")
    gor_operator_id: str = Field(..., description="ID of the GOR operator")
    bounty_amount: float = Field(..., gt=0.0, description="Bounty amount in currency units")


class CreateReceiptResponse(BaseModel):
    """Response for receipt creation."""
    receipt_id: str = Field(..., description="Created receipt ID")
    public_data: Dict[str, Any] = Field(..., description="Public receipt data")
    private_data: Dict[str, str] = Field(..., description="Private receipt data")
