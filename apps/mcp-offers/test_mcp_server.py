#!/usr/bin/env python3
"""Simple test script for MCP Offers Server"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from mcp_offers.server import main
from mcp_offers.gor_client import GORClient


async def test_gor_client():
    """Test GOR client functionality"""
    print("🧪 Testing GOR Client...")
    
    client = GORClient()
    
    try:
        # Test health check
        healthy = await client.health_check()
        print(f"✅ Health check: {'PASS' if healthy else 'FAIL'}")
        
        # Test search offers
        print("🔍 Testing search offers...")
        search_result = await client.search_offers({
            "query": "pizza",
            "lat": 42.3601,
            "lng": -71.0589,
            "radius_m": 50000,
            "limit": 5
        })
        
        if search_result:
            print(f"✅ Search offers: PASS (found {search_result.results.total} offers)")
        else:
            print("❌ Search offers: FAIL")
        
        # Test get offer by ID
        print("📋 Testing get offer by ID...")
        offer = await client.get_offer_by_id("ofr_001")
        
        if offer:
            print(f"✅ Get offer by ID: PASS (offer: {offer.offer_id})")
        else:
            print("❌ Get offer by ID: FAIL")
        
        # Test nearby offers
        print("📍 Testing nearby offers...")
        nearby_result = await client.get_nearby_offers({
            "lat": 42.3601,
            "lng": -71.0589,
            "radius_m": 25000,
            "limit": 5
        })
        
        if nearby_result:
            print(f"✅ Nearby offers: PASS (found {nearby_result.results.total} offers)")
        else:
            print("❌ Nearby offers: FAIL")
        
    except Exception as e:
        print(f"❌ GOR client test failed: {e}")
    
    finally:
        await client.client.aclose()


async def test_mcp_server():
    """Test MCP server functionality"""
    print("\n🧪 Testing MCP Server...")
    
    try:
        # Import and test server components
        from mcp_offers.server import server, handle_list_tools
        
        # Test tool listing
        tools = await handle_list_tools()
        print(f"✅ Tool listing: PASS (found {len(tools)} tools)")
        
        for tool in tools:
            print(f"   - {tool.name}: {tool.description}")
        
        # Test tool handling
        from mcp_offers.server import handle_search_offers, handle_get_offer_by_id, handle_nearby_offers
        
        # Test search offers handler
        search_args = {
            "query": "pizza",
            "lat": 42.3601,
            "lng": -71.0589,
            "radius_m": 50000,
            "limit": 5
        }
        
        search_response = await handle_search_offers(search_args)
        if search_response:
            print("✅ Search offers handler: PASS")
        else:
            print("❌ Search offers handler: FAIL")
        
        # Test get offer handler
        offer_args = {"offer_id": "ofr_001"}
        offer_response = await handle_get_offer_by_id(offer_args)
        if offer_response:
            print("✅ Get offer handler: PASS")
        else:
            print("❌ Get offer handler: FAIL")
        
        # Test nearby offers handler
        nearby_args = {
            "lat": 42.3601,
            "lng": -71.0589,
            "radius_m": 25000,
            "limit": 5
        }
        nearby_response = await handle_nearby_offers(nearby_args)
        if nearby_response:
            print("✅ Nearby offers handler: PASS")
        else:
            print("❌ Nearby offers handler: FAIL")
        
    except Exception as e:
        print(f"❌ MCP server test failed: {e}")


async def main():
    """Run all tests"""
    print("🚀 Starting MCP Offers Server Tests...\n")
    
    # Test GOR client
    await test_gor_client()
    
    # Test MCP server
    await test_mcp_server()
    
    print("\n✨ All tests completed!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Tests interrupted by user")
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        sys.exit(1)
