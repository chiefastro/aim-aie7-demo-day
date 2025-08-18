"""MCP client for consumer agent to communicate with MCP Offers server"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from mcp import ClientSession
from mcp.types import TextContent

logger = logging.getLogger(__name__)


class MCPClient:
    """Client for communicating with MCP Offers server"""
    
    def __init__(self, host: str = "localhost", port: int = 3002):
        self.host = host
        self.port = port
        self.session: Optional[ClientSession] = None
        self.available_tools = []
    
    async def connect(self) -> bool:
        """Connect to MCP server"""
        try:
            # Create connection to MCP server
            # Note: In a real implementation, this would use proper MCP connection
            # For demo purposes, we'll simulate the connection
            
            # Simulate connection delay
            await asyncio.sleep(0.1)
            
            # Get available tools
            self.available_tools = [
                "offers.search",
                "offers.getById", 
                "offers.nearby"
            ]
            
            logger.info(f"✅ Connected to MCP server at {self.host}:{self.port}")
            logger.info(f"Available tools: {', '.join(self.available_tools)}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to MCP server: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from MCP server"""
        if self.session:
            await self.session.close()
            self.session = None
        
        logger.info("👋 Disconnected from MCP server")
    
    async def search_offers(
        self,
        query: Optional[str] = None,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        radius_m: Optional[int] = None,
        labels: Optional[List[str]] = None,
        limit: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Search for offers using MCP offers.search tool"""
        try:
            # Build tool arguments
            arguments = {}
            if query:
                arguments["query"] = query
            if lat is not None:
                arguments["lat"] = lat
            if lng is not None:
                arguments["lng"] = lng
            if radius_m:
                arguments["radius_m"] = radius_m
            if labels:
                arguments["labels"] = labels
            if limit:
                arguments["limit"] = limit
            
            # Simulate MCP tool call
            logger.info(f"🔍 Calling offers.search with arguments: {arguments}")
            
            # For demo purposes, return mock data
            # In real implementation, this would call the actual MCP tool
            return await self._mock_search_offers(arguments)
            
        except Exception as e:
            logger.error(f"Search offers failed: {e}")
            return None
    
    async def get_offer_by_id(self, offer_id: str) -> Optional[Dict[str, Any]]:
        """Get offer details using MCP offers.getById tool"""
        try:
            arguments = {"offer_id": offer_id}
            
            logger.info(f"📋 Calling offers.getById with offer_id: {offer_id}")
            
            # For demo purposes, return mock data
            return await self._mock_get_offer_by_id(offer_id)
            
        except Exception as e:
            logger.error(f"Get offer by ID failed: {e}")
            return None
    
    async def get_nearby_offers(
        self,
        lat: float,
        lng: float,
        radius_m: Optional[int] = None,
        limit: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Find nearby offers using MCP offers.nearby tool"""
        try:
            arguments = {
                "lat": lat,
                "lng": lng,
                "radius_m": radius_m or 50000,
                "limit": limit or 20
            }
            
            logger.info(f"📍 Calling offers.nearby with arguments: {arguments}")
            
            # For demo purposes, return mock data
            return await self._mock_nearby_offers(arguments)
            
        except Exception as e:
            logger.error(f"Get nearby offers failed: {e}")
            return None
    
    async def _mock_search_offers(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Mock implementation for demo purposes"""
        query = arguments.get("query", "")
        lat = arguments.get("lat")
        lng = arguments.get("lng")
        radius_m = arguments.get("radius_m", 50000)
        limit = arguments.get("limit", 20)
        
        # Simulate API delay
        await asyncio.sleep(0.5)
        
        # Generate mock results based on query
        if "pizza" in query.lower():
            offers = [
                {
                    "offer_id": "ofr_001",
                    "title": "Pizza Delivery Special",
                    "description": "Get 20% off on all pizza orders with delivery",
                    "merchant": {
                        "name": "OTTO Portland",
                        "location": {
                            "city": "Dover",
                            "state": "NH"
                        }
                    },
                    "bounty": {
                        "amount": 2.50,
                        "currency": "USD",
                        "revenue_split": {"user": 50, "agent": 40, "associate": 10}
                    },
                    "labels": ["pizza", "delivery", "italian"]
                },
                {
                    "offer_id": "ofr_002", 
                    "title": "Margherita Pizza Deal",
                    "description": "Classic Margherita pizza at special price",
                    "merchant": {
                        "name": "Street Exeter",
                        "location": {
                            "city": "Exeter",
                            "state": "NH"
                        }
                    },
                    "bounty": {
                        "amount": 2.00,
                        "currency": "USD",
                        "revenue_split": {"user": 50, "agent": 40, "associate": 10}
                    },
                    "labels": ["pizza", "italian", "dine-in"]
                }
            ]
        elif "seafood" in query.lower():
            offers = [
                {
                    "offer_id": "ofr_003",
                    "title": "Lobster Special",
                    "description": "Fresh Maine lobster with sides",
                    "merchant": {
                        "name": "Newick's Lobster House",
                        "location": {
                            "city": "Dover",
                            "state": "NH"
                        }
                    },
                    "bounty": {
                        "amount": 3.00,
                        "currency": "USD",
                        "revenue_split": {"user": 50, "agent": 40, "associate": 10}
                    },
                    "labels": ["seafood", "lobster", "dine-in"]
                }
            ]
        else:
            # Generic offers
            offers = [
                {
                    "offer_id": "ofr_001",
                    "title": "Restaurant Special",
                    "description": "Special offer from local restaurant",
                    "merchant": {
                        "name": "Local Restaurant",
                        "location": {
                            "city": "Boston",
                            "state": "MA"
                        }
                    },
                    "bounty": {
                        "amount": 2.50,
                        "currency": "USD",
                        "revenue_split": {"user": 50, "agent": 40, "associate": 10}
                    },
                    "labels": ["restaurant", "local"]
                }
            ]
        
        # Limit results
        offers = offers[:limit]
        
        return {
            "offers": offers,
            "total": len(offers),
            "limit": limit,
            "offset": 0
        }
    
    async def _mock_get_offer_by_id(self, offer_id: str) -> Optional[Dict[str, Any]]:
        """Mock implementation for getting offer by ID"""
        # Simulate API delay
        await asyncio.sleep(0.3)
        
        # Mock offer data based on ID
        if offer_id == "ofr_001":
            return {
                "offer_id": "ofr_001",
                "title": "Pizza Delivery Special",
                "description": "Get 20% off on all pizza orders with delivery. Valid for online orders only.",
                "merchant": {
                    "name": "OTTO Portland",
                    "location": {
                        "address": "431 Central Avenue",
                        "city": "Dover",
                        "state": "NH",
                        "zip": "03820"
                    },
                    "hours": ["11:00 AM - 10:00 PM Daily"]
                },
                "bounty": {
                    "amount": 2.50,
                    "currency": "USD",
                    "revenue_split": {"user": 50, "agent": 40, "associate": 10}
                },
                "labels": ["pizza", "delivery", "italian", "online"],
                "terms": {
                    "valid_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                    "valid_hours": {"start": "11:00", "end": "22:00"}
                },
                "content": {
                    "cuisine_type": "Italian",
                    "featured_items": ["Cheese Pizza", "Margherita", "Pepperoni"]
                }
            }
        elif offer_id == "ofr_002":
            return {
                "offer_id": "ofr_002",
                "title": "Margherita Pizza Deal",
                "description": "Classic Margherita pizza at special price. Dine-in only.",
                "merchant": {
                    "name": "Street Exeter",
                    "location": {
                        "address": "8 Clifford Street",
                        "city": "Exeter",
                        "state": "NH"
                    },
                    "hours": ["11:00 AM - 10:00 PM Daily"]
                },
                "bounty": {
                    "amount": 2.00,
                    "currency": "USD",
                    "revenue_split": {"user": 50, "agent": 40, "associate": 10}
                },
                "labels": ["pizza", "italian", "dine-in"],
                "terms": {
                    "valid_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                    "valid_hours": {"start": "11:00", "end": "22:00"}
                },
                "content": {
                    "cuisine_type": "Italian",
                    "featured_items": ["Margherita Pizza", "House Special"]
                }
            }
        elif offer_id == "ofr_003":
            return {
                "offer_id": "ofr_003",
                "title": "Lobster Special",
                "description": "Fresh Maine lobster with sides. Seasonal offer.",
                "merchant": {
                    "name": "Newick's Lobster House",
                    "location": {
                        "address": "431 Dover Point Rd",
                        "city": "Dover",
                        "state": "NH"
                    },
                    "hours": ["11:00 AM - 10:00 PM Daily"]
                },
                "bounty": {
                    "amount": 3.00,
                    "currency": "USD",
                    "revenue_split": {"user": 50, "agent": 40, "associate": 10}
                },
                "labels": ["seafood", "lobster", "dine-in", "seasonal"],
                "terms": {
                    "valid_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                    "valid_hours": {"start": "11:00", "end": "22:00"}
                },
                "content": {
                    "cuisine_type": "Seafood",
                    "featured_items": ["Maine Lobster", "Clam Chowder", "Fish & Chips"]
                }
            }
        
        return None
    
    async def _mock_nearby_offers(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Mock implementation for nearby offers"""
        lat = arguments["lat"]
        lng = arguments["lng"]
        radius_m = arguments["radius_m"]
        limit = arguments["limit"]
        
        # Simulate API delay
        await asyncio.sleep(0.4)
        
        # Generate mock nearby offers
        offers = [
            {
                "offer_id": "ofr_001",
                "title": "Pizza Delivery Special",
                "description": "Get 20% off on all pizza orders with delivery",
                "merchant": {
                    "name": "OTTO Portland",
                    "location": {
                        "city": "Dover",
                        "state": "NH"
                    }
                },
                "bounty": {
                    "amount": 2.50,
                    "currency": "USD",
                    "revenue_split": {"user": 50, "agent": 40, "associate": 10}
                },
                "labels": ["pizza", "delivery", "italian"]
            },
            {
                "offer_id": "ofr_002",
                "title": "Margherita Pizza Deal", 
                "description": "Classic Margherita pizza at special price",
                "merchant": {
                    "name": "Street Exeter",
                    "location": {
                        "city": "Exeter",
                        "state": "NH"
                    }
                },
                "bounty": {
                    "amount": 2.00,
                    "currency": "USD",
                    "revenue_split": {"user": 50, "agent": 40, "associate": 10}
                },
                "labels": ["pizza", "italian", "dine-in"]
            }
        ]
        
        # Limit results
        offers = offers[:limit]
        
        return {
            "offers": offers,
            "total": len(offers),
            "limit": limit,
            "offset": 0
        }
