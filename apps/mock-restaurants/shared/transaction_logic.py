import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from .models import (
    OrderStatus, OrderItem, OrderResponse, ValidateOfferResponse,
    MenuItem, CreateOrderRequest, ConfirmOrderRequest, SettleOrderRequest
)

class MockTransactionLogic:
    def __init__(self, restaurant_id: str, data_dir: str):
        self.restaurant_id = restaurant_id
        self.data_dir = data_dir
        self.orders: Dict[str, OrderResponse] = {}
        self.menu_items: Dict[str, MenuItem] = {}
        self.offers: Dict[str, dict] = {}
        self._load_data()
    
    def _load_data(self):
        """Load menu items and offers from data directory"""
        # Load menu items
        menu_file = os.path.join(self.data_dir, "menu.json")
        if os.path.exists(menu_file):
            with open(menu_file, 'r') as f:
                menu_data = json.load(f)
                for item in menu_data.get("items", []):
                    menu_item = MenuItem(**item)
                    self.menu_items[menu_item.id] = menu_item
        
        # Load offers
        offers_dir = os.path.join(self.data_dir, ".well-known", "offers")
        if os.path.exists(offers_dir):
            for filename in os.listdir(offers_dir):
                if filename.endswith(".json"):
                    offer_id = filename.replace(".json", "")
                    with open(os.path.join(offers_dir, filename), 'r') as f:
                        self.offers[offer_id] = json.load(f)
    
    def create_order(self, request: CreateOrderRequest) -> OrderResponse:
        """Create a new order"""
        order_id = f"order_{self.restaurant_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.orders) + 1}"
        
        # Calculate totals
        subtotal = sum(item.price * item.quantity for item in request.items)
        tax = subtotal * 0.08  # 8% tax
        discount = 0.0
        
        # Apply offer if provided
        offer_applied = None
        if request.offer_id and request.offer_id in self.offers:
            offer = self.offers[request.offer_id]
            validation = self.validate_offer(request.offer_id, request.items, request.order_type)
            if validation.valid:
                discount = validation.discount_amount
                offer_applied = request.offer_id
        
        total = subtotal + tax - discount
        
        order = OrderResponse(
            order_id=order_id,
            status=OrderStatus.CREATED,
            items=request.items,
            subtotal=subtotal,
            tax=tax,
            discount=discount,
            total=total,
            offer_applied=offer_applied,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.orders[order_id] = order
        return order
    
    def get_order(self, order_id: str) -> Optional[OrderResponse]:
        """Get order by ID"""
        return self.orders.get(order_id)
    
    def confirm_order(self, order_id: str, request: ConfirmOrderRequest) -> Optional[OrderResponse]:
        """Confirm an order"""
        order = self.orders.get(order_id)
        if not order or order.status != OrderStatus.CREATED:
            return None
        
        order.status = OrderStatus.CONFIRMED
        order.updated_at = datetime.now()
        order.estimated_ready_time = request.estimated_ready_time or (
            datetime.now() + timedelta(minutes=25)
        )
        
        return order
    
    def settle_order(self, order_id: str, request: SettleOrderRequest) -> Optional[OrderResponse]:
        """Settle payment for an order"""
        order = self.orders.get(order_id)
        if not order or order.status != OrderStatus.CONFIRMED:
            return None
        
        # Mock payment processing
        if request.payment_method == "credit_card":
            # Simulate payment processing delay
            import time
            time.sleep(0.1)
        
        order.status = OrderStatus.SETTLED
        order.updated_at = datetime.now()
        
        return order
    
    def validate_offer(self, offer_id: str, items: List[OrderItem], order_type: str) -> ValidateOfferResponse:
        """Validate if an offer can be applied to an order"""
        if offer_id not in self.offers:
            return ValidateOfferResponse(
                valid=False,
                message="Offer not found",
                restrictions=["Invalid offer ID"]
            )
        
        offer = self.offers[offer_id]
        restrictions = []
        
        # Check minimum spend
        subtotal = sum(item.price * item.quantity for item in items)
        min_spend = offer.get("terms", {}).get("min_spend", 0)
        if subtotal < min_spend:
            restrictions.append(f"Minimum spend of ${min_spend} required")
        
        # Check order type restrictions
        valid_types = offer.get("terms", {}).get("valid_order_types", ["dine-in", "takeout"])
        if order_type not in valid_types:
            restrictions.append(f"Offer not valid for {order_type} orders")
        
        # Check time restrictions
        current_hour = datetime.now().hour
        valid_hours = offer.get("terms", {}).get("valid_hours", {})
        if valid_hours:
            start_hour = int(valid_hours.get("start", "0").split(":")[0])
            end_hour = int(valid_hours.get("end", "23").split(":")[0])
            if not (start_hour <= current_hour <= end_hour):
                restrictions.append("Offer not valid at current time")
        
        if restrictions:
            return ValidateOfferResponse(
                valid=False,
                message="Offer cannot be applied",
                restrictions=restrictions
            )
        
        # Calculate discount
        discount_amount = offer.get("bounty", {}).get("amount", 0)
        max_discount = offer.get("terms", {}).get("max_discount", discount_amount)
        discount_amount = min(discount_amount, max_discount)
        
        return ValidateOfferResponse(
            valid=True,
            discount_amount=discount_amount,
            message="Offer is valid and can be applied"
        )
    
    def get_menu(self) -> Dict[str, List[MenuItem]]:
        """Get restaurant menu organized by categories"""
        categories = {}
        for item in self.menu_items.values():
            if item.category not in categories:
                categories[item.category] = []
            categories[item.category].append(item)
        return categories
