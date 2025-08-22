"""
ACP SDK Exceptions - Custom exception classes for commerce operations.
"""

from typing import Any, Dict, Optional


class ACPError(Exception):
    """Base exception for all ACP SDK errors."""
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class SkillExecutionError(ACPError):
    """Raised when a skill fails to execute properly."""
    
    def __init__(
        self, 
        message: str, 
        skill_name: Optional[str] = None,
        task_id: Optional[str] = None,
        **kwargs
    ):
        self.skill_name = skill_name
        self.task_id = task_id
        super().__init__(message, error_code="SKILL_EXECUTION_ERROR", **kwargs)


class ValidationError(ACPError):
    """Raised when input validation fails."""
    
    def __init__(
        self, 
        message: str, 
        field_name: Optional[str] = None,
        value: Optional[Any] = None,
        **kwargs
    ):
        self.field_name = field_name
        self.value = value
        super().__init__(message, error_code="VALIDATION_ERROR", **kwargs)


class ConfigurationError(ACPError):
    """Raised when ACP SDK configuration is invalid."""
    
    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        self.config_key = config_key
        super().__init__(message, error_code="CONFIGURATION_ERROR", **kwargs)


class MerchantNotFoundError(ACPError):
    """Raised when a merchant cannot be found."""
    
    def __init__(self, merchant_id: str, **kwargs):
        self.merchant_id = merchant_id
        super().__init__(
            f"Merchant '{merchant_id}' not found", 
            error_code="MERCHANT_NOT_FOUND",
            **kwargs
        )


class OfferNotFoundError(ACPError):
    """Raised when an offer cannot be found."""
    
    def __init__(self, offer_id: str, **kwargs):
        self.offer_id = offer_id
        super().__init__(
            f"Offer '{offer_id}' not found", 
            error_code="OFFER_NOT_FOUND",
            **kwargs
        )


class OrderNotFoundError(ACPError):
    """Raised when an order cannot be found."""
    
    def __init__(self, order_id: str, **kwargs):
        self.order_id = order_id
        super().__init__(
            f"Order '{order_id}' not found", 
            error_code="ORDER_NOT_FOUND",
            **kwargs
        )


class PaymentError(ACPError):
    """Raised when payment processing fails."""
    
    def __init__(
        self, 
        message: str, 
        payment_method: Optional[str] = None,
        amount: Optional[float] = None,
        **kwargs
    ):
        self.payment_method = payment_method
        self.amount = amount
        super().__init__(message, error_code="PAYMENT_ERROR", **kwargs)


class InsufficientInventoryError(ACPError):
    """Raised when requested items are not available in sufficient quantity."""
    
    def __init__(
        self, 
        item_name: str, 
        requested_quantity: int, 
        available_quantity: int,
        **kwargs
    ):
        self.item_name = item_name
        self.requested_quantity = requested_quantity
        self.available_quantity = available_quantity
        super().__init__(
            f"Insufficient inventory for '{item_name}': requested {requested_quantity}, available {available_quantity}",
            error_code="INSUFFICIENT_INVENTORY",
            **kwargs
        )


class OfferExpiredError(ACPError):
    """Raised when an offer has expired."""
    
    def __init__(self, offer_id: str, expiry_date: str, **kwargs):
        self.offer_id = offer_id
        self.expiry_date = expiry_date
        super().__init__(
            f"Offer '{offer_id}' expired on {expiry_date}",
            error_code="OFFER_EXPIRED",
            **kwargs
        )


class OfferRestrictionViolationError(ACPError):
    """Raised when an offer's restrictions are violated."""
    
    def __init__(
        self, 
        offer_id: str, 
        violations: list[str],
        **kwargs
    ):
        self.offer_id = offer_id
        self.violations = violations
        super().__init__(
            f"Offer '{offer_id}' restrictions violated: {', '.join(violations)}",
            error_code="OFFER_RESTRICTION_VIOLATION",
            **kwargs
        )


class A2ACommunicationError(ACPError):
    """Raised when communication with A2A agent fails."""
    
    def __init__(
        self, 
        message: str, 
        agent_url: Optional[str] = None,
        response_status: Optional[int] = None,
        **kwargs
    ):
        self.agent_url = agent_url
        self.response_status = response_status
        super().__init__(message, error_code="A2A_COMMUNICATION_ERROR", **kwargs)


class HITLRequiredError(ACPError):
    """Raised when human intervention is required to complete a task."""
    
    def __init__(
        self, 
        message: str, 
        required_action: Optional[str] = None,
        user_prompt: Optional[str] = None,
        **kwargs
    ):
        self.required_action = required_action
        self.user_prompt = user_prompt
        super().__init__(message, error_code="HITL_REQUIRED", **kwargs)
