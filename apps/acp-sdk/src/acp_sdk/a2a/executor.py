"""
ACP Base Executor - Standardized A2A executor with minimal boilerplate.

This module provides a base executor class that handles most of the A2A
protocol boilerplate while allowing merchants to focus on their business logic.
"""

import logging
import asyncio
import httpx
import json
from typing import Any, Dict, List, Optional, Callable, Awaitable
from datetime import datetime
from pathlib import Path

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    InternalError,
    InvalidParamsError,
    Part,
    TaskState,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils import (
    new_agent_text_message,
    new_task,
)
from a2a.utils.errors import ServerError

from .models import ACPConfig, AgentCapability, TaskType, CommerceTask, CommerceResult
from .core import ACPAgent
from .exceptions import ACPError, SkillExecutionError

logger = logging.getLogger(__name__)


class ACPBaseExecutor(AgentExecutor):
    """
    Base ACP executor that handles most A2A boilerplate.
    
    Merchants can extend this class and override specific methods to customize
    behavior while inheriting all the standard A2A protocol handling.
    """
    
    def __init__(self, config: ACPConfig):
        self.config = config
        
        # Configure HTTP client
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
            http2=False
        )
        
        # Initialize ACP agent with custom skills
        self.acp_agent = ACPAgent(
            agent_id=config.agent_id,
            name=config.name,
            description=config.description,
            custom_skills=self._create_custom_skills()
        )
        
        # Extract base URL from OSF endpoint
        self.mock_server_base = config.osf_endpoint.replace('/.well-known/osf.json', '')
        
        logger.info(f"ACP Base Executor initialized for {config.name}")

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """Main execution method - handles all A2A protocol boilerplate."""
        error = self._validate_request(context)
        if error:
            raise ServerError(error=InvalidParamsError())

        query = context.get_user_input()
        task = context.current_task
        if not task:
            task = new_task(context.message)  # type: ignore
            await event_queue.enqueue_event(task)
        
        updater = TaskUpdater(event_queue, task.id, task.context_id)
        
        try:
            logger.info(f"Processing query: {query}")
            
            # Try structured ACP task first
            if self._is_structured_acp_task(query):
                response = await self._handle_structured_acp_task(query, updater)
                if response:
                    await updater.add_artifact(
                        [Part(root=TextPart(text=response))],
                        name='acp_structured_task',
                    )
                    await updater.complete()
                    return
            
            # Try ACP operation detection
            if self._is_acp_operation(query):
                response = await self._handle_acp_operation(query, updater)
                if response:
                    await updater.add_artifact(
                        [Part(root=TextPart(text=response))],
                        name='acp_operation',
                    )
                    await updater.complete()
                    return
            
            # Try capability-specific handling
            capability_response = await self._handle_capability_request(query, updater)
            if capability_response:
                await updater.add_artifact(
                    [Part(root=TextPart(text=capability_response))],
                    name='capability_response',
                )
                await updater.complete()
                return
            
            # Fall back to general conversation
            response = await self._handle_general_conversation(query, task.context_id)
            
            if response and len(response.strip()) > 0:
                await updater.add_artifact(
                    [Part(root=TextPart(text=response))],
                    name='general_response',
                )
                await updater.complete()
            else:
                await updater.update_status(
                    TaskState.input_required,
                    new_agent_text_message(
                        "I'm here to help! What would you like to do?",
                        task.context_id,
                        task.id,
                    ),
                    final=True,
                )

        except Exception as e:
            logger.error(f'Error during execution: {e}')
            raise ServerError(error=InternalError()) from e

    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        """Cancel the current task."""
        raise ServerError(error=UnsupportedOperationError())

    async def cleanup(self):
        """Clean up resources."""
        await self.http_client.aclose()

    # ============================================================================
    # Methods that merchants can override for customization
    # ============================================================================

    def _create_custom_skills(self) -> List[Any]:
        """
        Create custom ACP skills for this agent.
        
        Override this method to provide custom skill implementations.
        """
        return []

    async def _handle_general_conversation(self, query: str, context_id: str) -> str:
        """
        Handle general conversation queries.
        
        Override this method to provide custom conversation handling.
        """
        return f"Hello! I'm {self.config.name}. I can help you with orders, offers, and menu information."

    async def _custom_capability_handler(
        self, 
        capability: AgentCapability, 
        payload: Dict[str, Any]
    ) -> Optional[str]:
        """
        Handle custom capability requests.
        
        Override this method to provide custom capability handling.
        """
        return None

    # ============================================================================
    # Internal helper methods (can be overridden if needed)
    # ============================================================================

    def _validate_request(self, context: RequestContext) -> bool:
        """Validate the incoming request."""
        user_input = context.get_user_input()
        if not user_input or not user_input.strip():
            return True  # Invalid - no input
        return False

    def _is_acp_operation(self, query: str) -> bool:
        """Check if the query is an ACP commerce operation."""
        acp_keywords = [
            "order food", "place order", "create order",
            "validate offer", "check offer", "apply offer",
            "process payment", "make payment", "pay for order",
            "get menu", "show menu", "menu items"
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in acp_keywords)

    def _is_structured_acp_task(self, query: str) -> bool:
        """Check if the query is a structured ACP task from A2A client."""
        try:
            task_data = json.loads(query)
            is_structured = (
                isinstance(task_data, dict) and
                "operation" in task_data and
                task_data["operation"] in ["order_food", "validate_offer", "process_payment", "get_menu"]
            )
            return is_structured
        except (json.JSONDecodeError, TypeError):
            return False

    async def _handle_structured_acp_task(self, query: str, updater: TaskUpdater) -> Optional[str]:
        """Handle structured ACP tasks from A2A client."""
        try:
            task_data = json.loads(query)
            operation = task_data.get("operation")
            
            logger.info(f"Handling structured ACP task: {operation}")
            
            if operation == "get_menu":
                return await self._get_menu_structured()
            
            elif operation == "order_food":
                items = task_data.get("items", [])
                offer_id = task_data.get("offer_id")
                pickup = task_data.get("pickup", True)
                delivery_address = task_data.get("delivery_address")
                special_instructions = task_data.get("special_instructions")
                
                return await self._create_order_structured(items, offer_id, pickup, delivery_address, special_instructions)
            
            elif operation == "validate_offer":
                offer_id = task_data.get("offer_id", "default")
                items = task_data.get("items", [])
                return await self._validate_offer_structured(offer_id, items)
            
            elif operation == "process_payment":
                order_id = task_data.get("order_id", "unknown")
                amount = task_data.get("amount", 0.0)
                payment_method = task_data.get("payment_method", "credit_card")
                payment_details = task_data.get("payment_details", {})
                
                return await self._process_payment_structured(order_id, amount, payment_method, payment_details)
            
            else:
                return f"ACP operation '{operation}' not supported by {self.config.name}"
                
        except Exception as e:
            logger.error(f"Error handling structured ACP task: {e}")
            return f"Error processing ACP task: {str(e)}"

    async def _handle_acp_operation(self, query: str, updater: TaskUpdater) -> Optional[str]:
        """Handle ACP commerce operations using ACP skills."""
        try:
            query_lower = query.lower()
            
            if "order food" in query_lower or "place order" in query_lower:
                items = self._extract_order_items_from_query(query)
                if items:
                    task = self._create_order_task(items)
                    result = await self.acp_agent.execute_commerce_task(task)
                    if result.success:
                        return f"Order created successfully! Order ID: {result.data.get('order_id', 'N/A')}"
                    else:
                        return f"Order creation failed: {result.error_message}"
                else:
                    return "Please specify what items you'd like to order."
            
            elif "validate offer" in query_lower or "check offer" in query_lower:
                offer_id = self._extract_offer_id(query)
                if offer_id:
                    task = self._create_offer_task(offer_id, [])
                    result = await self.acp_agent.execute_commerce_task(task)
                    if result.success:
                        return f"Offer {offer_id} is valid!"
                    else:
                        return f"Offer validation failed: {result.error_message}"
                else:
                    return "Please specify which offer to validate."
            
            elif "get menu" in query_lower or "show menu" in query_lower:
                task = self._create_inventory_task()
                result = await self.acp_agent.execute_commerce_task(task)
                if result.success:
                    return f"Menu retrieved successfully for {self.config.name}!"
                else:
                    return f"Menu retrieval failed: {result.error_message}"
            
            else:
                return f"I can help you with orders, offers, and menu information for {self.config.name}."
                
        except Exception as e:
            logger.error(f"Error handling ACP operation: {e}")
            return f"Sorry, I encountered an error processing your request."

    async def _handle_capability_request(self, query: str, updater: TaskUpdater) -> Optional[str]:
        """Handle capability-specific requests."""
        query_lower = query.lower()
        
        # All capability requests should be routed through ACP skills
        # The merchant can customize behavior by overriding _create_custom_skills()
        
        # Check for capability keywords and route to appropriate ACP operations
        if "offer" in query_lower and ("present" in query_lower or "show" in query_lower):
            # Route to ACP offer management
            task = self._create_inventory_task()  # Get menu/offers
            result = await self.acp_agent.execute_commerce_task(task)
            if result.success:
                return f"Here are the current offers from {self.config.name}!"
            else:
                return f"Sorry, I couldn't retrieve offers at this time."
        
        elif "checkout" in query_lower or "order" in query_lower:
            # Route to ACP order management
            items = self._extract_order_items_from_query(query)
            if items:
                task = self._create_order_task(items)
                result = await self.acp_agent.execute_commerce_task(task)
                if result.success:
                    return f"Order initiated successfully! Order ID: {result.data.get('order_id', 'N/A')}"
                else:
                    return f"Order initiation failed: {result.error_message}"
            else:
                return "Please specify what items you'd like to order."
        
        elif "menu" in query_lower:
            # Route to ACP inventory management
            task = self._create_inventory_task()
            result = await self.acp_agent.execute_commerce_task(task)
            if result.success:
                return f"Menu retrieved successfully for {self.config.name}!"
            else:
                return f"Menu retrieval failed: {result.error_message}"
        
        return None

    # ============================================================================
    # Task creation helpers
    # ============================================================================

    def _create_order_task(self, items: List[Dict[str, Any]]) -> CommerceTask:
        """Create an order task from items."""
        from .models import OrderTask, OrderItem
        
        order_items = []
        for item in items:
            order_items.append(OrderItem(
                name=item.get("name", "Unknown"),
                quantity=item.get("quantity", 1),
                price=item.get("price", 0.0)
            ))
        
        return OrderTask(
            task_id=f"task_{datetime.now().timestamp()}",
            restaurant_id=self.config.agent_id,
            items=order_items,
            pickup=True
        )

    def _create_offer_task(self, offer_id: str, items: List[Dict[str, Any]]) -> CommerceTask:
        """Create an offer validation task."""
        from .models import OfferTask, OrderItem
        
        order_items = []
        for item in items:
            order_items.append(OrderItem(
                name=item.get("name", "Unknown"),
                quantity=item.get("quantity", 1),
                price=item.get("price", 0.0)
            ))
        
        return OfferTask(
            task_id=f"task_{datetime.now().timestamp()}",
            restaurant_id=self.config.agent_id,
            offer_id=offer_id,
            items=order_items
        )

    def _create_inventory_task(self) -> CommerceTask:
        """Create an inventory query task."""
        from .models import InventoryTask
        
        return InventoryTask(
            task_id=f"task_{datetime.now().timestamp()}",
            restaurant_id=self.config.agent_id
        )

    # ============================================================================
    # Structured response methods (can be overridden)
    # ============================================================================

    async def _get_menu_structured(self) -> str:
        """Get restaurant menu and return structured JSON."""
        try:
            response = await self.http_client.get(
                self.config.menu_endpoint,
                timeout=30.0
            )
            
            if response.status_code == 200:
                menu_data = response.json()
                
                result = {
                    "menu_items": [],
                    "categories": [],
                    "restaurant_info": menu_data.get('restaurant_info', {})
                }
                
                categories = menu_data.get('categories', {})
                for category_name, items in categories.items():
                    result["categories"].append(category_name)
                    for item in items:
                        menu_item = {
                            "id": item.get('id', ''),
                            "name": item.get('name', ''),
                            "description": item.get('description', ''),
                            "price": item.get('price', 0.0),
                            "category": item.get('category', category_name),
                            "available": item.get('available', True),
                            "dietary_tags": item.get('dietary_tags', [])
                        }
                        result["menu_items"].append(menu_item)
                
                return json.dumps(result)
            else:
                return json.dumps({
                    "error": f"Failed to retrieve menu: {response.status_code}",
                    "menu_items": [],
                    "categories": []
                })
                
        except Exception as e:
            logger.error(f"Error getting menu: {e}")
            return json.dumps({
                "error": f"Error retrieving menu: {str(e)}",
                "menu_items": [],
                "categories": []
            })

    async def _create_order_structured(
        self, 
        items: List[Dict[str, Any]], 
        offer_id: Optional[str] = None, 
        pickup: bool = True, 
        delivery_address: Optional[Dict[str, Any]] = None, 
        special_instructions: Optional[str] = None
    ) -> str:
        """Create order with structured JSON response."""
        try:
            # Calculate order total
            subtotal = 0.0
            for item in items:
                try:
                    price = float(item.get("price", 0.0))
                    quantity = int(item.get("quantity", 1))
                    subtotal += price * quantity
                except (ValueError, TypeError):
                    continue
            
            tax = subtotal * 0.08  # 8% tax
            total = subtotal + tax
            
            # Generate order ID
            order_id = f"ord_{self.config.agent_id}_{int(datetime.now().timestamp())}"
            
            result = {
                "order_id": order_id,
                "restaurant_id": self.config.agent_id,
                "restaurant_name": self.config.name,
                "items": items,
                "subtotal": subtotal,
                "tax": tax,
                "total": total,
                "status": "created",
                "pickup": pickup,
                "delivery_address": delivery_address,
                "special_instructions": special_instructions,
                "offer_id": offer_id,
                "created_at": datetime.now().isoformat()
            }
            
            return json.dumps(result)
                
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            return json.dumps({
                "error": f"Error creating order: {str(e)}",
                "status": "failed"
            })

    async def _validate_offer_structured(self, offer_id: str, items: List[Dict[str, Any]]) -> str:
        """Validate offer with structured JSON response."""
        try:
            result = {
                "is_valid": True,  # Default to valid for demo
                "offer_id": offer_id,
                "restaurant_id": self.config.agent_id,
                "restaurant_name": self.config.name,
                "items": items,
                "discount_amount": 2.50,
                "message": "Offer is valid",
                "restrictions_violated": [],
                "validated_at": datetime.now().isoformat()
            }
            
            return json.dumps(result)
                
        except Exception as e:
            logger.error(f"Error validating offer: {e}")
            return json.dumps({
                "error": f"Error validating offer: {str(e)}",
                "is_valid": False,
                "offer_id": offer_id
            })

    async def _process_payment_structured(
        self, 
        order_id: str, 
        amount: float, 
        payment_method: str, 
        payment_details: Optional[Dict[str, Any]] = None
    ) -> str:
        """Process payment with structured JSON response."""
        try:
            payment_id = f"pay_{order_id}_{int(datetime.now().timestamp())}"
            
            result = {
                "payment_id": payment_id,
                "order_id": order_id,
                "restaurant_id": self.config.agent_id,
                "restaurant_name": self.config.name,
                "amount": amount,
                "payment_method": payment_method,
                "status": "completed",
                "transaction_id": f"txn_{payment_id}",
                "processed_at": datetime.now().isoformat(),
                "receipt_url": f"http://localhost:8001/receipts/{payment_id}"
            }
            
            return json.dumps(result)
                
        except Exception as e:
            logger.error(f"Error processing payment: {e}")
            return json.dumps({
                "error": f"Error processing payment: {str(e)}",
                "payment_id": payment_id,
                "status": "failed"
            })

    # ============================================================================
    # Utility methods (can be overridden)
    # ============================================================================

    def _extract_offer_id(self, query: str) -> str:
        """Extract offer ID from user query."""
        import re
        
        patterns = [
            r'offer\s+(\w+)',
            r'(\w+)\s+offer',
            r'show\s+(\w+)',
            r'(\w+)\s+special'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query.lower())
            if match:
                return match.group(1)
        
        return "lunch_special"

    def _extract_order_info(self, query: str) -> Dict[str, Any]:
        """Extract order information from user query."""
        items = []
        
        food_mapping = {
            "pizza": {"menu_item_id": "pizza_001", "name": "Pizza", "price": 15.0},
            "salad": {"menu_item_id": "salad_001", "name": "Salad", "price": 12.0},
            "pasta": {"menu_item_id": "pasta_001", "name": "Pasta", "price": 16.0},
            "burger": {"menu_item_id": "burger_001", "name": "Burger", "price": 14.0},
            "sandwich": {"menu_item_id": "sandwich_001", "name": "Sandwich", "price": 13.0},
            "soup": {"menu_item_id": "soup_001", "name": "Soup", "price": 8.0}
        }
        
        for food_item, item_data in food_mapping.items():
            if food_item in query.lower():
                items.append({
                    "menu_item_id": item_data["menu_item_id"],
                    "quantity": 1,
                    "price": item_data["price"]
                })
        
        return {
            "offer_id": "lunch_special",
            "items": items
        }

    def _extract_order_items_from_query(self, query: str) -> List[Dict[str, Any]]:
        """Extract order items from a natural language query."""
        items = []
        
        food_mapping = {
            "pizza": {"name": "Pizza", "price": 15.99},
            "salad": {"name": "Salad", "price": 12.99},
            "pasta": {"name": "Pasta", "price": 16.99},
            "burger": {"name": "Burger", "price": 14.99},
            "sandwich": {"name": "Sandwich", "price": 13.99},
            "soup": {"name": "Soup", "price": 8.99}
        }
        
        query_lower = query.lower()
        for food_item, item_data in food_mapping.items():
            if food_item in query_lower:
                items.append({
                    "name": item_data["name"],
                    "quantity": 1,
                    "price": item_data["price"]
                })
        
        return items
