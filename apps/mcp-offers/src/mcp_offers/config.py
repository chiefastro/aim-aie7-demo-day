"""Configuration management for MCP Offers Server"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration for MCP Offers Server"""
    
    # GOR API configuration
    GOR_BASE_URL: str = os.getenv("GOR_BASE_URL", "http://localhost:3001")
    
    # MCP Server configuration
    MCP_HOST: str = os.getenv("MCP_HOST", "localhost")
    MCP_PORT: int = int(os.getenv("MCP_PORT", "3002"))
    
    # Logging configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Search defaults
    DEFAULT_SEARCH_RADIUS_M: int = int(os.getenv("DEFAULT_SEARCH_RADIUS_M", "50000"))
    DEFAULT_SEARCH_LIMIT: int = int(os.getenv("DEFAULT_SEARCH_LIMIT", "20"))
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        try:
            # Validate GOR URL
            if not cls.GOR_BASE_URL.startswith(("http://", "https://")):
                raise ValueError("GOR_BASE_URL must be a valid HTTP URL")
            
            # Validate port
            if not (1 <= cls.MCP_PORT <= 65535):
                raise ValueError("MCP_PORT must be between 1 and 65535")
            
            # Validate radius
            if cls.DEFAULT_SEARCH_RADIUS_M <= 0:
                raise ValueError("DEFAULT_SEARCH_RADIUS_M must be positive")
            
            # Validate limit
            if cls.DEFAULT_SEARCH_LIMIT <= 0:
                raise ValueError("DEFAULT_SEARCH_LIMIT must be positive")
            
            return True
            
        except Exception as e:
            print(f"❌ Configuration validation failed: {e}")
            return False


# Global config instance
config = Config()
