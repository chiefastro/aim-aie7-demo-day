"""MCP Restaurant Client Server - Wraps A2A client functionality."""

import logging
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP
from mcp.types import (
    TextContent,
)
from .a2a_client import A2AClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP(name="mcp-restaurant-client")

# A2A client will be initialized in main() function
a2a_client = None


@mcp.tool()
async def discover_restaurant(restaurant_id: str) -> str:
    """Discover restaurant information and available offers"""
    try:
        logger.info(f"Discover restaurant called with: restaurant_id={restaurant_id}")
        
        if a2a_client is None:
            return "❌ A2A client not initialized. Please check the server configuration."
        
        result = await a2a_client.discover_restaurant(restaurant_id)
        
        if result.get("status") == "error":
            return f"❌ Discovery failed: {result.get('error', 'Unknown error')}"
        
        # Format the response
        response_text = f"🏪 **Restaurant Discovery: {restaurant_id}**\n\n"
        
        agent_card = result.get("agent_card", {})
        if agent_card:
            response_text += f"**Agent Name**: {agent_card.get('name', 'Unknown')}\n"
            response_text += f"**Description**: {agent_card.get('description', 'No description available')}\n"
            
            if agent_card.get('capabilities'):
                response_text += f"**Capabilities**: {', '.join(agent_card['capabilities'])}\n"
            
            if agent_card.get('contact'):
                contact = agent_card['contact']
                response_text += f"**Contact**: {contact.get('name', 'Unknown')}\n"
                if contact.get('email'):
                    response_text += f"**Email**: {contact['email']}\n"
        
        response_text += f"\n**Status**: {result.get('status', 'Unknown')}"
        
        return response_text
        
    except Exception as e:
        logger.error(f"Unexpected error in discover restaurant: {e}")
        return f"❌ Discovery failed: {str(e)}"


@mcp.tool()
async def present_offer(offer_id: str, restaurant_id: str) -> str:
    """Present a specific offer from a restaurant"""
    try:
        logger.info(f"Present offer called with: offer_id={offer_id}, restaurant_id={restaurant_id}")
        
        if a2a_client is None:
            return "❌ A2A client not initialized. Please check the server configuration."
        
        result = await a2a_client.present_offer(offer_id, restaurant_id)
        
        # Simple response formatting
        if isinstance(result, dict):
            if result.get("status") == "error":
                return f"❌ Present offer failed: {result.get('error', 'Unknown error')}"
            else:
                return f"✅ Present offer success: {result.get('result', 'Offer presented successfully')}"
        else:
            return f"❌ Present offer failed: Unexpected result type {type(result)}: {result}"
        
    except Exception as e:
        logger.error(f"Unexpected error in present offer: {e}")
        return f"❌ Present offer failed: {str(e)}"


@mcp.tool()
async def initiate_checkout(
    offer_id: str,
    items: List[Dict[str, Any]],
    restaurant_id: str,
    pickup: bool = False
) -> str:
    """Initiate checkout process for an order"""
    try:
        logger.info(f"Initiate checkout called with: offer_id={offer_id}, restaurant_id={restaurant_id}, pickup={pickup}")
        
        if a2a_client is None:
            return "❌ A2A client not initialized. Please check the server configuration."
        
        result = await a2a_client.initiate_checkout(offer_id, items, restaurant_id, pickup)
        
        # Simple response formatting
        if isinstance(result, dict):
            if result.get("status") == "error":
                return f"❌ Checkout failed: {result.get('error', 'Unknown error')}"
            else:
                return f"✅ Checkout success: {result.get('result', 'Checkout initiated successfully')}"
        else:
            return f"❌ Checkout failed: Unexpected result type {type(result)}: {result}"
        
    except Exception as e:
        logger.error(f"Unexpected error in initiate checkout: {e}")
        return f"❌ Checkout failed: {str(e)}"


@mcp.tool()
async def confirm_order(order_id: str, restaurant_id: str) -> str:
    """Confirm an order"""
    try:
        logger.info(f"Confirm order called with: order_id={order_id}, restaurant_id={restaurant_id}")
        
        if a2a_client is None:
            return "❌ A2A client not initialized. Please check the server configuration."
        
        result = await a2a_client.confirm_order(order_id, restaurant_id)
        
        # Simple response formatting
        if isinstance(result, dict):
            if result.get("status") == "error":
                return f"❌ Order confirmation failed: {result.get('error', 'Unknown error')}"
            else:
                return f"✅ Order confirmation success: {result.get('result', 'Order confirmed successfully')}"
        else:
            return f"❌ Order confirmation failed: Unexpected result type {type(result)}: {result}"
        
    except Exception as e:
        logger.error(f"Unexpected error in confirm order: {e}")
        return f"❌ Order confirmation failed: {str(e)}"


@mcp.tool()
async def validate_offer(
    offer_id: str,
    items: List[Dict[str, Any]],
    restaurant_id: str
) -> str:
    """Validate if an offer can be applied to an order"""
    try:
        logger.info(f"Validate offer called with: offer_id={offer_id}, restaurant_id={restaurant_id}")
        
        if a2a_client is None:
            return "❌ A2A client not initialized. Please check the server configuration."
        
        result = await a2a_client.validate_offer(offer_id, items, restaurant_id)
        
        # Simple response formatting
        if isinstance(result, dict):
            if result.get("status") == "error":
                return f"❌ Offer validation failed: {result.get('error', 'Unknown error')}"
            else:
                return f"✅ Offer validation success: {result.get('result', 'Offer validation completed successfully')}"
        else:
            return f"❌ Offer validation failed: Unexpected result type {type(result)}: {result}"
        
    except Exception as e:
        logger.error(f"Unexpected error in validate offer: {e}")
        return f"❌ Offer validation failed: {str(e)}"


@mcp.tool()
async def chat_with_restaurant(message: str, restaurant_id: str) -> str:
    """Chat with a restaurant agent"""
    try:
        logger.info(f"Chat with restaurant called with: restaurant_id={restaurant_id}")
        
        if a2a_client is None:
            return "❌ A2A client not initialized. Please check the server configuration."
        
        result = await a2a_client.chat_with_restaurant(message, restaurant_id)
        
        # Simple response formatting
        if isinstance(result, dict):
            if result.get("status") == "error":
                return f"❌ Chat failed: {result.get('error', 'Unknown error')}"
            else:
                return f"✅ Chat success: {result.get('result', 'Chat completed successfully')}"
        else:
            return f"❌ Chat failed: Unexpected result type {type(result)}: {result}"
        
    except Exception as e:
        logger.error(f"Unexpected error in chat with restaurant: {e}")
        return f"❌ Chat failed: {str(e)}"


def main(a2a_server_url: str = "http://localhost:4001"):
    """Initialize A2A client and run MCP server."""
    global a2a_client
    
    try:
        a2a_client = A2AClient(a2a_server_url)
        logger.info(f"A2A client initialized successfully with URL: {a2a_server_url}")
    except Exception as e:
        logger.error(f"Failed to initialize A2A client with URL {a2a_server_url}: {e}")
        a2a_client = None
    
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
