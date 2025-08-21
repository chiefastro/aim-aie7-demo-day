#!/usr/bin/env python3
"""
Simple Restaurant Agent Example

This example demonstrates how to create a restaurant A2A agent with minimal code
using the refactored ACP SDK.
"""

import asyncio
from acp_sdk import (
    create_acp_server,
    ACPBaseExecutor,
    AgentCapability,
    AgentCapability,
    OrderManagementSkill,
    PaymentProcessingSkill,
    OrderItem,
    OrderSummary,
    OrderStatus,
    PaymentDetails,
    PaymentStatus,
    PaymentRequest,
    PaymentMethod,
)
from decimal import Decimal
from datetime import datetime


class SimpleRestaurantSkill(OrderManagementSkill):
    """Simple restaurant-specific order management skill."""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.orders = {}  # Simple in-memory order storage
    
    async def _handle_order_task(self, task):
        """Handle order-specific tasks."""
        # Generate order ID
        order_id = f"ord_{self.config.agent_id}_{len(self.orders) + 1}"
        
        # Calculate totals
        subtotal = sum(item.total for item in task.items)
        tax = subtotal * Decimal('0.08')  # 8% tax
        total = subtotal + tax
        
        # Create order summary
        order = OrderSummary(
            order_id=order_id,
            restaurant_id=self.config.agent_id,
            items=task.items,
            subtotal=subtotal,
            tax=tax,
            total=total,
            status=OrderStatus.CREATED,
            created_at=datetime.now()
        )
        
        # Store order
        self.orders[order_id] = order
        
        return OrderResult(
            task_id=task.task_id,
            success=True,
            data={"order_id": order_id},
            order=order
        )


class SimplePaymentSkill(PaymentProcessingSkill):
    """Simple restaurant-specific payment processing skill."""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.payments = {}  # Simple in-memory payment storage
    
    async def _process_payment(self, payment_request):
        """Process a restaurant payment."""
        # Generate payment ID
        payment_id = f"pay_{self.config.agent_id}_{len(self.payments) + 1}"
        
        # Mock payment processing
        payment_result = PaymentDetails(
            payment_id=payment_id,
            order_id=payment_request.order_id,
            amount=payment_request.amount,
            status=PaymentStatus.COMPLETED,
            processed_at=datetime.now()
        )
        
        # Store payment
        self.payments[payment_id] = payment_result
        
        return PaymentResult(
            task_id=f"task_{datetime.now().timestamp()}",
            success=True,
            data={"payment_id": payment_id},
            payment=payment_result
        )


class SimpleRestaurantExecutor(ACPBaseExecutor):
    """Simple restaurant executor with custom skills."""
    
    def _create_custom_skills(self):
        """Create custom skills for this restaurant."""
        return [
            SimpleRestaurantSkill(self.config),
            SimplePaymentSkill(self.config)
        ]
    
    async def _handle_general_conversation(self, query: str, context_id: str) -> str:
        """Handle general conversation with restaurant-specific responses."""
        return f"Welcome to {self.config.name}! I can help you place orders, check our menu, and process payments. What would you like to do today?"


def main():
    """Create and run a simple restaurant agent."""
    
    # Create the server with minimal configuration
    server = create_acp_server(
        agent_id="simple_restaurant",
        name="Simple Restaurant",
        description="A simple restaurant agent with basic ordering capabilities",
        osf_endpoint="http://localhost:8001/.well-known/osf.json",
        menu_endpoint="http://localhost:8001/a2a/menu",
        capabilities=[
            AgentCapability.PRESENT_OFFER,
            AgentCapability.INITIATE_CHECKOUT,
            AgentCapability.CONFIRM_ORDER,
            AgentCapability.VALIDATE_OFFER,
            AgentCapability.PROCESS_PAYMENT,
            AgentCapability.GET_MENU,
        ],
        executor_class=SimpleRestaurantExecutor,
        host="localhost",
        port=4001
    )
    
    # Run the server
    server.run()


if __name__ == "__main__":
    main()
