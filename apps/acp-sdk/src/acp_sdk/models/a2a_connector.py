"""
ACP Data Models - Standardized data structures for commerce operations.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


class TaskType(str, Enum):
    """Standard ACP task types."""
    ORDER_FOOD = "order_food"
    VALIDATE_OFFER = "validate_offer"
    PROCESS_PAYMENT = "process_payment"
    TRACK_ORDER = "track_order"
    MODIFY_ORDER = "modify_order"
    CANCEL_ORDER = "cancel_order"
    GET_MENU = "get_menu"
    APPLY_COUPON = "apply_coupon"


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


class PaymentMethod(str, Enum):
    """Standard payment methods."""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    CASH = "cash"
    DIGITAL_WALLET = "digital_wallet"
    BANK_TRANSFER = "bank_transfer"


class AgentCapability(str, Enum):
    """Standard ACP agent capabilities."""
    PRESENT_OFFER = "present_offer"
    INITIATE_CHECKOUT = "initiate_checkout"
    CONFIRM_ORDER = "confirm_order"
    VALIDATE_OFFER = "validate_offer"
    PROCESS_PAYMENT = "process_payment"
    GET_MENU = "get_menu"
    TRACK_ORDER = "track_order"


class ACPConfig(BaseModel):
    """Standardized configuration for ACP agents."""
    agent_id: str = Field(..., description="Unique agent identifier")
    name: str = Field(..., description="Agent display name")
    description: str = Field(..., description="Agent description")
    version: str = Field("1.0.0", description="Agent version")
    
    # Endpoints
    osf_endpoint: str = Field(..., description="OSF discovery endpoint")
    menu_endpoint: str = Field(..., description="Menu retrieval endpoint")
    a2a_endpoints: Dict[str, str] = Field(default_factory=dict, description="A2A operation endpoints")
    
    # Capabilities
    capabilities: List[AgentCapability] = Field(default_factory=list, description="Supported capabilities")
    
    # Configuration
    default_policies: Dict[str, Any] = Field(default_factory=dict, description="Default agent policies")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    # Server configuration
    host: str = Field("localhost", description="Server host")
    port: int = Field(4001, description="Server port")
    
    @property
    def restaurant_id(self) -> str:
        """Backward compatibility property."""
        return self.agent_id
    
    @property
    def well_known_endpoint(self) -> str:
        """Generate well-known endpoint URL."""
        return f"http://{self.host}:{self.port}/.well-known/agent-card.json"


class OrderItem(BaseModel):
    """Individual item in an order."""
    name: str = Field(..., description="Item name")
    quantity: int = Field(..., ge=1, description="Quantity ordered")
    price: Decimal = Field(..., ge=0, description="Unit price")
    sku: Optional[str] = Field(None, description="Stock keeping unit")
    notes: Optional[str] = Field(None, description="Special instructions")
    
    @property
    def total(self) -> Decimal:
        """Calculate total price for this item."""
        return self.price * self.quantity


class OrderSummary(BaseModel):
    """Summary of an order."""
    order_id: str = Field(..., description="Unique order identifier")
    restaurant_id: str = Field(..., description="Restaurant identifier")
    items: List[OrderItem] = Field(..., description="Ordered items")
    subtotal: Decimal = Field(..., description="Subtotal before tax/fees")
    tax: Decimal = Field(..., description="Tax amount")
    delivery_fee: Optional[Decimal] = Field(None, description="Delivery fee if applicable")
    tip: Optional[Decimal] = Field(None, description="Tip amount")
    total: Decimal = Field(..., description="Total amount")
    status: OrderStatus = Field(..., description="Current order status")
    estimated_ready_time: Optional[datetime] = Field(None, description="Estimated ready time")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Order creation time")
    
    @validator('total')
    def validate_total(cls, v, values):
        """Ensure total matches calculated sum."""
        if 'subtotal' in values and 'tax' in values:
            calculated = values['subtotal'] + values['tax']
            if values.get('delivery_fee'):
                calculated += values['delivery_fee']
            if values.get('tip'):
                calculated += values['tip']
            if abs(v - calculated) > Decimal('0.01'):
                raise ValueError("Total must equal subtotal + tax + fees + tip")
        return v


class OfferDetails(BaseModel):
    """Details of a merchant offer."""
    offer_id: str = Field(..., description="Unique offer identifier")
    title: str = Field(..., description="Offer title")
    description: str = Field(..., description="Offer description")
    discount_type: str = Field(..., description="Type of discount (percentage, fixed, etc.)")
    discount_value: Decimal = Field(..., description="Discount amount or percentage")
    minimum_spend: Optional[Decimal] = Field(None, description="Minimum order amount required")
    valid_until: datetime = Field(..., description="Offer expiration time")
    restrictions: List[str] = Field(default_factory=list, description="Offer restrictions")
    applicable_items: List[str] = Field(default_factory=list, description="Items this offer applies to")


class PaymentRequest(BaseModel):
    """Payment processing request."""
    order_id: str = Field(..., description="Order to pay for")
    amount: Decimal = Field(..., description="Amount to charge")
    payment_method: PaymentMethod = Field(..., description="Payment method to use")
    payment_details: Dict[str, Any] = Field(..., description="Payment method specific details")
    billing_address: Optional[Dict[str, str]] = Field(None, description="Billing address if required")


class PaymentDetails(BaseModel):
    """Details of payment processing."""
    payment_id: str = Field(..., description="Unique payment identifier")
    order_id: str = Field(..., description="Order that was paid for")
    amount: Decimal = Field(..., description="Amount charged")
    status: PaymentStatus = Field(..., description="Payment status")
    transaction_id: Optional[str] = Field(None, description="External transaction ID")
    processed_at: datetime = Field(default_factory=datetime.utcnow, description="Payment processing time")
    error_message: Optional[str] = Field(None, description="Error message if payment failed")


class CommerceTask(BaseModel):
    """Base class for all ACP commerce tasks."""
    task_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique task identifier")
    task_type: TaskType = Field(..., description="Type of commerce task")
    restaurant_id: str = Field(..., description="Target restaurant identifier")
    user_id: Optional[str] = Field(None, description="User making the request")
    session_id: Optional[str] = Field(None, description="User session identifier")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional task metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Task creation time")


class OrderTask(CommerceTask):
    """Task for order management operations."""
    task_type: TaskType = Field(TaskType.ORDER_FOOD, description="Order management task")
    items: List[OrderItem] = Field(..., description="Items to order")
    offer_id: Optional[str] = Field(None, description="Offer to apply")
    pickup: bool = Field(True, description="Whether this is pickup or delivery")
    delivery_address: Optional[Dict[str, str]] = Field(None, description="Delivery address if applicable")
    special_instructions: Optional[str] = Field(None, description="Special order instructions")


class PaymentTask(CommerceTask):
    """Task for payment processing operations."""
    task_type: TaskType = Field(TaskType.PROCESS_PAYMENT, description="Payment processing task")
    order_id: str = Field(..., description="Order to pay for")
    payment_request: PaymentRequest = Field(..., description="Payment details")


class OfferTask(CommerceTask):
    """Task for offer management operations."""
    task_type: TaskType = Field(TaskType.VALIDATE_OFFER, description="Offer validation task")
    offer_id: str = Field(..., description="Offer to validate")
    items: List[OrderItem] = Field(..., description="Items to validate against")


class InventoryTask(CommerceTask):
    """Task for inventory management operations."""
    task_type: TaskType = Field(TaskType.GET_MENU, description="Inventory query task")
    category: Optional[str] = Field(None, description="Menu category to query")
    include_unavailable: bool = Field(False, description="Whether to include unavailable items")


class CustomerServiceTask(CommerceTask):
    """Task for customer service operations."""
    task_type: TaskType = Field(TaskType.TRACK_ORDER, description="Customer service task")
    order_id: Optional[str] = Field(None, description="Order to track")
    inquiry_type: str = Field(..., description="Type of customer inquiry")
    message: Optional[str] = Field(None, description="Customer message or inquiry")


class CommerceResult(BaseModel):
    """Base class for all ACP commerce task results."""
    task_id: str = Field(..., description="Task identifier this result corresponds to")
    success: bool = Field(..., description="Whether the task succeeded")
    data: Optional[Dict[str, Any]] = Field(None, description="Task result data")
    error_message: Optional[str] = Field(None, description="Error message if task failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional result metadata")
    completed_at: datetime = Field(default_factory=datetime.utcnow, description="Task completion time")


class OrderResult(CommerceResult):
    """Result of order management operations."""
    order: Optional[OrderSummary] = Field(None, description="Created or modified order")
    offer_applied: Optional[OfferDetails] = Field(None, description="Offer that was applied")


class PaymentResult(CommerceResult):
    """Result of payment processing operations."""
    payment: Optional[PaymentDetails] = Field(None, description="Payment processing result")


class OfferValidationResult(CommerceResult):
    """Result of offer validation operations."""
    is_valid: bool = Field(..., description="Whether the offer is valid")
    discount_amount: Optional[Decimal] = Field(None, description="Calculated discount amount")
    restrictions_violated: List[str] = Field(default_factory=list, description="Violated restrictions")


class InventoryResult(CommerceResult):
    """Result of inventory query operations."""
    menu_items: List[Dict[str, Any]] = Field(default_factory=list, description="Available menu items")
    categories: List[str] = Field(default_factory=list, description="Available menu categories")


class CustomerServiceResult(CommerceResult):
    """Result of customer service operations."""
    response: str = Field(..., description="Response to customer inquiry")
    order_status: Optional[OrderStatus] = Field(None, description="Order status if applicable")
    estimated_time: Optional[str] = Field(None, description="Estimated time if applicable")
