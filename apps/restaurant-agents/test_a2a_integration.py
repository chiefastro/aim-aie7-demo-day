#!/usr/bin/env python3
"""Test script for A2A integration with mock restaurant servers."""

import asyncio
import json
import logging
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

from restaurant_agents.a2a_executor import RestaurantAgentExecutor
from restaurant_agents.config import get_restaurant_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_a2a_integration():
    """Test the A2A executor integration with mock servers."""
    
    # Test with OTTO Portland
    config = get_restaurant_config("otto_portland")
    executor = RestaurantAgentExecutor(config)
    
    try:
        print("Testing A2A Integration with Mock Restaurant Server")
        print("=" * 60)
        
        test_results = []
        
        # Test 1: Get menu
        print("\n1. Testing menu retrieval...")
        menu_response = await executor._get_menu()
        print(f"Menu Response: {menu_response[:200]}...")
        menu_success = "Sorry, I couldn't retrieve the menu" not in menu_response
        test_results.append(("Menu retrieval", menu_success))
        
        # Test 2: Present offer
        print("\n2. Testing offer presentation...")
        offer_response = await executor._present_offer("ofr_001")
        print(f"Offer Response: {offer_response}")
        offer_success = "Sorry, I couldn't retrieve offer" not in offer_response
        test_results.append(("Offer presentation", offer_success))
        
        # Test 3: Validate offer
        print("\n3. Testing offer validation...")
        items = [
            {"menu_item_id": "pizza_001", "quantity": 1, "price": 18.00},
            {"menu_item_id": "salad_001", "quantity": 1, "price": 12.00}
        ]
        validation_response = await executor._validate_offer("ofr_001", items)
        print(f"Validation Response: {validation_response}")
        validation_success = "Sorry, I couldn't validate offer" not in validation_response
        test_results.append(("Offer validation", validation_success))
        
        # Test 4: Initiate checkout
        print("\n4. Testing checkout initiation...")
        checkout_response = await executor._initiate_checkout("ofr_001", items)
        print(f"Checkout Response: {checkout_response}")
        checkout_success = "Sorry, I couldn't initiate checkout" not in checkout_response
        test_results.append(("Checkout initiation", checkout_success))
        
        # Test 5: Extract information from queries
        print("\n5. Testing query parsing...")
        test_queries = [
            "Show me the lunch_special offer",
            "I want to order a pizza and salad",
            "What's on the menu?",
            "Can you confirm my order order_123?"
        ]
        
        query_parsing_success = True
        for query in test_queries:
            offer_id = executor._extract_offer_id(query)
            order_info = executor._extract_order_info(query)
            print(f"Query: '{query}'")
            print(f"  Extracted offer_id: {offer_id}")
            print(f"  Extracted order_info: {order_info}")
            if not offer_id or not order_info:
                query_parsing_success = False
        
        test_results.append(("Query parsing", query_parsing_success))
        
        # Report results
        print("\n" + "="*60)
        print("TEST RESULTS:")
        print("="*60)
        
        passed = 0
        total = len(test_results)
        
        for test_name, success in test_results:
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{test_name}: {status}")
            if success:
                passed += 1
        
        print(f"\nSummary: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 All tests passed successfully!")
        else:
            print(f"\n⚠️  {total - passed} tests failed. Check the output above for details.")
            return False
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await executor.cleanup()


if __name__ == "__main__":
    print("Starting A2A Integration Tests...")
    print("Make sure mock restaurant servers are running on ports 8001-8003")
    print()
    
    asyncio.run(test_a2a_integration())
