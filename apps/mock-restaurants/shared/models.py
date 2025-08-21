from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
import uuid

class OrderStatus(str, Enum):
    CREATED = "CREATED"
    CONFIRMED = "CONFIRMED"
    SETTLED = "SETTLED"
    CANCELLED = "CANCELLED"

class MenuItem(BaseModel):
    id: str
    name: str
    description: str
    price: float
    category: str
    available: bool = True
    dietary_tags: List[str] = []

class OrderItem(BaseModel):
    menu_item_id: str
    quantity: int = 1
    special_instructions: Optional[str] = None
    price: float

class CreateOrderRequest(BaseModel):
    items: List[OrderItem]
    offer_id: Optional[str] = None
    customer_name: str
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    order_type: str = "dine-in"  # dine-in, takeout, delivery
    special_instructions: Optional[str] = None

class OrderResponse(BaseModel):
    order_id: str
    status: OrderStatus
    items: List[OrderItem]
    subtotal: float
    tax: float
    discount: float = 0.0
    total: float
    offer_applied: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    estimated_ready_time: Optional[datetime] = None

class ConfirmOrderRequest(BaseModel):
    estimated_ready_time: Optional[datetime] = None
    notes: Optional[str] = None

class SettleOrderRequest(BaseModel):
    payment_method: str = "credit_card"
    payment_token: Optional[str] = None
    tip_amount: float = 0.0

class ValidateOfferRequest(BaseModel):
    offer_id: str
    items: List[OrderItem]
    order_type: str = "dine-in"

class ValidateOfferResponse(BaseModel):
    valid: bool
    discount_amount: float = 0.0
    message: str
    restrictions: List[str] = []

# A2A Protocol Models
class A2AEnvelope(BaseModel):
    """A2A message envelope"""
    envelope_id: str
    a2a_version: str = "0.1"
    agent_id: str
    audience: str
    nonce: str
    issued_at: datetime
    expires_at: Optional[datetime] = None
    capabilities: List[str] = []
    policies: Dict[str, Any] = {}
    payload: Dict[str, Any]
    signature: Optional[str] = None

class PresentOfferRequest(BaseModel):
    """Request to present an offer"""
    offer_id: str
    user_context: Optional[Dict[str, Any]] = None

class PresentOfferResponse(BaseModel):
    """Response with offer details"""
    offer_id: str
    offer_summary: str
    constraints: List[str]
    estimated_total: float
    currency: str = "USD"
    valid_until: datetime

class InitiateCheckoutRequest(BaseModel):
    """Request to initiate checkout"""
    offer_id: str
    items: List[Dict[str, Any]]
    pickup: bool = False
    notes: Optional[str] = None
    user_preferences: Optional[Dict[str, Any]] = None

class InitiateCheckoutResponse(BaseModel):
    """Response with order details"""
    order_id: str
    status: str
    total_amount: float
    currency: str = "USD"
    payment_instructions: Dict[str, Any]
    estimated_ready_time: Optional[datetime] = None

class ConfirmOrderRequest(BaseModel):
    """Request to confirm order"""
    order_id: str
    payment_confirmation: Optional[Dict[str, Any]] = None

class ConfirmOrderResponse(BaseModel):
    """Response with confirmation details"""
    order_id: str
    status: str
    confirmation_details: Dict[str, Any]
    receipt_url: Optional[str] = None

class MenuResponse(BaseModel):
    categories: Dict[str, List[MenuItem]]
    restaurant_info: Dict[str, Any]

class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
