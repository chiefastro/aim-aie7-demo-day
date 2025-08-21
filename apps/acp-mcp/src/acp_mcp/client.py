"""
ACP Client - Client for interacting with ACP-compliant merchant agents.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from uuid import uuid4

import httpx
from a2a.client import A2AClient as BaseA2AClient, A2ACardResolver
from a2a.types import AgentCard, MessageSendParams, SendMessageRequest

from .models import (
    CommerceRequest,
    CommerceResponse,
    MerchantInfo,
    OrderRequest,
    PaymentRequest,
    OfferValidationRequest,
    OrderSummary,
    PaymentSummary,
    OfferValidationResult,
    MenuResponse,
)

logger = logging.getLogger(__name__)


class ACPClient:
    """
    ACP client for interacting with ACP-compliant merchant agents.
    
    This client handles communication with ACP-compliant merchants
    through their A2A agent endpoints, providing a unified interface
    for commerce operations.
    """
    
    def __init__(self, a2a_server_url: str = None, timeout: float = 30.0):
        self.a2a_server_url = a2a_server_url.rstrip('/') if a2a_server_url else None
        self.timeout = timeout
        self.http_client = httpx.AsyncClient(timeout=httpx.Timeout(timeout))
        self.base_client = None
        self.agent_card = None
        self._merchant_cache: Dict[str, MerchantInfo] = {}

    async def _ensure_initialized(self, agent_url: str = None):
        """Ensure the A2A client is initialized with agent card."""
        if self.base_client is None:
            try:
                server_url = agent_url or self.a2a_server_url
                if not server_url:
                    raise ValueError("No A2A server URL provided")
                
                # Try to get agent card from the default path first
                resolver = A2ACardResolver(
                    httpx_client=self.http_client,
                    base_url=server_url
                )
                
                # Fetch public agent card from default path
                logger.info(f"Fetching agent card from: {server_url}/.well-known/agent-card.json")
                self.agent_card = await resolver.get_agent_card()
                logger.info(f"Agent card fetched successfully: {type(self.agent_card)}")
                
                # Initialize A2A client
                self.base_client = BaseA2AClient(
                    httpx_client=self.http_client,
                    agent_card=self.agent_card
                )
                logger.info("A2A client initialized successfully")
                
            except Exception as e:
                logger.error(f"Failed to initialize A2A client with default path: {e}")
                # Fallback to custom path if default fails
                try:
                    resolver = A2ACardResolver(
                        httpx_client=self.http_client,
                        base_url=server_url,
                        agent_card_path="/.well-known/agent.json"
                    )
                    
                    logger.info(f"Trying fallback path: {server_url}/.well-known/agent.json")
                    self.agent_card = await resolver.get_agent_card()
                    
                    self.base_client = BaseA2AClient(
                        httpx_client=self.http_client,
                        agent_card=self.agent_card
                    )
                    logger.info("A2A client initialized successfully with fallback path")
                    
                except Exception as fallback_error:
                    logger.error(f"Failed to initialize A2A client with fallback path: {fallback_error}")
                    raise

    async def discover_merchant(self, agent_url: str) -> Optional[MerchantInfo]:
        """
        Discover merchant information from an A2A agent endpoint.
        
        Args:
            agent_url: URL of the A2A agent endpoint
            
        Returns:
            MerchantInfo if the agent is ACP-compliant, None otherwise
        """
        try:
            await self._ensure_initialized(agent_url)
            
            # Check if agent is ACP-compliant
            if not self._is_acp_compliant(self.agent_card):
                logger.warning(f"Agent at {agent_url} is not ACP-compliant")
                return None
            
            # Extract merchant information
            merchant_info = self._extract_merchant_info(self.agent_card, agent_url)
            
            # Cache the merchant info
            self._merchant_cache[merchant_info.merchant_id] = merchant_info
            
            return merchant_info
            
        except Exception as e:
            logger.error(f"Failed to discover merchant at {agent_url}: {str(e)}")
            return None

    async def order_food(self, request: OrderRequest) -> CommerceResponse:
        """
        Place a food order with an ACP-compliant merchant.
        
        Args:
            request: Order request details
            
        Returns:
            CommerceResponse with order result
        """
        try:
            # Get merchant info
            merchant_info = await self._get_merchant_info(request.merchant_id)
            if not merchant_info:
                return CommerceResponse(
                    success=False,
                    error_message=f"Merchant {request.merchant_id} not found or not ACP-compliant",
                    request_id=request.request_id
                )
            
            # Initialize A2A client for this merchant
            await self._ensure_initialized(merchant_info.agent_url)
            
            # Create A2A task for order
            task_data = {
                "operation": "order_food",
                "merchant_id": request.merchant_id,
                "items": [item.dict() for item in request.items],
                "offer_id": request.offer_id,
                "pickup": request.pickup,
                "delivery_address": request.delivery_address,
                "special_instructions": request.special_instructions
            }
            
            # Execute through A2A
            result = await self._execute_a2a_task(task_data)
            
            # Convert result back to CommerceResponse
            return self._convert_from_a2a_result(result, request.request_id)
            
        except Exception as e:
            logger.error(f"Failed to place order: {str(e)}")
            return CommerceResponse(
                success=False,
                error_message=f"Order failed: {str(e)}",
                request_id=request.request_id
            )

    async def validate_offer(self, request: OfferValidationRequest) -> CommerceResponse:
        """
        Validate an offer with an ACP-compliant merchant.
        
        Args:
            request: Offer validation request
            
        Returns:
            CommerceResponse with validation result
        """
        try:
            # Get merchant info
            merchant_info = await self._get_merchant_info(request.merchant_id)
            if not merchant_info:
                return CommerceResponse(
                    success=False,
                    error_message=f"Merchant {request.merchant_id} not found or not ACP-compliant",
                    request_id=request.request_id
                )
            
            # Initialize A2A client for this merchant
            await self._ensure_initialized(merchant_info.agent_url)
            
            # Create A2A task for offer validation
            task_data = {
                "operation": "validate_offer",
                "merchant_id": request.merchant_id,
                "offer_id": request.offer_id,
                "items": [item.dict() for item in request.items]
            }
            
            # Execute through A2A
            result = await self._execute_a2a_task(task_data)
            
            # Convert result back to CommerceResponse
            return self._convert_from_a2a_result(result, request.request_id)
            
        except Exception as e:
            logger.error(f"Failed to validate offer: {str(e)}")
            return CommerceResponse(
                success=False,
                error_message=f"Offer validation failed: {str(e)}",
                request_id=request.request_id
            )

    async def process_payment(self, request: PaymentRequest) -> CommerceResponse:
        """
        Process payment with an ACP-compliant merchant.
        
        Args:
            request: Payment request
            
        Returns:
            CommerceResponse with payment result
        """
        try:
            # Get merchant info
            merchant_info = await self._get_merchant_info(request.merchant_id)
            if not merchant_info:
                return CommerceResponse(
                    success=False,
                    error_message=f"Merchant {request.merchant_id} not found or not ACP-compliant",
                    request_id=request.request_id
                )
            
            # Initialize A2A client for this merchant
            await self._ensure_initialized(merchant_info.agent_url)
            
            # Create A2A task for payment
            task_data = {
                "operation": "process_payment",
                "merchant_id": request.merchant_id,
                "order_id": request.order_id,
                "amount": float(request.amount),
                "payment_method": request.payment_method,
                "payment_details": request.payment_details
            }
            
            # Execute through A2A
            result = await self._execute_a2a_task(task_data)
            
            # Convert result back to CommerceResponse
            return self._convert_from_a2a_result(result, request.request_id)
            
        except Exception as e:
            logger.error(f"Failed to process payment: {str(e)}")
            return CommerceResponse(
                success=False,
                error_message=f"Payment processing failed: {str(e)}",
                request_id=request.request_id
            )

    async def get_menu(self, merchant_id: str, category: Optional[str] = None) -> CommerceResponse:
        """
        Get menu from an ACP-compliant merchant.
        
        Args:
            merchant_id: Merchant identifier
            category: Optional menu category filter
            
        Returns:
            CommerceResponse with menu information
        """
        try:
            # Get merchant info
            merchant_info = await self._get_merchant_info(merchant_id)
            if not merchant_info:
                return CommerceResponse(
                    success=False,
                    error_message=f"Merchant {merchant_id} not found or not ACP-compliant",
                    request_id=""
                )
            
            # Initialize A2A client for this merchant
            await self._ensure_initialized(merchant_info.agent_url)
            
            # Create A2A task for menu retrieval
            task_data = {
                "operation": "get_menu",
                "merchant_id": merchant_id,
                "category": category
            }
            
            # Execute through A2A
            result = await self._execute_a2a_task(task_data)
            
            # Convert result back to CommerceResponse
            return self._convert_from_a2a_result(result, "")
            
        except Exception as e:
            logger.error(f"Failed to get menu: {str(e)}")
            return CommerceResponse(
                success=False,
                error_message=f"Menu retrieval failed: {str(e)}",
                request_id=""
            )

    def _is_acp_compliant(self, agent_card: AgentCard) -> bool:
        """Check if an agent is ACP-compliant."""
        # Check for ACP skills in the agent card
        required_skills = ["acp_order_management", "acp_payment_processing", "acp_offer_management"]
        
        if not agent_card.skills:
            return False
        
        skill_ids = [skill.id for skill in agent_card.skills]
        return all(skill in skill_ids for skill in required_skills)

    def _extract_merchant_info(self, agent_card: AgentCard, agent_url: str) -> MerchantInfo:
        """Extract merchant information from agent card."""
        # This is a simplified implementation
        # In a real implementation, this would parse the agent card more thoroughly
        return MerchantInfo(
            merchant_id=f"merchant_{hash(agent_url) % 10000}",
            name=agent_card.name,
            description=agent_card.description,
            agent_url=agent_url,
            capabilities=["order_food", "validate_offer", "process_payment"],
            is_acp_compliant=True
        )

    async def _get_merchant_info(self, merchant_id: str) -> Optional[MerchantInfo]:
        """Get merchant info from cache or discover it."""
        if merchant_id in self._merchant_cache:
            return self._merchant_cache[merchant_id]
        
        # Hardcoded merchant mapping for demo
        merchant_urls = {
            "otto_portland": "http://localhost:4001",
            "street_exeter": "http://localhost:4002", 
            "newicks_lobster": "http://localhost:4003"
        }
        
        if merchant_id in merchant_urls:
            agent_url = merchant_urls[merchant_id]
            try:
                # Discover the merchant
                merchant_info = await self.discover_merchant(agent_url)
                if merchant_info:
                    return merchant_info
            except Exception as e:
                logger.error(f"Failed to discover merchant {merchant_id}: {e}")
        
        return None

    async def _execute_a2a_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute A2A task using send_message with proper message format."""
        try:
            # Create task input as JSON string
            task_input = json.dumps(task_data, default=str)  # Use default=str to handle Decimal types
            
            # Create proper A2A message format
            send_message_payload: dict[str, Any] = {
                'message': {
                    'role': 'user',
                    'parts': [
                        {'kind': 'text', 'text': task_input}
                    ],
                    'message_id': uuid4().hex,
                },
            }
            
            request = SendMessageRequest(
                id=str(uuid4()), 
                params=MessageSendParams(**send_message_payload)
            )
            
            # Send message to A2A agent
            logger.info(f"Sending task to A2A agent: {task_input}")
            response = await self.base_client.send_message(request)
            logger.info(f"Received response from A2A agent: {response}")
            logger.info(f"Response type: {type(response)}")
            logger.info(f"Response attributes: {dir(response)}")
            if hasattr(response, 'root'):
                logger.info(f"Response root: {response.root}")
                if hasattr(response.root, 'result'):
                    logger.info(f"Response result: {response.root.result}")
                    if hasattr(response.root.result, 'content'):
                        logger.info(f"Response content: {response.root.result.content}")
                        logger.info(f"Response content type: {type(response.root.result.content)}")
                        logger.info(f"Response content length: {len(str(response.root.result.content))}")
            else:
                logger.info("Response has no 'root' attribute")
                logger.info(f"Response dir: {dir(response)}")
                # Try to find content in other attributes
                for attr in dir(response):
                    if not attr.startswith('_'):
                        try:
                            value = getattr(response, attr)
                            logger.info(f"Response.{attr}: {value}")
                        except:
                            pass
            
            # Parse the response
            if hasattr(response, 'root') and hasattr(response.root, 'result'):
                # Extract content from the response
                result = response.root.result
                
                # Try to get content from artifacts first (this is where the restaurant agent puts the data)
                if hasattr(result, 'artifacts') and result.artifacts:
                    for artifact in result.artifacts:
                        if hasattr(artifact, 'parts') and artifact.parts:
                            for part in artifact.parts:
                                if hasattr(part, 'root') and hasattr(part.root, 'text'):
                                    content = part.root.text
                                    logger.info(f"Found content in artifact: {content[:200]}...")
                                    
                                    # Try to parse content as JSON first
                                    try:
                                        if isinstance(content, str):
                                            result_data = json.loads(content)
                                        else:
                                            result_data = content
                                        
                                        return {
                                            "success": True,
                                            "data": result_data,
                                            "error_message": None
                                        }
                                    except json.JSONDecodeError:
                                        # If not JSON, parse the text response to extract structured data
                                        return self._parse_text_response(content, task_data)
                
                # Fallback to old method
                if hasattr(result, 'content') and result.content:
                    # Try to parse content as JSON first
                    try:
                        if isinstance(result.content, str):
                            result_data = json.loads(result.content)
                        else:
                            result_data = result.content
                        
                        return {
                            "success": True,
                            "data": result_data,
                            "error_message": None
                        }
                    except json.JSONDecodeError:
                        # If not JSON, parse the text response to extract structured data
                        return self._parse_text_response(result.content, task_data)
                else:
                    return {
                        "success": True,
                        "data": {"message": "Task completed"},
                        "error_message": None
                    }
            else:
                return {
                    "success": True,
                    "data": {"message": "Task completed"},
                    "error_message": None
                }
            
        except Exception as e:
            logger.error(f"Error executing A2A task: {e}")
            return {
                "success": False,
                "data": None,
                "error_message": str(e)
            }



    def _parse_text_response(self, text_content: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse text response from restaurant agents to extract structured data."""
        operation = task_data.get("operation", "")
        
        if operation == "get_menu":
            return self._parse_menu_response(text_content)
        elif operation == "order_food":
            return self._parse_order_response(text_content)
        elif operation == "process_payment":
            return self._parse_payment_response(text_content)
        elif operation == "validate_offer":
            return self._parse_offer_response(text_content)
        else:
            return {"message": text_content}
    
    def _parse_menu_response(self, text_content: str) -> Dict[str, Any]:
        """Parse menu response text to extract menu items."""
        menu_items = []
        categories = []
        current_category = None
        
        lines = text_content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for category headers (all caps followed by colon)
            if line.isupper() and line.endswith(':'):
                current_category = line[:-1].title()  # Remove colon and title case
                categories.append(current_category)
            # Check for menu items (start with bullet point)
            elif line.startswith('•') and current_category:
                # Extract item name and price
                item_text = line[1:].strip()  # Remove bullet point
                if ' - $' in item_text:
                    name_part, price_part = item_text.split(' - $', 1)
                    name = name_part.strip()
                    try:
                        price = float(price_part.strip())
                        menu_items.append({
                            "name": name,
                            "price": price,
                            "category": current_category,
                            "available": True
                        })
                    except ValueError:
                        # If price parsing fails, just add the name
                        menu_items.append({
                            "name": name,
                            "price": 0.0,
                            "category": current_category,
                            "available": True
                        })
        
        return {
            "menu_items": menu_items,
            "categories": categories,
            "message": text_content
        }
    
    def _parse_order_response(self, text_content: str) -> Dict[str, Any]:
        """Parse order response text to extract order details."""
        import re
        
        # Extract order ID
        order_id_match = re.search(r'Order\s+(\w+)\s+created', text_content)
        order_id = order_id_match.group(1) if order_id_match else "N/A"
        
        # Extract total amount
        total_match = re.search(r'Total:\s+\$([\d.]+)', text_content)
        total = float(total_match.group(1)) if total_match else 0.0
        
        return {
            "order_id": order_id,
            "total": total,
            "status": "created",
            "message": text_content
        }
    
    def _parse_payment_response(self, text_content: str) -> Dict[str, Any]:
        """Parse payment response text to extract payment details."""
        import re
        
        # Extract payment amount
        amount_match = re.search(r'\$([\d.]+)', text_content)
        amount = float(amount_match.group(1)) if amount_match else 0.0
        
        # Extract order ID
        order_match = re.search(r'order\s+(\w+)', text_content)
        order_id = order_match.group(1) if order_match else "N/A"
        
        return {
            "payment_id": f"pay_{order_id}_{int(datetime.now().timestamp())}",
            "order_id": order_id,
            "amount": amount,
            "status": "completed",
            "message": text_content
        }
    
    def _parse_offer_response(self, text_content: str) -> Dict[str, Any]:
        """Parse offer validation response text."""
        is_valid = "valid" in text_content.lower() and "not valid" not in text_content.lower()
        
        return {
            "is_valid": is_valid,
            "message": text_content
        }

    def _convert_from_a2a_result(self, a2a_result: Dict[str, Any], request_id: str) -> CommerceResponse:
        """Convert A2A result to CommerceResponse."""
        return CommerceResponse(
            success=a2a_result.get("success", False),
            data=a2a_result.get("data"),
            error_message=a2a_result.get("error_message"),
            request_id=request_id
        )

    async def close(self):
        """Close the HTTP client."""
        await self.http_client.aclose()
