"""MCP Offers Server - Semantic layer for ACP offers"""

import logging
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP
from mcp.types import (
    TextContent,
)
from .gor_client import GORClient
from .models import (
    SearchOffersInput,
    GetOfferByIdInput,
    NearbyOffersInput,
    SearchResponse,
    Offer,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP(name="mcp-offers")

# Initialize GOR client
try:
    gor_client = GORClient()
    logger.info("GOR client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize GOR client: {e}")
    gor_client = None


@mcp.tool()
def offers_search(
    query: Optional[str] = None,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    radius_m: Optional[int] = None,
    labels: Optional[List[str]] = None,
    limit: Optional[int] = None
) -> str:
    """Search for offers using semantic query with optional geo and label filters"""
    try:
        logger.info(f"Search offers called with: query={query}, lat={lat}, lng={lng}, radius_m={radius_m}, limit={limit}")
        
        # Ensure proper type conversion - handle string inputs from MCP
        try:
            if lat is not None:
                lat = float(lat)
            if lng is not None:
                lng = float(lng)
            if radius_m is not None:
                radius_m = int(radius_m)
            if limit is not None:
                limit = int(limit)
        except (ValueError, TypeError) as e:
            logger.error(f"Parameter conversion failed: {e}")
            return f"❌ Invalid parameter values. Please provide valid numbers for lat, lng, radius_m, and limit."
        
        arguments = {
            "query": query,
            "lat": lat,
            "lng": lng,
            "radius_m": radius_m,
            "labels": labels,
            "limit": limit
        }
        result = handle_search_offers(arguments)
        return result[0].text if result else "No results found"
    except (ValueError, TypeError) as e:
        logger.error(f"Parameter type error in search: {e}")
        return f"❌ Invalid parameter type: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error in search: {e}")
        return f"❌ Search failed: {str(e)}"

@mcp.tool()
def offers_get_by_id(offer_id: str) -> str:
    """Get a specific offer by its ID"""
    try:
        logger.info(f"Get offer by ID called with: offer_id={offer_id}")
        
        # Check if GOR client is available
        if gor_client is None:
            return "❌ GOR client not initialized. Please check the server configuration."
        if not gor_client.health_check():
            return "❌ GOR API is not available. Please check if the service is running."
        
        arguments = {"offer_id": offer_id}
        result = handle_get_offer_by_id(arguments)
        return result[0].text if result else "Offer not found"
    except Exception as e:
        logger.error(f"Unexpected error in get offer by ID: {e}")
        return f"❌ Get offer failed: {str(e)}"

@mcp.tool()
def offers_nearby(
    lat: float,
    lng: float,
    radius_m: int,
    limit: int
) -> str:
    """Find offers near a specific location"""
    try:
        logger.info(f"Nearby offers called with: lat={lat}, lng={lng}, radius_m={radius_m}, limit={limit}")
        
        # Ensure proper type conversion - handle string inputs from MCP
        try:
            lat = float(lat) if lat is not None else 0.0
            lng = float(lng) if lng is not None else 0.0
            radius_m = int(radius_m) if radius_m is not None else 50000
            limit = int(limit) if limit is not None else 20
        except (ValueError, TypeError) as e:
            logger.error(f"Parameter conversion failed: {e}")
            return f"❌ Invalid parameter values. Please provide valid numbers for lat, lng, radius_m, and limit."
        
        arguments = {
            "lat": lat,
            "lng": lng,
            "radius_m": radius_m,
            "limit": limit
        }
        result = handle_nearby_offers(arguments)
        return result[0].text if result else "No nearby offers found"
    except (ValueError, TypeError) as e:
        logger.error(f"Parameter type error in nearby: {e}")
        return f"❌ Invalid parameter type: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error in nearby: {e}")
        return f"❌ Nearby search failed: {str(e)}"





