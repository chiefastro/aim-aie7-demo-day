#!/usr/bin/env python3
"""
Debug script to test ACP SDK imports
"""

try:
    print("Testing import of acp_sdk.txns.server...")
    from acp_sdk.txns.server import create_txn_simulator_app
    print("✅ Successfully imported create_txn_simulator_app")
    
    print("Testing import of acp_sdk...")
    from acp_sdk import create_txn_simulator_app, WalletManager
    print("✅ Successfully imported from acp_sdk")
    
    print("Testing function call...")
    app = create_txn_simulator_app()
    print("✅ Successfully created app")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
