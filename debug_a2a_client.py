#!/usr/bin/env python3
"""
Direct A2A client debug script to test communication with restaurant agents.
"""

import asyncio
import json
import sys
import os
import logging

# Configure logging to see debug output
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

# Add the acp-mcp src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'apps', 'acp-mcp', 'src'))

from acp_mcp.client import ACPClient

async def debug_a2a_client():
    """Debug A2A client communication with restaurant agents."""
    
    print("🔍 Debugging A2A Client Communication")
    print("=" * 50)
    
    # Test with OTTO Portland
    merchant_id = "otto_portland"
    agent_url = "http://localhost:4001"
    
    print(f"\n1. Testing merchant discovery for {merchant_id} at {agent_url}")
    print("-" * 50)
    
    try:
        client = ACPClient()
        
        # Test merchant discovery
        print("Discovering merchant...")
        merchant_info = await client.discover_merchant(agent_url)
        
        if merchant_info:
            print(f"✅ Merchant discovered successfully!")
            print(f"   Name: {merchant_info.name}")
            print(f"   Description: {merchant_info.description}")
            print(f"   Agent URL: {merchant_info.agent_url}")
            print(f"   Is ACP Compliant: {merchant_info.is_acp_compliant}")
            print(f"   Capabilities: {merchant_info.capabilities}")
        else:
            print("❌ Merchant discovery failed")
            return
        
        print(f"\n2. Testing menu retrieval for {merchant_id}")
        print("-" * 50)
        
        # Test menu retrieval
        print("Getting menu...")
        response = await client.get_menu(merchant_id)
        
        print(f"Response success: {response.success}")
        print(f"Response data type: {type(response.data)}")
        print(f"Response data: {json.dumps(response.data, indent=2) if response.data else 'None'}")
        print(f"Error message: {response.error_message}")
        
        if response.data and 'menu_items' in response.data:
            print(f"\n✅ Menu items found: {len(response.data['menu_items'])}")
            for i, item in enumerate(response.data['menu_items'][:3]):  # Show first 3 items
                print(f"   {i+1}. {item.get('name', 'Unknown')} - ${item.get('price', 0)}")
        else:
            print("\n❌ No menu items found in response")
        
        print(f"\n3. Testing order placement for {merchant_id}")
        print("-" * 50)
        
        # Test order placement
        from acp_mcp.models import OrderRequest, OrderItem
        
        order_items = [
            OrderItem(name="Margherita Pizza", quantity=1, price=16.5)
        ]
        
        order_request = OrderRequest(
            merchant_id=merchant_id,
            items=order_items,
            pickup=True,
            request_id="test_order_123"
        )
        
        print("Placing order...")
        order_response = await client.order_food(order_request)
        
        print(f"Order response success: {order_response.success}")
        print(f"Order response data: {json.dumps(order_response.data, indent=2) if order_response.data else 'None'}")
        print(f"Order error message: {order_response.error_message}")
        
        await client.close()
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_a2a_client())
