"""A2A Client for communicating with restaurant A2A servers."""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

import httpx
from a2a.client import A2AClient as BaseA2AClient, A2ACardResolver
from a2a.types import AgentCard, Task

logger = logging.getLogger(__name__)


class A2AClient:
    """A2A client for restaurant interactions."""

    def __init__(self, a2a_server_url: str):
        self.a2a_server_url = a2a_server_url.rstrip('/')
        self.http_client = httpx.AsyncClient(timeout=httpx.Timeout(60.0))
        self.base_client = None
        self.agent_card = None

    async def _ensure_initialized(self):
        """Ensure the A2A client is initialized with agent card."""
        if self.base_client is None:
            try:
                # Try to get agent card from the default path first
                resolver = A2ACardResolver(
                    httpx_client=self.http_client,
                    base_url=self.a2a_server_url
                )
                
                # Fetch public agent card from default path
                logger.info(f"Fetching agent card from: {self.a2a_server_url}/.well-known/agent-card.json")
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
                        base_url=self.a2a_server_url,
                        agent_card_path="/.well-known/agent.json"
                    )
                    
                    logger.info(f"Trying fallback path: {self.a2a_server_url}/.well-known/agent.json")
                    self.agent_card = await resolver.get_agent_card()
                    
                    self.base_client = BaseA2AClient(
                        httpx_client=self.http_client,
                        agent_card=self.agent_card
                    )
                    logger.info("A2A client initialized successfully with fallback path")
                    
                except Exception as fallback_error:
                    logger.error(f"Failed to initialize A2A client with fallback path: {fallback_error}")
                    raise

    async def discover_restaurant(self, restaurant_id: str) -> Dict[str, Any]:
        """Discover restaurant information and available offers."""
        try:
            await self._ensure_initialized()
            
            # Return the agent card information
            return {
                "restaurant_id": restaurant_id,
                "agent_card": self.agent_card.dict() if hasattr(self.agent_card, 'dict') else self.agent_card,
                "status": "discovered"
            }
                
        except Exception as e:
            logger.error(f"Error discovering restaurant {restaurant_id}: {e}")
            return {
                "restaurant_id": restaurant_id,
                "error": str(e),
                "status": "error"
            }

    async def present_offer(self, offer_id: str, restaurant_id: str) -> Dict[str, Any]:
        """Present a specific offer from a restaurant."""
        try:
            # Skip initialization for now to debug the issue
            # await self._ensure_initialized()
            
            # For now, return a simple response since the A2A SDK task execution is complex
            # In a real implementation, this would use the A2A SDK's task execution flow
            logger.info(f"Presenting offer {offer_id} for restaurant {restaurant_id}")
            return {
                "offer_id": offer_id,
                "restaurant_id": restaurant_id,
                "result": f"Offer {offer_id} is available at {restaurant_id}. This is a demo response.",
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Error presenting offer {offer_id}: {e}")
            return {
                "offer_id": offer_id,
                "restaurant_id": restaurant_id,
                "error": str(e),
                "status": "error"
            }

    async def initiate_checkout(
        self, 
        offer_id: str, 
        items: List[Dict[str, Any]], 
        restaurant_id: str,
        pickup: bool = False
    ) -> Dict[str, Any]:
        """Initiate checkout process for an order."""
        try:
            # Skip initialization for now to debug the issue
            # await self._ensure_initialized()
            
            # For now, return a simple response since the A2A SDK task execution is complex
            order_type = "pickup" if pickup else "delivery"
            return {
                "offer_id": offer_id,
                "restaurant_id": restaurant_id,
                "items": items,
                "pickup": pickup,
                "result": f"Checkout initiated for {order_type} order with {len(items)} items at {restaurant_id}. This is a demo response.",
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Error initiating checkout for offer {offer_id}: {e}")
            return {
                "offer_id": offer_id,
                "restaurant_id": restaurant_id,
                "error": str(e),
                "status": "error"
            }

    async def confirm_order(self, order_id: str, restaurant_id: str) -> Dict[str, Any]:
        """Confirm an order."""
        try:
            # Skip initialization for now to debug the issue
            # await self._ensure_initialized()
            
            # For now, return a simple response since the A2A SDK task execution is complex
            return {
                "order_id": order_id,
                "restaurant_id": restaurant_id,
                "result": f"Order {order_id} has been confirmed at {restaurant_id}. This is a demo response.",
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Error confirming order {order_id}: {e}")
            return {
                "order_id": order_id,
                "restaurant_id": restaurant_id,
                "error": str(e),
                "status": "error"
            }

    async def validate_offer(
        self, 
        offer_id: str, 
        items: List[Dict[str, Any]], 
        restaurant_id: str
    ) -> Dict[str, Any]:
        """Validate if an offer can be applied to an order."""
        try:
            await self._ensure_initialized()
            
            # For now, return a simple response since the A2A SDK task execution is complex
            return {
                "offer_id": offer_id,
                "restaurant_id": restaurant_id,
                "items": items,
                "result": f"Offer {offer_id} is valid for the selected items at {restaurant_id}. This is a demo response.",
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Error validating offer {offer_id}: {e}")
            return {
                "offer_id": offer_id,
                "restaurant_id": restaurant_id,
                "error": str(e),
                "status": "error"
            }

    async def chat_with_restaurant(self, message: str, restaurant_id: str) -> Dict[str, Any]:
        """Chat with a restaurant agent."""
        try:
            # Skip initialization for now to debug the issue
            # await self._ensure_initialized()
            
            # For now, return a simple response since the A2A SDK task execution is complex
            return {
                "message": message,
                "restaurant_id": restaurant_id,
                "result": f"Restaurant {restaurant_id} says: 'Thank you for your message: {message}. This is a demo response.'",
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Error chatting with restaurant {restaurant_id}: {e}")
            return {
                "message": message,
                "restaurant_id": restaurant_id,
                "error": str(e),
                "status": "error"
            }

    async def _wait_for_task_completion(self, task_id: str, timeout: int = 30) -> Dict[str, Any]:
        """Wait for a task to complete and return the result."""
        start_time = datetime.now()
        
        while True:
            try:
                # Check if we've exceeded timeout
                if (datetime.now() - start_time).seconds > timeout:
                    raise TimeoutError(f"Task {task_id} timed out after {timeout} seconds")
                
                # Get task status
                task = await self.base_client.get_task(task_id)
                
                if task.state == "completed":
                    # Get task artifacts
                    artifacts = await self.base_client.get_task_artifacts(task_id)
                    return {
                        "task_state": task.state,
                        "artifacts": [artifact.dict() if hasattr(artifact, 'dict') else artifact for artifact in artifacts]
                    }
                elif task.state == "failed":
                    return {
                        "task_state": task.state,
                        "error": "Task failed"
                    }
                elif task.state == "input_required":
                    return {
                        "task_state": task.state,
                        "message": "Task requires additional input"
                    }
                
                # Wait a bit before checking again
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error waiting for task completion: {e}")
                raise

    async def close(self):
        """Close the HTTP client."""
        await self.http_client.aclose()
