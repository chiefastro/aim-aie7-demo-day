"""
Agentic Commerce Protocol (ACP) SDK for Python.

This SDK provides standardized commerce skills for A2A agents,
enabling universal commerce integration across all merchants.
"""

from .core import ACPAgent, CommerceSkills
from .skills import (
    OrderManagementSkill,
    PaymentProcessingSkill,
    OfferManagementSkill,
    InventoryManagementSkill,
    CustomerServiceSkill,
)
from .models import (
    CommerceTask,
    CommerceResult,
    OrderTask,
    PaymentTask,
    OfferTask,
    InventoryTask,
    CustomerServiceTask,
    OrderItem,
    OrderSummary,
    OrderStatus,
    PaymentRequest,
    PaymentDetails,
    PaymentResult,
    PaymentStatus,
    PaymentMethod,
    OfferDetails,
)
from .exceptions import ACPError, SkillExecutionError, ValidationError

__version__ = "0.1.0"
__author__ = "ACP Team"
__email__ = "team@acp.dev"

__all__ = [
    # Core components
    "ACPAgent",
    "CommerceSkills",
    
    # Skills
    "OrderManagementSkill",
    "PaymentProcessingSkill", 
    "OfferManagementSkill",
    "InventoryManagementSkill",
    "CustomerServiceSkill",
    
    # Models
    "CommerceTask",
    "CommerceResult",
    "OrderTask",
    "PaymentTask",
    "OfferTask",
    "InventoryTask",
    "CustomerServiceTask",
    "OrderItem",
    "OrderSummary",
    "OrderStatus",
    "PaymentRequest",
    "PaymentDetails",
    "PaymentResult",
    "PaymentStatus",
    "PaymentMethod",
    "OfferDetails",
    
    # Exceptions
    "ACPError",
    "SkillExecutionError",
    "ValidationError",
]
