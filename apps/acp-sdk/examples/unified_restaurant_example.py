#!/usr/bin/env python3
"""
Unified Restaurant Example

This example demonstrates the new unified skill architecture where all operations
go through ACP skills with merchant-specific customization.
"""

import asyncio
from acp_sdk import (
    create_acp_server,
    ACPBaseExecutor,
    AgentCapability,
    OrderManagementSkill,
    PaymentProcessingSkill,
    OfferManagementSkill,
    OrderResult,
    PaymentResult,
    OfferValidationResult,
    OrderSummary,
    PaymentDetails,
    OrderStatus,
    PaymentStatus,
)
from decimal import Decimal
from datetime import datetime


class UnifiedRestaurantOrderSkill(OrderManagementSkill):
    """Unified restaurant order management skill."""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.orders = {}
    
    async def _handle_order_task(self, task):
        """Handle order-specific tasks with custom business logic."""
        # Generate order ID
        order_id = f"unified_{self.config.agent_id}_{len(self.orders) + 1}"
        
        # Calculate totals with custom business rules
        subtotal = sum(item.total for item in task.items)
        
        # Custom business rule: Free delivery for orders over $30
        delivery_fee = Decimal('0.00') if subtotal > 30 else Decimal('5.00')
        
        tax = subtotal * Decimal('0.08')  # 8% tax
        total = subtotal + tax + delivery_fee
        
        # Create order summary
        order = OrderSummary(
            order_id=order_id,
            restaurant_id=self.config.agent_id,
            items=task.items,
            subtotal=subtotal,
            tax=tax,
            delivery_fee=delivery_fee,
            total=total,
            status=OrderStatus.CREATED,
            created_at=datetime.now()
        )
        
        # Store order
        self.orders[order_id] = order
        
        return OrderResult(
            task_id=task.task_id,
            success=True,
            data={"order_id": order_id, "delivery_fee": delivery_fee},
            order=order
        )


class UnifiedRestaurantPaymentSkill(PaymentProcessingSkill):
    """Unified restaurant payment processing skill."""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.payments = {}
    
    async def _process_payment(self, payment_request):
        """Process payment with custom business logic."""
        # Generate payment ID
        payment_id = f"unified_pay_{self.config.agent_id}_{len(self.payments) + 1}"
        
        # Custom business rule: Add 2% service fee for credit card payments
        service_fee = Decimal('0.00')
        if payment_request.payment_method.value == "credit_card":
            service_fee = payment_request.amount * Decimal('0.02')
        
        # Mock payment processing
        payment_result = PaymentDetails(
            payment_id=payment_id,
            order_id=payment_request.order_id,
            amount=payment_request.amount + service_fee,
            status=PaymentStatus.COMPLETED,
            processed_at=datetime.now()
        )
        
        # Store payment
        self.payments[payment_id] = payment_result
        
        return PaymentResult(
            task_id=f"task_{datetime.now().timestamp()}",
            success=True,
            data={"payment_id": payment_id, "service_fee": service_fee},
            payment=payment_result
        )


class UnifiedRestaurantOfferSkill(OfferManagementSkill):
    """Unified restaurant offer management skill."""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.offers = {
            "welcome_discount": {
                "title": "Welcome Discount",
                "description": "10% off your first order",
                "discount": Decimal('0.10'),
                "min_order": Decimal('15.00'),
                "max_discount": Decimal('10.00')
            },
            "lunch_rush": {
                "title": "Lunch Rush Special",
                "description": "15% off lunch orders",
                "discount": Decimal('0.15'),
                "valid_hours": (11, 14)  # 11 AM to 2 PM
            }
        }
    
    async def _validate_offer(self, offer_id: str, items: list):
        """Validate offer with custom business rules."""
        if offer_id not in self.offers:
            return OfferValidationResult(
                task_id=f"task_{datetime.now().timestamp()}",
                success=True,
                is_valid=False,
                discount_amount=Decimal('0.00'),
                restrictions_violated=["Offer not found"]
            )
        
        offer = self.offers[offer_id]
        subtotal = sum(item.total for item in items)
        
        # Custom business rules
        if offer_id == "welcome_discount":
            # Check minimum order amount
            if subtotal < offer["min_order"]:
                return OfferValidationResult(
                    task_id=f"task_{datetime.now().timestamp()}",
                    success=True,
                    is_valid=False,
                    discount_amount=Decimal('0.00'),
                    restrictions_violated=[f"Minimum order of ${offer['min_order']} required"]
                )
            
            # Calculate discount with maximum cap
            discount_amount = min(subtotal * offer["discount"], offer["max_discount"])
            
        elif offer_id == "lunch_rush":
            # Check if current time is within lunch hours
            current_hour = datetime.now().hour
            if not (offer["valid_hours"][0] <= current_hour <= offer["valid_hours"][1]):
                return OfferValidationResult(
                    task_id=f"task_{datetime.now().timestamp()}",
                    success=True,
                    is_valid=False,
                    discount_amount=Decimal('0.00'),
                    restrictions_violated=["Lunch rush special only valid 11 AM - 2 PM"]
                )
            
            discount_amount = subtotal * offer["discount"]
        
        else:
            discount_amount = subtotal * offer["discount"]
        
        return OfferValidationResult(
            task_id=f"task_{datetime.now().timestamp()}",
            success=True,
            is_valid=True,
            discount_amount=discount_amount,
            restrictions_violated=[]
        )


class UnifiedRestaurantExecutor(ACPBaseExecutor):
    """Unified restaurant executor demonstrating the new architecture."""
    
    def _create_custom_skills(self):
        """Create custom skills that override ACP skill behavior."""
        return [
            UnifiedRestaurantOrderSkill(self.config),
            UnifiedRestaurantPaymentSkill(self.config),
            UnifiedRestaurantOfferSkill(self.config)
        ]
    
    async def _handle_general_conversation(self, query: str, context_id: str) -> str:
        """Handle general conversation with restaurant-specific responses."""
        return f"Welcome to {self.config.name}! I can help you with orders, payments, and offers. We have special business rules like free delivery on orders over $30 and lunch rush discounts!"


def main():
    """Create and run a unified restaurant agent."""
    
    # Create the server with the new unified architecture
    server = create_acp_server(
        agent_id="unified_restaurant",
        name="Unified Restaurant",
        description="A restaurant demonstrating the unified ACP skill architecture",
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
        executor_class=UnifiedRestaurantExecutor,
        host="localhost",
        port=4002
    )
    
    print("Starting Unified Restaurant Agent...")
    print("This demonstrates the new unified skill architecture where:")
    print("- All operations go through ACP skills")
    print("- Custom business logic is implemented in custom skills")
    print("- Merchant-specific rules (free delivery, service fees, time-based offers)")
    print("- Single code path for all operations")
    print()
    
    server.run()


if __name__ == "__main__":
    main()
