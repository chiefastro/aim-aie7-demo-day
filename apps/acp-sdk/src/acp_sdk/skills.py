"""
ACP Commerce Skills - Standardized commerce capabilities for A2A agents.

This module provides base skill classes that merchants can extend
to implement standardized commerce operations while maintaining
compliance with the ACP protocol.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, Union

from a2a.types import AgentSkill

from .exceptions import ACPError, HITLRequiredError, SkillExecutionError, ValidationError
from .models import (
    CommerceResult,
    CommerceTask,
    CustomerServiceResult,
    InventoryResult,
    OfferValidationResult,
    OrderResult,
    OrderTask,
    PaymentResult,
    PaymentTask,
)


class BaseCommerceSkill(ABC):
    """Base class for all ACP commerce skills."""
    
    def __init__(self, skill_name: str, description: str, tags: Optional[List[str]] = None):
        self.skill_name = skill_name
        self.description = description
        self.tags = tags or []
        self.requires_hitl = False
        self.hitl_prompts: List[str] = []
    
    @abstractmethod
    async def execute(self, task: CommerceTask) -> CommerceResult:
        """Execute the commerce skill with the given task."""
        pass
    
    def to_a2a_format(self) -> AgentSkill:
        """Convert skill to A2A agent card format."""
        return AgentSkill(
            id=f"acp_{self.skill_name.lower().replace(' ', '_')}",
            name=self.skill_name,
            description=self.description,
            tags=self.tags,
            examples=[f"Use {self.skill_name.lower()} for commerce operations"],
        )
    
    async def request_human_input(self, prompt: str, options: Optional[List[str]] = None) -> str:
        """Request human input for HITL workflows."""
        self.requires_hitl = True
        self.hitl_prompts.append(prompt)
        
        # In a real implementation, this would integrate with A2A's HITL system
        # For now, we'll raise an exception to indicate HITL is required
        raise HITLRequiredError(
            f"Human input required: {prompt}",
            required_action="user_input",
            user_prompt=prompt
        )


class OrderManagementSkill(BaseCommerceSkill):
    """Standardized order management skill for restaurants."""
    
    def __init__(self):
        super().__init__(
            skill_name="Order Management",
            description="Handle food orders, modifications, and cancellations",
            tags=["commerce", "restaurant", "ordering"]
        )
    
    async def execute(self, task: CommerceTask) -> CommerceResult:
        """Execute order management operations."""
        try:
            if isinstance(task, OrderTask):
                return await self._handle_order_task(task)
            else:
                raise SkillExecutionError(
                    f"Invalid task type for OrderManagementSkill: {type(task)}",
                    skill_name=self.skill_name,
                    task_id=task.task_id
                )
        except Exception as e:
            if isinstance(e, ACPError):
                raise
            raise SkillExecutionError(
                f"Order management failed: {str(e)}",
                skill_name=self.skill_name,
                task_id=task.task_id
            )
    
    async def _handle_order_task(self, task: OrderTask) -> OrderResult:
        """Handle order-specific tasks."""
        # This is the base implementation - merchants should override this
        # to provide their specific order logic while maintaining compliance
        
        # Validate order
        await self._validate_order(task)
        
        # Create order
        order = await self._create_order(task)
        
        # Apply offers if specified
        offer_applied = None
        if task.offer_id:
            offer_applied = await self._apply_offer(task.offer_id, task.items)
        
        return OrderResult(
            task_id=task.task_id,
            success=True,
            order=order,
            offer_applied=offer_applied
        )
    
    async def _validate_order(self, task: OrderTask) -> None:
        """Validate order requirements."""
        # Base validation - merchants can extend this
        if not task.items:
            raise ValidationError("Order must contain at least one item")
        
        for item in task.items:
            if item.quantity <= 0:
                raise ValidationError(f"Invalid quantity for {item.name}: {item.quantity}")
            if item.price < 0:
                raise ValidationError(f"Invalid price for {item.name}: {item.price}")
    
    async def _create_order(self, task: OrderTask) -> Any:
        """Create the order."""
        # This should be implemented by merchants
        raise NotImplementedError("Merchants must implement _create_order")
    
    async def _apply_offer(self, offer_id: str, items: List[Any]) -> Any:
        """Apply an offer to the order."""
        # This should be implemented by merchants
        raise NotImplementedError("Merchants must implement _apply_offer")


class PaymentProcessingSkill(BaseCommerceSkill):
    """Standardized payment processing skill for restaurants."""
    
    def __init__(self):
        super().__init__(
            skill_name="Payment Processing",
            description="Process payments and handle refunds",
            tags=["commerce", "payment", "financial"]
        )
    
    async def execute(self, task: CommerceTask) -> CommerceResult:
        """Execute payment processing operations."""
        try:
            if isinstance(task, PaymentTask):
                return await self._handle_payment_task(task)
            else:
                raise SkillExecutionError(
                    f"Invalid task type for PaymentProcessingSkill: {type(task)}",
                    skill_name=self.skill_name,
                    task_id=task.task_id
                )
        except Exception as e:
            if isinstance(e, ACPError):
                raise
            raise SkillExecutionError(
                f"Payment processing failed: {str(e)}",
                skill_name=self.skill_name,
                task_id=task.task_id
            )
    
    async def _handle_payment_task(self, task: PaymentTask) -> PaymentResult:
        """Handle payment-specific tasks."""
        # Validate payment request
        await self._validate_payment(task.payment_request)
        
        # Process payment
        payment_result = await self._process_payment(task.payment_request)
        
        return PaymentResult(
            task_id=task.task_id,
            success=True,
            payment=payment_result
        )
    
    async def _validate_payment(self, payment_request: Any) -> None:
        """Validate payment request."""
        # Base validation - merchants can extend this
        if payment_request.amount <= 0:
            raise ValidationError("Payment amount must be positive")
        
        if not payment_request.payment_method:
            raise ValidationError("Payment method is required")
    
    async def _process_payment(self, payment_request: Any) -> Any:
        """Process the payment."""
        # This should be implemented by merchants
        raise NotImplementedError("Merchants must implement _process_payment")


class OfferManagementSkill(BaseCommerceSkill):
    """Standardized offer management skill for restaurants."""
    
    def __init__(self):
        super().__init__(
            skill_name="Offer Management",
            description="Validate and apply offers to orders",
            tags=["commerce", "offers", "discounts"]
        )
    
    async def execute(self, task: CommerceTask) -> CommerceResult:
        """Execute offer management operations."""
        try:
            # This skill handles offer validation and application
            # Implementation depends on the specific task type
            raise NotImplementedError("Offer management execution not implemented")
        except Exception as e:
            if isinstance(e, ACPError):
                raise
            raise SkillExecutionError(
                f"Offer management failed: {str(e)}",
                skill_name=self.skill_name,
                task_id=task.task_id
            )


class InventoryManagementSkill(BaseCommerceSkill):
    """Standardized inventory management skill for restaurants."""
    
    def __init__(self):
        super().__init__(
            skill_name="Inventory Management",
            description="Query menu items and check availability",
            tags=["commerce", "inventory", "menu"]
        )
    
    async def execute(self, task: CommerceTask) -> CommerceResult:
        """Execute inventory management operations."""
        try:
            # This skill handles menu queries and availability checks
            # Implementation depends on the specific task type
            raise NotImplementedError("Inventory management execution not implemented")
        except Exception as e:
            if isinstance(e, ACPError):
                raise
            raise SkillExecutionError(
                f"Inventory management failed: {str(e)}",
                skill_name=self.skill_name,
                task_id=task.task_id
            )


class CustomerServiceSkill(BaseCommerceSkill):
    """Standardized customer service skill for restaurants."""
    
    def __init__(self):
        super().__init__(
            skill_name="Customer Service",
            description="Handle customer inquiries and order tracking",
            tags=["commerce", "customer_service", "support"]
        )
    
    async def execute(self, task: CommerceTask) -> CommerceResult:
        """Execute customer service operations."""
        try:
            # This skill handles customer inquiries and order tracking
            # Implementation depends on the specific task type
            raise NotImplementedError("Customer service execution not implemented")
        except Exception as e:
            if isinstance(e, ACPError):
                raise
            raise SkillExecutionError(
                f"Customer service failed: {str(e)}",
                skill_name=self.skill_name,
                task_id=task.task_id
            )


class CommerceSkills:
    """Container for all ACP commerce skills."""
    
    def __init__(self):
        self.skills: Dict[str, BaseCommerceSkill] = {}
        self._initialize_default_skills()
    
    def _initialize_default_skills(self):
        """Initialize default commerce skills."""
        self.add_skill(OrderManagementSkill())
        self.add_skill(PaymentProcessingSkill())
        self.add_skill(OfferManagementSkill())
        self.add_skill(InventoryManagementSkill())
        self.add_skill(CustomerServiceSkill())
    
    def add_skill(self, skill: BaseCommerceSkill):
        """Add a commerce skill."""
        skill_id = f"acp_{skill.skill_name.lower().replace(' ', '_')}"
        self.skills[skill_id] = skill
    
    def get_skill(self, skill_id: str) -> Optional[BaseCommerceSkill]:
        """Get a skill by ID."""
        return self.skills.get(skill_id)
    
    def get_all_skills(self) -> List[BaseCommerceSkill]:
        """Get all registered skills."""
        return list(self.skills.values())
    
    def to_a2a_format(self) -> List[Dict[str, Any]]:
        """Convert all skills to A2A agent card format."""
        return [skill.to_a2a_format() for skill in self.skills.values()]
    
    async def execute_skill(self, skill_id: str, task: CommerceTask) -> CommerceResult:
        """Execute a specific skill with the given task."""
        skill = self.get_skill(skill_id)
        if not skill:
            raise SkillExecutionError(
                f"Skill '{skill_id}' not found",
                skill_name=skill_id,
                task_id=task.task_id
            )
        
        return await skill.execute(task)
