#!/usr/bin/env python3
"""
Test script for ACP-compliant restaurant agents.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared'))

# Add ACP SDK to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'acp-sdk', 'src'))

from restaurant_agents.acp_restaurant_agent import create_acp_restaurant_agent
from restaurant_agents.config import get_restaurant_config


async def test_acp_agent(restaurant_id: str):
    """Test an ACP-compliant restaurant agent."""
    print(f"\n{'='*50}")
    print(f"Testing ACP Agent: {restaurant_id}")
    print(f"{'='*50}")
    
    try:
        # Create agent
        agent = create_acp_restaurant_agent(restaurant_id)
        
        # Test agent card
        card = agent.get_agent_card()
        print(f"✅ Agent Card: {card.name}")
        print(f"✅ ACP Compliant: {agent.acp_agent.is_acp_compliant()}")
        print(f"✅ Skills: {len(agent.acp_agent.commerce_skills.skills)}")
        
        # Test health check
        health = await agent.health_check()
        print(f"✅ Health Status: {health['status']}")
        print(f"✅ Skills Health: {len(health['skills'])} skills")
        
        # Test commerce task
        task_data = {
            "operation": "order_food",
            "merchant_id": restaurant_id,
            "items": [
                {
                    "name": "Margherita Pizza",
                    "quantity": 1,
                    "price": 18.99
                }
            ],
            "pickup": True
        }
        
        result = await agent.process_commerce_task(task_data)
        print(f"✅ Commerce Task Result: {result['success']}")
        
        if result['success'] and result['data']:
            if isinstance(result['data'], dict):
                print(f"✅ Order Created: {result['data'].get('order_id', 'N/A')}")
            else:
                print(f"✅ Order Created: {result['data']}")
        elif result['success']:
            print(f"✅ Task completed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed for {restaurant_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run tests for all ACP-compliant restaurant agents."""
    print("Testing ACP-Compliant Restaurant Agents")
    print("=" * 50)
    
    # Test all restaurants
    restaurants = ["otto_portland", "street_exeter", "newicks_lobster"]
    
    results = []
    for restaurant_id in restaurants:
        success = await test_acp_agent(restaurant_id)
        results.append((restaurant_id, success))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print(f"{'='*50}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for restaurant_id, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {restaurant_id}")
    
    print(f"\nOverall: {passed}/{total} agents passed")
    
    if passed == total:
        print("🎉 All ACP-compliant agents are working correctly!")
    else:
        print("⚠️  Some agents need attention.")


if __name__ == "__main__":
    asyncio.run(main())
