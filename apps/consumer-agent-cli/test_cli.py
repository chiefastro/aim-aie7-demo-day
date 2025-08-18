#!/usr/bin/env python3
"""Simple test script for Consumer Agent CLI"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from consumer_agent.mcp_client import MCPClient
from consumer_agent.config import config


async def test_mcp_client():
    """Test MCP client functionality"""
    print("🧪 Testing MCP Client...")
    
    client = MCPClient()
    
    try:
        # Test connection
        connected = await client.connect()
        print(f"✅ Connection: {'PASS' if connected else 'FAIL'}")
        
        if connected:
            # Test search offers
            print("🔍 Testing search offers...")
            search_result = await client.search_offers(
                query="pizza",
                lat=42.3601,
                lng=-71.0589,
                radius_m=50000,
                limit=5
            )
            
            if search_result:
                print(f"✅ Search offers: PASS (found {search_result.get('total', 0)} offers)")
            else:
                print("❌ Search offers: FAIL")
            
            # Test get offer by ID
            print("📋 Testing get offer by ID...")
            offer = await client.get_offer_by_id("ofr_001")
            
            if offer:
                print(f"✅ Get offer by ID: PASS (offer: {offer.get('offer_id', 'N/A')})")
            else:
                print("❌ Get offer by ID: FAIL")
            
            # Test nearby offers
            print("📍 Testing nearby offers...")
            nearby_result = await client.get_nearby_offers(
                lat=42.3601,
                lng=-71.0589,
                radius_m=25000,
                limit=5
            )
            
            if nearby_result:
                print(f"✅ Nearby offers: PASS (found {nearby_result.get('total', 0)} offers)")
            else:
                print("❌ Nearby offers: FAIL")
        
        # Test disconnect
        await client.disconnect()
        print("✅ Disconnect: PASS")
        
    except Exception as e:
        print(f"❌ MCP client test failed: {e}")


async def test_config():
    """Test configuration management"""
    print("\n🧪 Testing Configuration...")
    
    try:
        # Test config validation
        valid = config.validate()
        print(f"✅ Config validation: {'PASS' if valid else 'FAIL'}")
        
        # Test config values
        print(f"   MCP Host: {config.MCP_HOST}")
        print(f"   MCP Port: {config.MCP_PORT}")
        print(f"   GOR URL: {config.GOR_BASE_URL}")
        print(f"   Default Radius: {config.DEFAULT_SEARCH_RADIUS_M}m")
        print(f"   Default Limit: {config.DEFAULT_SEARCH_LIMIT}")
        print(f"   Demo Lat: {config.DEMO_LAT}")
        print(f"   Demo Lng: {config.DEMO_LNG}")
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")


async def test_mock_data():
    """Test mock data generation"""
    print("\n🧪 Testing Mock Data...")
    
    client = MCPClient()
    
    try:
        # Test pizza search
        print("🍕 Testing pizza search...")
        pizza_result = await client._mock_search_offers({
            "query": "pizza",
            "limit": 3
        })
        
        if pizza_result and pizza_result.get("offers"):
            offers = pizza_result["offers"]
            print(f"✅ Pizza search: PASS (found {len(offers)} offers)")
            for offer in offers:
                print(f"   - {offer.get('title', 'N/A')} (${offer.get('bounty', {}).get('amount', 0)})")
        else:
            print("❌ Pizza search: FAIL")
        
        # Test seafood search
        print("🦞 Testing seafood search...")
        seafood_result = await client._mock_search_offers({
            "query": "seafood",
            "limit": 3
        })
        
        if seafood_result and seafood_result.get("offers"):
            offers = seafood_result["offers"]
            print(f"✅ Seafood search: PASS (found {len(offers)} offers)")
            for offer in offers:
                print(f"   - {offer.get('title', 'N/A')} (${offer.get('bounty', {}).get('amount', 0)})")
        else:
            print("❌ Seafood search: FAIL")
        
        # Test generic search
        print("🍽️  Testing generic search...")
        generic_result = await client._mock_search_offers({
            "query": "restaurant",
            "limit": 3
        })
        
        if generic_result and generic_result.get("offers"):
            offers = generic_result["offers"]
            print(f"✅ Generic search: PASS (found {len(offers)} offers)")
            for offer in offers:
                print(f"   - {offer.get('title', 'N/A')} (${offer.get('bounty', {}).get('amount', 0)})")
        else:
            print("❌ Generic search: FAIL")
        
    except Exception as e:
        print(f"❌ Mock data test failed: {e}")


async def main():
    """Run all tests"""
    print("🚀 Starting Consumer Agent CLI Tests...\n")
    
    # Test configuration
    await test_config()
    
    # Test MCP client
    await test_mcp_client()
    
    # Test mock data
    await test_mock_data()
    
    print("\n✨ All tests completed!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Tests interrupted by user")
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        sys.exit(1)
