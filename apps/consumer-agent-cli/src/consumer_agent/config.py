"""Configuration management for Consumer Agent CLI"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration for Consumer Agent CLI"""
    
    # MCP Server configuration
    MCP_HOST: str = os.getenv("MCP_HOST", "localhost")
    MCP_PORT: int = int(os.getenv("MCP_PORT", "3002"))
    
    # GOR API configuration (for direct access if needed)
    GOR_BASE_URL: str = os.getenv("GOR_BASE_URL", "http://localhost:3001")
    
    # CLI configuration
    DEFAULT_SEARCH_RADIUS_M: int = int(os.getenv("DEFAULT_SEARCH_RADIUS_M", "50000"))
    DEFAULT_SEARCH_LIMIT: int = int(os.getenv("DEFAULT_SEARCH_LIMIT", "10"))
    
    # Demo defaults
    DEMO_LAT: float = float(os.getenv("DEMO_LAT", "42.3601"))
    DEMO_LNG: float = float(os.getenv("DEMO_LNG", "-71.0589"))
    DEMO_RADIUS_M: int = int(os.getenv("DEMO_RADIUS_M", "50000"))
    
    # Logging configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        try:
            # Validate MCP port
            if not (1 <= cls.MCP_PORT <= 65535):
                raise ValueError("MCP_PORT must be between 1 and 65535")
            
            # Validate GOR URL
            if not cls.GOR_BASE_URL.startswith(("http://", "https://")):
                raise ValueError("GOR_BASE_URL must be a valid HTTP URL")
            
            # Validate search defaults
            if cls.DEFAULT_SEARCH_RADIUS_M <= 0:
                raise ValueError("DEFAULT_SEARCH_RADIUS_M must be positive")
            
            if cls.DEFAULT_SEARCH_LIMIT <= 0:
                raise ValueError("DEFAULT_SEARCH_LIMIT must be positive")
            
            # Validate demo coordinates
            if not (-90 <= cls.DEMO_LAT <= 90):
                raise ValueError("DEMO_LAT must be between -90 and 90")
            
            if not (-180 <= cls.DEMO_LNG <= 180):
                raise ValueError("DEMO_LNG must be between -180 and 180")
            
            return True
            
        except Exception as e:
            print(f"❌ Configuration validation failed: {e}")
            return False


# Global config instance
config = Config()
