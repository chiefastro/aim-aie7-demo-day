"""
ACP MCP Server Data Models - Standardized request/response structures.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


class CommerceOperation(str, Enum):
    """Standard commerce operations supported by ACP MCP."""
    ORDER_FOOD = "order_food"
    VALIDATE_OFFER = "validate_offer"
    PROCESS_PAYMENT = "process_payment"
    TRACK_ORDER = "track_order"
    GET_MENU = "get_menu"
    DISCOVER_MERCHANTS = "discover_merchants"


class OrderStatus(str, Enum):
    """Standard order status values."""
    CREATED = "created"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class PaymentStatus(str, Enum):
    """Standard payment status values."""
    PENDING = "pending"
    AUTHORIZED = "authorized"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class OrderItem(BaseModel):
    """Individual item in an order."""
    name: str = Field(..., description="Item name")
    quantity: int = Field(..., ge=1, description="Quantity ordered")
    price: Optional[Decimal] = Field(None, description="Unit price")
    sku: Optional[str] = Field(None, description="Stock keeping unit")
    notes: Optional[str] = Field(None, description="Special instructions")


class MerchantInfo(BaseModel):
    """Information about a merchant."""
    merchant_id: str = Field(..., description="Unique merchant identifier")
    name: str = Field(..., description="Merchant name")
    description: Optional[str] = Field(None, description="Merchant description")
    agent_url: str = Field(..., description="A2A agent endpoint URL")
    capabilities: List[str] = Field(default_factory=list, description="Supported capabilities")
    location: Optional[Dict[str, Any]] = Field(None, description="Merchant location")
    cuisine_type: Optional[str] = Field(None, description="Type of cuisine (for restaurants)")
    rating: Optional[float] = Field(None, description="Merchant rating")
    is_acp_compliant: bool = Field(True, description="Whether merchant is ACP compliant")


class CommerceRequest(BaseModel):
    """Base request for commerce operations."""
    operation: CommerceOperation = Field(..., description="Commerce operation to perform")
    merchant_id: str = Field(..., description="Target merchant identifier")
    user_id: Optional[str] = Field(None, description="User making the request")
    session_id: Optional[str] = Field(None, description="User session identifier")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional request metadata")
    request_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique request identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Request timestamp")


class OrderRequest(CommerceRequest):
    """Request for ordering food."""
    operation: CommerceOperation = Field(CommerceOperation.ORDER_FOOD, description="Order food operation")
    items: List[OrderItem] = Field(..., description="Items to order")
    offer_id: Optional[str] = Field(None, description="Offer to apply")
    pickup: bool = Field(True, description="Whether this is pickup or delivery")
    delivery_address: Optional[Dict[str, str]] = Field(None, description="Delivery address if applicable")
    special_instructions: Optional[str] = Field(None, description="Special order instructions")


class PaymentRequest(CommerceRequest):
    """Request for payment processing."""
    operation: CommerceOperation = Field(CommerceOperation.PROCESS_PAYMENT, description="Process payment operation")
    order_id: str = Field(..., description="Order to pay for")
    amount: Decimal = Field(..., description="Amount to charge")
    payment_method: str = Field(..., description="Payment method to use")
    payment_details: Dict[str, Any] = Field(..., description="Payment method specific details")


class OfferValidationRequest(CommerceRequest):
    """Request for offer validation."""
    operation: CommerceOperation = Field(CommerceOperation.VALIDATE_OFFER, description="Validate offer operation")
    offer_id: str = Field(..., description="Offer to validate")
    items: List[OrderItem] = Field(..., description="Items to validate against")


class MenuItem(BaseModel):
    """Menu item information."""
    name: str = Field(..., description="Item name")
    description: Optional[str] = Field(None, description="Item description")
    price: Decimal = Field(..., description="Item price")
    sku: Optional[str] = Field(None, description="Stock keeping unit")
    category: Optional[str] = Field(None, description="Menu category")
    available: bool = Field(True, description="Whether item is available")
    allergens: List[str] = Field(default_factory=list, description="Allergen information")


class OrderSummary(BaseModel):
    """Summary of an order."""
    order_id: str = Field(..., description="Unique order identifier")
    merchant_id: str = Field(..., description="Merchant identifier")
    items: List[OrderItem] = Field(..., description="Ordered items")
    subtotal: Decimal = Field(..., description="Subtotal before tax/fees")
    tax: Decimal = Field(..., description="Tax amount")
    delivery_fee: Optional[Decimal] = Field(None, description="Delivery fee if applicable")
    tip: Optional[Decimal] = Field(None, description="Tip amount")
    total: Decimal = Field(..., description="Total amount")
    status: OrderStatus = Field(..., description="Current order status")
    estimated_ready_time: Optional[datetime] = Field(None, description="Estimated ready time")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Order creation time")


class PaymentSummary(BaseModel):
    """Summary of payment processing."""
    payment_id: str = Field(..., description="Unique payment identifier")
    order_id: str = Field(..., description="Order that was paid for")
    amount: Decimal = Field(..., description="Amount charged")
    status: PaymentStatus = Field(..., description="Payment status")
    transaction_id: Optional[str] = Field(None, description="External transaction ID")
    processed_at: datetime = Field(default_factory=datetime.utcnow, description="Payment processing time")


class OfferValidationResult(BaseModel):
    """Result of offer validation."""
    is_valid: bool = Field(..., description="Whether the offer is valid")
    discount_amount: Optional[Decimal] = Field(None, description="Calculated discount amount")
    restrictions_violated: List[str] = Field(default_factory=list, description="Violated restrictions")
    message: Optional[str] = Field(None, description="Validation message")


class CommerceResponse(BaseModel):
    """Base response for commerce operations."""
    success: bool = Field(..., description="Whether the operation succeeded")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    error_message: Optional[str] = Field(None, description="Error message if operation failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional response metadata")
    request_id: str = Field(..., description="Request identifier this response corresponds to")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class MerchantDiscovery(BaseModel):
    """Result of merchant discovery."""
    merchants: List[MerchantInfo] = Field(..., description="Discovered merchants")
    total_count: int = Field(..., description="Total number of merchants found")
    query: Optional[str] = Field(None, description="Search query used")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Applied filters")


class MenuResponse(BaseModel):
    """Response containing menu information."""
    merchant_id: str = Field(..., description="Merchant identifier")
    menu_items: List[MenuItem] = Field(..., description="Available menu items")
    categories: List[str] = Field(..., description="Available menu categories")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last menu update time")
