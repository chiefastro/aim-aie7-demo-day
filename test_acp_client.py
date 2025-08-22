#!/usr/bin/env python3
"""
Test script to debug ACP client connection issues.
"""

import asyncio
import sys
import os

# Add the acp-sdk src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'apps', 'acp-sdk', 'src'))

from acp_sdk.mcp.a2a_client import ACPClient
from acp_sdk.mcp.models import OrderRequest, OrderItem

async def test_acp_client():
    """Test ACP client connection to real A2A servers."""
    
    print("🧪 Testing ACP Client Connection...")
    
    # Test 1: Initialize client with a specific server URL
    print("\n1. Testing client initialization with OTTO Portland URL...")
    try:
        client = ACPClient("http://localhost:4001")
        print("✅ Client initialized successfully")
    except Exception as e:
        print(f"❌ Client initialization failed: {e}")
        return
    
    # Test 2: Discover merchant
    print("\n2. Testing merchant discovery...")
    try:
        merchant_info = await client.discover_merchant("http://localhost:4001")
        if merchant_info:
            print(f"✅ Merchant discovered: {merchant_info.name}")
            print(f"   ID: {merchant_info.merchant_id}")
            print(f"   URL: {merchant_info.agent_url}")
            print(f"   ACP Compliant: {merchant_info.is_acp_compliant}")
        else:
            print("❌ Merchant discovery failed")
            return
    except Exception as e:
        print(f"❌ Merchant discovery failed: {e}")
        return
    
    # Test 3: Get menu
    print("\n3. Testing menu retrieval...")
    try:
        response = await client.get_menu("otto_portland")
        if response.success:
            print("✅ Menu retrieval successful")
            print(f"   Data: {response.data}")
            if response.data and 'menu_items' in response.data:
                print(f"   Menu items found: {len(response.data['menu_items'])}")
                for item in response.data['menu_items'][:3]:  # Show first 3 items
                    print(f"     - {item.get('name', 'N/A')}: ${item.get('price', 'N/A')}")
        else:
            print(f"❌ Menu retrieval failed: {response.error_message}")
    except Exception as e:
        print(f"❌ Menu retrieval failed: {e}")
    
    # Test 4: Place order
    print("\n4. Testing order placement...")
    try:
        items = [OrderItem(name="Margherita Pizza", quantity=1, price=18.99)]
        request = OrderRequest(
            merchant_id="otto_portland",
            items=items,
            pickup=True
        )
        response = await client.order_food(request)
        if response.success:
            print("✅ Order placement successful")
            print(f"   Data: {response.data}")
        else:
            print(f"❌ Order placement failed: {response.error_message}")
    except Exception as e:
        print(f"❌ Order placement failed: {e}")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(test_acp_client())
