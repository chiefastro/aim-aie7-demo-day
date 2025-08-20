from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
import uuid

class OrderState(str, Enum):
    DISCOVERED = "DISCOVERED"
    PRESENTED = "PRESENTED"
    INTENT = "INTENT"
    CREATED = "CREATED"
    CONFIRMED = "CONFIRMED"
    SETTLED = "SETTLED"
    FAILED = "FAILED"

class AgentCapability(str, Enum):
    PRESENT_OFFER = "present_offer"
    INITIATE_CHECKOUT = "initiate_checkout"
    CONFIRM_ORDER = "confirm_order"
    VALIDATE_OFFER = "validate_offer"

class A2AEnvelope(BaseModel):
    """A2A message envelope with authentication"""
    envelope_id: str = Field(default_factory=lambda: f"a2a_{uuid.uuid4().hex[:8]}")
    a2a_version: str = "0.1"
    agent_id: str
    audience: str
    nonce: str = Field(default_factory=lambda: uuid.uuid4().hex)
    issued_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    capabilities: List[AgentCapability] = []
    policies: Dict[str, Any] = {}
    payload: Dict[str, Any]
    signature: Optional[str] = None  # Mock signature for demo

class AgentCard(BaseModel):
    """Agent discovery card for well-known endpoint"""
    agent_id: str
    name: str
    description: str
    version: str = "0.1"
    capabilities: List[AgentCapability]
    endpoints: Dict[str, str]
    policies: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}

class PresentOfferRequest(BaseModel):
    """Request to present an offer to a user"""
    offer_id: str
    user_context: Optional[Dict[str, Any]] = None

class PresentOfferResponse(BaseModel):
    """Response with offer details and constraints"""
    offer_id: str
    offer_summary: str
    constraints: List[str]
    estimated_total: float
    currency: str = "USD"
    valid_until: datetime

class InitiateCheckoutRequest(BaseModel):
    """Request to initiate checkout process"""
    offer_id: str
    items: List[Dict[str, Any]]
    pickup: bool = False
    notes: Optional[str] = None
    user_preferences: Optional[Dict[str, Any]] = None

class InitiateCheckoutResponse(BaseModel):
    """Response with order details and payment instructions"""
    order_id: str
    status: OrderState
    total_amount: float
    currency: str = "USD"
    payment_instructions: Dict[str, Any]
    estimated_ready_time: Optional[datetime] = None

class ConfirmOrderRequest(BaseModel):
    """Request to confirm an order"""
    order_id: str
    payment_confirmation: Optional[Dict[str, Any]] = None

class ConfirmOrderResponse(BaseModel):
    """Response with order confirmation"""
    order_id: str
    status: OrderState
    confirmation_details: Dict[str, Any]
    receipt_url: Optional[str] = None

class AgentState(BaseModel):
    """State for LangGraph agent"""
    session_id: str
    user_id: Optional[str] = None
    current_offer: Optional[Dict[str, Any]] = None
    current_order: Optional[Dict[str, Any]] = None
    conversation_history: List[Dict[str, Any]] = []
    order_state: OrderState = OrderState.DISCOVERED
    user_preferences: Dict[str, Any] = {}
    context: Dict[str, Any] = {}

class RestaurantConfig(BaseModel):
    """Configuration for a restaurant agent"""
    restaurant_id: str
    name: str
    description: str
    osf_endpoint: str
    a2a_endpoints: Dict[str, str]
    menu_endpoint: str
    well_known_endpoint: str
    agent_capabilities: List[AgentCapability]
    default_policies: Dict[str, Any] = {}
