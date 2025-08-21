"""
ACP MCP Server - Main entry point.
"""

import logging
import sys

from .server import main

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    try:
        logger.info("Starting ACP MCP Server...")
        main()
    except KeyboardInterrupt:
        logger.info("ACP MCP Server stopped by user")
    except Exception as e:
        logger.error(f"ACP MCP Server failed: {str(e)}")
        sys.exit(1)
