"""
OTTO Portland Example - Demonstrating ACP SDK usage.

This example shows how a restaurant can use the ACP SDK to implement
standardized commerce skills while maintaining their unique business logic.
"""

import asyncio
from datetime import datetime
from decimal import Decimal
from typing import List

from acp_sdk import (
    ACPAgent,
    OrderManagementSkill,
    PaymentProcessingSkill,
    OrderTask,
    PaymentTask,
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


class OttoPortlandOrderSkill(OrderManagementSkill):
    """OTTO Portland's custom order management implementation."""
    
    def __init__(self):
        super().__init__()
        # OTTO Portland specific configuration
        self.minimum_order = Decimal("15.00")
        self.delivery_fee = Decimal("5.00")
        self.tax_rate = Decimal("0.085")  # 8.5% NH state tax
        
    async def _create_order(self, task) -> OrderSummary:
        """Create an order with OTTO Portland's business logic."""
        # Calculate subtotal
        subtotal = sum(item.total for item in task.items)
        
        # Apply minimum order validation
        if subtotal < self.minimum_order:
            raise ValueError(f"Minimum order amount is ${self.minimum_order}")
        
        # Calculate tax
        tax = subtotal * self.tax_rate
        
        # Add delivery fee if not pickup
        delivery_fee = None
        if not task.pickup:
            delivery_fee = self.delivery_fee
        
        # Calculate total
        total = subtotal + tax
        if delivery_fee:
            total += delivery_fee
        
        # Create order summary
        order = OrderSummary(
            order_id=f"otto_{task.task_id}",
            restaurant_id="otto_portland",
            items=task.items,
            subtotal=subtotal,
            tax=tax,
            delivery_fee=delivery_fee,
            total=total,
            status=OrderStatus.CREATED,
            estimated_ready_time=None,  # Will be set by kitchen
        )
        
        print(f"✅ OTTO Portland order created: {order.order_id}")
        print(f"   Items: {len(order.items)}")
        print(f"   Subtotal: ${order.subtotal}")
        print(f"   Tax: ${order.tax}")
        if order.delivery_fee:
            print(f"   Delivery Fee: ${order.delivery_fee}")
        print(f"   Total: ${order.total}")
        
        return order
    
    async def _apply_offer(self, offer_id: str, items: List[OrderItem]) -> OfferDetails:
        """Apply OTTO Portland's offers."""
        # OTTO Portland specific offer logic
        if offer_id == "ofr_002":  # Dinner offer
            subtotal = sum(item.total for item in items)
            if subtotal >= Decimal("25.00"):
                        return OfferDetails(
            offer_id=offer_id,
            title="Dinner Special",
            description="$2.50 back on orders over $25",
            discount_type="cashback",
            discount_value=Decimal("2.50"),
            minimum_spend=Decimal("25.00"),
            valid_until=datetime(2025, 12, 31, 23, 59, 59),  # Set actual expiry
            restrictions=[],
            applicable_items=[]
        )
        
        return None


class OttoPortlandPaymentSkill(PaymentProcessingSkill):
    """OTTO Portland's custom payment processing implementation."""
    
    def __init__(self):
        super().__init__()
        # OTTO Portland accepts these payment methods
        self.accepted_methods = [PaymentMethod.CREDIT_CARD, PaymentMethod.CASH]
        
    async def _validate_payment(self, payment_request) -> None:
        """Validate payment with OTTO Portland's rules."""
        super()._validate_payment(payment_request)
        
        # Check if payment method is accepted
        if payment_request.payment_method not in self.accepted_methods:
            raise ValueError(f"Payment method {payment_request.payment_method} not accepted")
        
        # OTTO Portland specific validations
        if payment_request.payment_method == PaymentMethod.CREDIT_CARD:
            if not payment_request.payment_details.get("card_number"):
                raise ValueError("Credit card number required")
    
    async def _process_payment(self, payment_request) -> PaymentResult:
        """Process payment with OTTO Portland's logic."""
        # Simulate payment processing
        payment_id = f"pay_{payment_request.order_id}"
        
        # OTTO Portland specific payment logic
        if payment_request.payment_method == PaymentMethod.CREDIT_CARD:
            # Simulate credit card processing
            status = PaymentStatus.COMPLETED
            transaction_id = f"txn_{payment_id}"
        else:
            # Cash payment
            status = PaymentStatus.COMPLETED
            transaction_id = None
        
        payment_details = PaymentDetails(
            payment_id=payment_id,
            order_id=payment_request.order_id,
            amount=payment_request.amount,
            status=status,
            transaction_id=transaction_id,
        )
        
        print(f"💳 Payment processed: {payment_id}")
        print(f"   Method: {payment_request.payment_method}")
        print(f"   Amount: ${payment_request.amount}")
        print(f"   Status: {status}")
        
        return payment_details


async def main():
    """Demonstrate OTTO Portland using ACP SDK."""
    print("🍕 OTTO Portland ACP SDK Example")
    print("=" * 50)
    
    # Create OTTO Portland agent using ACP SDK
    otto_agent = ACPAgent(
        agent_id="agt_otto_portland",
        name="OTTO Portland",
        description="Italian pizza restaurant serving authentic Neapolitan-style pizzas",
        capabilities=["extensions", "push_notifications", "state_transition_history"],
        custom_skills=[
            OttoPortlandOrderSkill(),
            OttoPortlandPaymentSkill(),
        ],
        config={
            "merchant_type": "restaurant",
            "cuisine": "italian",
            "location": "Dover, NH",
        }
    )
    
    # Show agent capabilities
    print(f"\n🏪 Agent: {otto_agent.name}")
    print(f"   ID: {otto_agent.agent_id}")
    print(f"   ACP Compliant: {otto_agent.is_acp_compliant()}")
    print(f"   Skills: {len(otto_agent.list_skills())}")
    
    # List available skills
    print("\n🛠️  Available Skills:")
    for skill_info in otto_agent.list_skills():
        print(f"   • {skill_info['name']}: {skill_info['description']}")
    
    # Create a sample order
    print("\n📝 Creating Sample Order:")
    order_items = [
        OrderItem(
            name="Large Cheese Pizza",
            quantity=2,
            price=Decimal("18.99"),
            notes="Extra crispy crust"
        ),
        OrderItem(
            name="Coke",
            quantity=1,
            price=Decimal("2.99")
        )
    ]
    
    order_task = OrderTask(
        restaurant_id="otto_portland",
        items=order_items,
        offer_id="ofr_002",
        pickup=True,
        special_instructions="Please make it extra crispy!"
    )
    
    # Execute the order
    try:
        order_result = await otto_agent.execute_commerce_task(order_task)
        print(f"\n✅ Order completed successfully!")
        print(f"   Task ID: {order_result.task_id}")
        print(f"   Order ID: {order_result.order.order_id}")
        
        # Now process payment
        print("\n💳 Processing Payment:")
        payment_request = PaymentRequest(
            order_id=order_result.order.order_id,
            amount=order_result.order.total,
            payment_method=PaymentMethod.CREDIT_CARD,
            payment_details={
                "card_number": "**** **** **** 1234",
                "expiry": "12/25",
                "cvv": "123"
            }
        )
        
        payment_task = PaymentTask(
            restaurant_id="otto_portland",
            order_id=order_result.order.order_id,
            payment_request=payment_request
        )
        
        payment_result = await otto_agent.execute_commerce_task(payment_task)
        print(f"\n✅ Payment completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    
    # Show health check
    print("\n🏥 Agent Health Check:")
    health = await otto_agent.health_check()
    print(f"   Status: {health['status']}")
    print(f"   Skills: {health['skills_count']}")
    
    print("\n🎉 Example completed!")


if __name__ == "__main__":
    asyncio.run(main())
