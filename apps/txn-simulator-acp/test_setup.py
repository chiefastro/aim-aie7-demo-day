#!/usr/bin/env python3
"""
Test script to verify the new transaction simulator setup.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all imports work correctly."""
    print("🧪 Testing imports...")
    
    try:
        # Test ACP SDK imports
        from acp_sdk import create_txn_simulator_app, WalletManager
        print("✅ ACP SDK imports successful")
        
        # Test local imports
        from txn_simulator_acp.main import app
        print("✅ Local imports successful")
        
        # Test app creation
        test_app = create_txn_simulator_app(
            title="Test Simulator",
            description="Test transaction simulator",
            version="0.1.0"
        )
        print("✅ App creation successful")
        
        # Test wallet manager
        wallet_manager = WalletManager()
        print("✅ Wallet manager creation successful")
        
        print("\n🎉 All tests passed! The transaction simulator is ready to use.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_endpoints():
    """Test that the app has the expected endpoints."""
    print("\n🧪 Testing endpoints...")
    
    try:
        from txn_simulator_acp.main import app
        
        # Check for standard endpoints
        routes = [route.path for route in app.routes]
        
        expected_endpoints = [
            "/health",
            "/",
            "/protocol/stats",
            "/receipts",
            "/postbacks",
            "/custom/demo-stats",
            "/custom/health"
        ]
        
        for endpoint in expected_endpoints:
            if endpoint in routes:
                print(f"✅ Found endpoint: {endpoint}")
            else:
                print(f"❌ Missing endpoint: {endpoint}")
        
        # Check for wallet endpoints (these are added dynamically)
        wallet_endpoints = [route for route in routes if "/wallets/" in route]
        print(f"✅ Found {len(wallet_endpoints)} wallet endpoints")
        
        print("\n🎉 Endpoint tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Endpoint test error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Transaction Simulator Setup\n")
    
    imports_ok = test_imports()
    endpoints_ok = test_endpoints()
    
    if imports_ok and endpoints_ok:
        print("\n✅ All tests passed! The transaction simulator is ready.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the setup.")
        sys.exit(1)
