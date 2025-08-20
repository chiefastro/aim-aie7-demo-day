#!/usr/bin/env python3
"""Test script for the MCP Restaurant Client."""

import asyncio
import json
import logging
from mcp_restaurant_client.a2a_client import A2AClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_a2a_client():
    """Test the A2A client functionality."""
    
    # Test with OTTO Portland
    client = A2AClient("http://localhost:4001")
    
    try:
        # Test restaurant discovery
        logger.info("Testing restaurant discovery...")
        result = await client.discover_restaurant("otto_portland")
        print(f"Discovery result: {json.dumps(result, indent=2)}")
        
        # Test chat with restaurant
        logger.info("Testing chat with restaurant...")
        result = await client.chat_with_restaurant(
            "Hello! What offers do you have today?", 
            "otto_portland"
        )
        print(f"Chat result: {json.dumps(result, indent=2)}")
        
        # Test offer presentation
        logger.info("Testing offer presentation...")
        result = await client.present_offer("lunch_special", "otto_portland")
        print(f"Offer presentation result: {json.dumps(result, indent=2)}")
        
        # Test checkout initiation
        logger.info("Testing checkout initiation...")
        items = [
            {"name": "Margherita Pizza", "quantity": 1, "price": 18.00},
            {"name": "Caesar Salad", "quantity": 1, "price": 12.00}
        ]
        result = await client.initiate_checkout(
            "lunch_special", 
            items, 
            "otto_portland",
            pickup=True
        )
        print(f"Checkout result: {json.dumps(result, indent=2)}")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
    finally:
        await client.close()


async def test_mcp_server():
    """Test the MCP server functionality."""
    from mcp_restaurant_client.server import RestaurantMCPClient
    
    # This would test the MCP server directly
    # For now, just create an instance
    client = RestaurantMCPClient("http://localhost:4001")
    logger.info("MCP server created successfully")


if __name__ == "__main__":
    print("Testing A2A Client...")
    asyncio.run(test_a2a_client())
    
    print("\nTesting MCP Server...")
    asyncio.run(test_mcp_server())
    
    print("\nTests completed!")
