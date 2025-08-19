#!/usr/bin/env python3
"""
Test script for mock restaurant servers
"""

import requests
import json
import time
from typing import Dict, List

RESTAURANTS = {
    "OTTO Portland": "http://localhost:8001",
    "Street Exeter": "http://localhost:8002", 
    "Newick's Lobster House": "http://localhost:8003"
}

def test_health_endpoints():
    """Test health endpoints for all restaurants"""
    print("🏥 Testing health endpoints...")
    
    for name, url in RESTAURANTS.items():
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ {name}: {data.get('status', 'unknown')}")
            else:
                print(f"  ❌ {name}: HTTP {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"  ❌ {name}: {e}")

def test_osf_endpoints():
    """Test OSF endpoints for all restaurants"""
    print("\n📄 Testing OSF endpoints...")
    
    for name, url in RESTAURANTS.items():
        try:
            response = requests.get(f"{url}/.well-known/osf.json", timeout=5)
            if response.status_code == 200:
                data = response.json()
                merchant_name = data.get("publisher", {}).get("name", "Unknown")
                offers_count = len(data.get("offers", []))
                print(f"  ✅ {name}: {merchant_name} ({offers_count} offers)")
            else:
                print(f"  ❌ {name}: HTTP {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"  ❌ {name}: {e}")

def test_menu_endpoints():
    """Test menu endpoints for all restaurants"""
    print("\n🍽️ Testing menu endpoints...")
    
    for name, url in RESTAURANTS.items():
        try:
            response = requests.get(f"{url}/a2a/menu", timeout=5)
            if response.status_code == 200:
                data = response.json()
                categories = data.get("categories", {})
                total_items = sum(len(items) for items in categories.values())
                print(f"  ✅ {name}: {len(categories)} categories, {total_items} items")
            else:
                print(f"  ❌ {name}: HTTP {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"  ❌ {name}: {e}")

def test_order_creation():
    """Test order creation for all restaurants"""
    print("\n🛒 Testing order creation...")
    
    for name, url in RESTAURANTS.items():
        try:
            # Get menu first to get valid item IDs
            menu_response = requests.get(f"{url}/a2a/menu", timeout=5)
            if menu_response.status_code != 200:
                print(f"  ❌ {name}: Could not get menu")
                continue
                
            menu_data = menu_response.json()
            categories = menu_data.get("categories", {})
            
            # Find first available item
            first_item = None
            for category_items in categories.values():
                if category_items:
                    first_item = category_items[0]
                    break
            
            if not first_item:
                print(f"  ❌ {name}: No menu items found")
                continue
            
            # Create order
            order_data = {
                "items": [
                    {
                        "menu_item_id": first_item["id"],
                        "quantity": 1,
                        "price": first_item["price"]
                    }
                ],
                "customer_name": "Test Customer",
                "order_type": "dine-in"
            }
            
            response = requests.post(
                f"{url}/a2a/order/create",
                json=order_data,
                timeout=5
            )
            
            if response.status_code == 200:
                order = response.json()
                order_id = order.get("order_id", "unknown")
                total = order.get("total", 0)
                print(f"  ✅ {name}: Order {order_id} created (${total:.2f})")
            else:
                print(f"  ❌ {name}: HTTP {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"  ❌ {name}: {e}")

def main():
    """Run all tests"""
    print("🧪 Testing Mock Restaurant Servers")
    print("=" * 40)
    
    # Wait a moment for servers to be ready
    time.sleep(1)
    
    test_health_endpoints()
    test_osf_endpoints()
    test_menu_endpoints()
    test_order_creation()
    
    print("\n" + "=" * 40)
    print("✅ Testing complete!")

if __name__ == "__main__":
    main()