def handle_search_offers(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle offers.search tool call"""
    try:
        # Parse arguments
        params = SearchOffersInput(**arguments)
        
        # Check if GOR client is available
        if gor_client is None:
            return [TextContent(
                type="text",
                text="❌ GOR client not initialized. Please check the server configuration."
            )]
        if not gor_client.health_check():
            return [TextContent(
                type="text",
                text="❌ GOR API is not available. Please check if the service is running."
            )]
        
        # Call GOR API
        response = gor_client.search_offers(params)
        
        if not response.success:
            return [TextContent(
                type="text",
                text="❌ Search failed"
            )]
        
        # Format results
        results = response.results
        offers = results.offers
        
        if not offers:
            return [TextContent(
                type="text",
                text=f"🔍 No offers found for query: {params.query or 'all offers'}"
            )]
        
        # Build response text
        response_text = f"🔍 Found {results.total} offers"
        if params.query:
            response_text += f" for '{params.query}'"
        if params.lat and params.lng:
            response_text += f" near ({params.lat}, {params.lng})"
        response_text += f"\n\n"
        
        for i, offer in enumerate(offers[:params.limit or 20], 1):
            response_text += f"{i}. **{offer.title or offer.offer_id}**\n"
            if offer.merchant:
                response_text += f"   🏪 {offer.merchant.name}"
                if offer.merchant.location and offer.merchant.location.city:
                    response_text += f" ({offer.merchant.location.city})"
                response_text += "\n"
            
            if offer.bounty:
                response_text += f"   💰 ${offer.bounty.amount} bounty\n"
            
            if offer.labels:
                response_text += f"   🏷️  {', '.join(offer.labels)}\n"
            
            if offer.description:
                response_text += f"   📝 {offer.description}\n"
            
            response_text += f"   🆔 {offer.offer_id}\n\n"
        
        return [TextContent(
            type="text",
            text=response_text
        )]
        
    except Exception as e:
        logger.error(f"Search offers failed: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Search offers failed: {str(e)}"
        )]


def handle_get_offer_by_id(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle offers.getById tool call"""
    try:
        # Parse arguments
        params = GetOfferByIdInput(**arguments)
        
        # Check if GOR client is available
        if gor_client is None:
            return [TextContent(
                type="text",
                text="❌ GOR client not initialized. Please check the server configuration."
            )]
        if not gor_client.health_check():
            return [TextContent(
                type="text",
                text="❌ GOR API is not available. Please check if the service is running."
            )]
        
        # Call GOR API
        offer = gor_client.get_offer_by_id(params)
        
        # Format offer details
        response_text = f"📋 **Offer Details: {offer.offer_id}**\n\n"
        
        if offer.title:
            response_text += f"**Title**: {offer.title}\n"
        
        if offer.description:
            response_text += f"**Description**: {offer.description}\n"
        
        if offer.merchant:
            response_text += f"\n**Merchant**: {offer.merchant.name}"
            if offer.merchant.location:
                loc = offer.merchant.location
                if loc.city and loc.state:
                    response_text += f" ({loc.city}, {loc.state})"
                elif loc.address:
                    response_text += f" ({loc.address})"
            response_text += "\n"
            
            if offer.merchant.hours:
                response_text += f"**Hours**: {', '.join(offer.merchant.hours)}\n"
        
        if offer.bounty:
            response_text += f"\n**Bounty**: ${offer.bounty.amount} {offer.bounty.currency}\n"
            if offer.bounty.revenue_split:
                response_text += f"**Revenue Split**: "
                splits = []
                for party, share in offer.bounty.revenue_split.items():
                    splits.append(f"{party}: {share}%")
                response_text += ", ".join(splits) + "\n"
        
        if offer.labels:
            response_text += f"\n**Labels**: {', '.join(offer.labels)}\n"
        
        if offer.terms:
            if offer.terms.valid_days:
                response_text += f"**Valid Days**: {', '.join(offer.terms.valid_days)}\n"
            if offer.terms.valid_hours:
                response_text += f"**Valid Hours**: {offer.terms.valid_hours}\n"
        
        if offer.content:
            if offer.content.cuisine_type:
                response_text += f"\n**Cuisine**: {offer.content.cuisine_type}\n"
            if offer.content.featured_items:
                response_text += f"**Featured Items**: {', '.join(offer.content.featured_items)}\n"
        
        return [TextContent(
            type="text",
            text=response_text
        )]
        
    except Exception as e:
        logger.error(f"Get offer by ID failed: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Get offer failed: {str(e)}"
        )]


def handle_nearby_offers(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle offers.nearby tool call"""
    try:
        # Parse arguments
        params = NearbyOffersInput(**arguments)
        
        # Check if GOR client is available
        if gor_client is None:
            return [TextContent(
                type="text",
                text="❌ GOR client not initialized. Please check the server configuration."
            )]
        if not gor_client.health_check():
            return [TextContent(
                type="text",
                text="❌ GOR API is not available. Please check if the service is running."
            )]
        
        # Call GOR API
        response = gor_client.get_nearby_offers(params)
        
        if not response.success:
            return [TextContent(
                type="text",
                text="❌ Nearby search failed"
            )]
        
        # Format results
        results = response.results
        offers = results.offers
        
        if not offers:
            return [TextContent(
                type="text",
                text=f"📍 No offers found within {params.radius_m}m of ({params.lat}, {params.lng})"
            )]
        
        # Build response text
        response_text = f"📍 Found {results.total} offers within {params.radius_m}m of ({params.lat}, {params.lng})\n\n"
        
        for i, offer in enumerate(offers[:params.limit or 20], 1):
            response_text += f"{i}. **{offer.title or offer.offer_id}**\n"
            if offer.merchant:
                response_text += f"   🏪 {offer.merchant.name}"
                if offer.merchant.location:
                    loc = offer.merchant.location
                    if loc.city and loc.state:
                        response_text += f" ({loc.city}, {loc.state})"
                    elif loc.address:
                        response_text += f" ({loc.address})"
                response_text += "\n"
            
            if offer.bounty:
                response_text += f"   💰 ${offer.bounty.amount} bounty\n"
            
            if offer.labels:
                response_text += f"   🏷️  {', '.join(offer.labels)}\n"
            
            response_text += f"   🆔 {offer.offer_id}\n\n"
        
        return [TextContent(
            type="text",
            text=response_text
        )]
        
    except Exception as e:
        logger.error(f"Nearby offers failed: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Nearby offers failed: {str(e)}"
        )]



def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
