"""CLI entry point for Consumer Agent CLI"""

import asyncio
import sys
from .cli import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Consumer Agent CLI stopped")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
