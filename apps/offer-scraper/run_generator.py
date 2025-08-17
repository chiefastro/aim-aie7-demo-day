#!/usr/bin/env python3
"""
Simple script to run the ACP offer generator
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import and run the generator
from generate_offers import main
import asyncio

if __name__ == "__main__":
    print("Starting ACP Offer Generator...")
    print(f"MAPBOX_TOKEN: {'Set' if os.getenv('MAPBOX_TOKEN') else 'Not set'}")
    
    try:
        asyncio.run(main())
        print("Offer generation completed successfully!")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
