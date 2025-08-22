"""
ACP MCP Server - Universal commerce MCP server for ACP-compliant merchants.
"""

import logging
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

from .a2a_client import ACPClient
from .a2a_client import (
    CommerceRequest,
    CommerceResponse,
    MerchantInfo,
    OrderRequest,
    PaymentRequest,
    OfferValidationRequest,
)
from ..models.mcp_connector import OrderItem, MerchantDiscovery
from ..discovery.gor_client import GORClient
from ..models.offers import (
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
mcp = FastMCP(name="acp-mcp")

# ACP client will be initialized in main() function
acp_client = None

# Initialize GOR client for offer discovery
try:
    gor_client = GORClient()
    logger.info("GOR client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize GOR client: {e}")
    gor_client = None


@mcp.tool()
async def discover_merchants(
    query: Optional[str] = None,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    radius_m: Optional[int] = None,
    cuisine_type: Optional[str] = None
) -> str:
    """Discover ACP-compliant merchants"""
    try:
        logger.info(f"Discover merchants called with: query={query}, cuisine_type={cuisine_type}")
        
        if acp_client is None:
            return "❌ ACP client not initialized. Please check the server configuration."
        
        # Ensure proper type conversion
        try:
            if lat is not None:
                lat = float(lat)
            if lng is not None:
                lng = float(lng)
            if radius_m is not None:
                radius_m = int(radius_m)
        except (ValueError, TypeError) as e:
            logger.error(f"Parameter conversion failed: {e}")
            return f"❌ Invalid parameter values. Please provide valid numbers for lat, lng, and radius_m."
        
        arguments = {
            "query": query,
            "location": {"lat": lat, "lng": lng, "radius_m": radius_m} if lat and lng else {},
            "cuisine_type": cuisine_type
        }
        result = handle_discover_merchants(arguments)
        return result[0].text if result else "No merchants found"
    except Exception as e:
        logger.error(f"Unexpected error in discover merchants: {e}")
        return f"❌ Merchant discovery failed: {str(e)}"


@mcp.tool()
async def order_food(
    merchant_id: str,
    items: List[Dict[str, Any]],
    offer_id: Optional[str] = None,
    pickup: bool = True,
    delivery_address: Optional[Dict[str, str]] = None,
    special_instructions: Optional[str] = None
) -> str:
    """Place a food order with an ACP-compliant merchant"""
    try:
        logger.info(f"Order food called with: merchant_id={merchant_id}, items_count={len(items)}")
        
        if acp_client is None:
            return "❌ ACP client not initialized. Please check the server configuration."
        
        arguments = {
            "merchant_id": merchant_id,
            "items": items,
            "offer_id": offer_id,
            "pickup": pickup,
            "delivery_address": delivery_address,
            "special_instructions": special_instructions
        }
        result = await handle_order_food(arguments)
        return result[0].text if result else "Order failed"
    except Exception as e:
        logger.error(f"Unexpected error in order food: {e}")
        return f"❌ Order failed: {str(e)}"


@mcp.tool()
async def validate_offer(
    merchant_id: str,
    offer_id: str,
    items: List[Dict[str, Any]]
) -> str:
    """Validate an offer with an ACP-compliant merchant"""
    try:
        logger.info(f"Validate offer called with: merchant_id={merchant_id}, offer_id={offer_id}")
        
        if acp_client is None:
            return "❌ ACP client not initialized. Please check the server configuration."
        
        arguments = {
            "merchant_id": merchant_id,
            "offer_id": offer_id,
            "items": items
        }
        result = await handle_validate_offer(arguments)
        return result[0].text if result else "Offer validation failed"
    except Exception as e:
        logger.error(f"Unexpected error in validate offer: {e}")
        return f"❌ Offer validation failed: {str(e)}"


@mcp.tool()
async def process_payment(
    merchant_id: str,
    order_id: str,
    amount: float,
    payment_method: str,
    payment_details: Optional[Dict[str, Any]] = None
) -> str:
    """Process payment with an ACP-compliant merchant"""
    try:
        logger.info(f"Process payment called with: merchant_id={merchant_id}, order_id={order_id}, amount={amount}")
        
        if acp_client is None:
            return "❌ ACP client not initialized. Please check the server configuration."
        
        # Ensure proper type conversion
        try:
            amount = float(amount)
        except (ValueError, TypeError) as e:
            logger.error(f"Parameter conversion failed: {e}")
            return f"❌ Invalid amount value. Please provide a valid number."
        
        arguments = {
            "merchant_id": merchant_id,
            "order_id": order_id,
            "amount": amount,
            "payment_method": payment_method,
            "payment_details": payment_details or {}
        }
        result = await handle_process_payment(arguments)
        return result[0].text if result else "Payment failed"
    except Exception as e:
        logger.error(f"Unexpected error in process payment: {e}")
        return f"❌ Payment failed: {str(e)}"


@mcp.tool()
async def get_menu(
    merchant_id: str,
    category: Optional[str] = None
) -> str:
    """Get menu from an ACP-compliant merchant"""
    try:
        logger.info(f"Get menu called with: merchant_id={merchant_id}, category={category}")
        
        if acp_client is None:
            return "❌ ACP client not initialized. Please check the server configuration."
        
        arguments = {
            "merchant_id": merchant_id,
            "category": category
        }
        result = await handle_get_menu(arguments)
        return result[0].text if result else "Menu retrieval failed"
    except Exception as e:
        logger.error(f"Unexpected error in get menu: {e}")
        return f"❌ Menu retrieval failed: {str(e)}"


@mcp.tool()
async def track_order(
    merchant_id: str,
    order_id: str
) -> str:
    """Track order status with an ACP-compliant merchant"""
    try:
        logger.info(f"Track order called with: merchant_id={merchant_id}, order_id={order_id}")
        
        if acp_client is None:
            return "❌ ACP client not initialized. Please check the server configuration."
        
        arguments = {
            "merchant_id": merchant_id,
            "order_id": order_id
        }
        result = handle_track_order(arguments)
        return result[0].text if result else "Order tracking failed"
    except Exception as e:
        logger.error(f"Unexpected error in track order: {e}")
        return f"❌ Order tracking failed: {str(e)}"


# Offer Discovery Tools
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


def handle_discover_merchants(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle discover_merchants tool call"""
    try:
        query = arguments.get("query", "")
        location = arguments.get("location", {})
        cuisine_type = arguments.get("cuisine_type")
        
        # For now, return mock merchants
        # In a real implementation, this would query a merchant registry
        mock_merchants = [
            {
                "merchant_id": "otto_portland",
                "name": "OTTO Portland",
                "description": "Artisan pizza and Italian cuisine",
                "agent_url": "http://localhost:4001",
                "capabilities": ["order_food", "validate_offer", "process_payment"],
                "location": {"lat": 45.5152, "lng": -122.6784},
                "cuisine_type": "Italian",
                "rating": 4.5,
                "is_acp_compliant": True
            },
            {
                "merchant_id": "street_exeter",
                "name": "Street Exeter",
                "description": "Modern British cuisine",
                "agent_url": "http://localhost:4002",
                "capabilities": ["order_food", "validate_offer", "process_payment"],
                "location": {"lat": 50.7184, "lng": -3.5339},
                "cuisine_type": "British",
                "rating": 4.3,
                "is_acp_compliant": True
            },
            {
                "merchant_id": "newicks_lobster",
                "name": "Newick's Lobster House",
                "description": "Fresh seafood and lobster",
                "agent_url": "http://localhost:4003",
                "capabilities": ["order_food", "validate_offer", "process_payment"],
                "location": {"lat": 43.0587, "lng": -70.7626},
                "cuisine_type": "Seafood",
                "rating": 4.7,
                "is_acp_compliant": True
            }
        ]
        
        # Filter by query if provided
        if query:
            mock_merchants = [
                m for m in mock_merchants 
                if query.lower() in m["name"].lower() or query.lower() in m["cuisine_type"].lower()
            ]
        
        # Filter by cuisine type if provided
        if cuisine_type:
            mock_merchants = [
                m for m in mock_merchants 
                if cuisine_type.lower() == m["cuisine_type"].lower()
            ]
        
        if not mock_merchants:
            return [TextContent(
                type="text",
                text=f"🔍 No merchants found for query: {query or 'all merchants'}"
            )]
        
        # Build response text
        response_text = f"🔍 Found {len(mock_merchants)} ACP-compliant merchants"
        if query:
            response_text += f" for '{query}'"
        if cuisine_type:
            response_text += f" with cuisine type '{cuisine_type}'"
        response_text += f"\n\n"
        
        for i, merchant in enumerate(mock_merchants, 1):
            response_text += f"{i}. **{merchant['name']}**\n"
            response_text += f"   📝 {merchant['description']}\n"
            response_text += f"   🏪 {merchant['cuisine_type']} cuisine\n"
            response_text += f"   ⭐ Rating: {merchant['rating']}/5\n"
            response_text += f"   🆔 {merchant['merchant_id']}\n"
            response_text += f"   🌐 {merchant['agent_url']}\n\n"
        
        return [TextContent(
            type="text",
            text=response_text
        )]
        
    except Exception as e:
        logger.error(f"Discover merchants failed: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Merchant discovery failed: {str(e)}"
        )]


async def handle_order_food(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle order_food tool call"""
    try:
        merchant_id = arguments["merchant_id"]
        items_data = arguments["items"]
        offer_id = arguments.get("offer_id")
        pickup = arguments.get("pickup", True)
        delivery_address = arguments.get("delivery_address")
        special_instructions = arguments.get("special_instructions")
        
        # Convert items to OrderItem objects
        items = [
            OrderItem(
                name=item["name"],
                quantity=item["quantity"],
                price=item.get("price"),
                notes=item.get("notes")
            )
            for item in items_data
        ]
        
        # Create order request
        request = OrderRequest(
            merchant_id=merchant_id,
            items=items,
            offer_id=offer_id,
            pickup=pickup,
            delivery_address=delivery_address,
            special_instructions=special_instructions
        )
        
        # Execute order
        response = await acp_client.order_food(request)
        
        if response.success:
            response_text = f"✅ Order placed successfully!\n\n"
            response_text += f"**Order ID**: {response.data.get('order_id', 'N/A')}\n"
            response_text += f"**Total**: ${response.data.get('total', 'N/A')}\n"
            response_text += f"**Status**: {response.data.get('status', 'N/A')}\n"
            response_text += f"**Merchant**: {merchant_id}\n"
            
            if offer_id:
                response_text += f"**Offer Applied**: {offer_id}\n"
            
            if special_instructions:
                response_text += f"**Special Instructions**: {special_instructions}\n"
        else:
            response_text = f"❌ Order failed: {response.error_message}"
        
        return [TextContent(
            type="text",
            text=response_text
        )]
        
    except Exception as e:
        logger.error(f"Order food failed: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Order failed: {str(e)}"
        )]


async def handle_validate_offer(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle validate_offer tool call"""
    try:
        merchant_id = arguments["merchant_id"]
        offer_id = arguments["offer_id"]
        items_data = arguments["items"]
        
        # Convert items to OrderItem objects
        items = [
            OrderItem(
                name=item["name"],
                quantity=item["quantity"],
                price=item.get("price")
            )
            for item in items_data
        ]
        
        # Create validation request
        request = OfferValidationRequest(
            merchant_id=merchant_id,
            offer_id=offer_id,
            items=items
        )
        
        # Execute validation
        response = await acp_client.validate_offer(request)
        
        if response.success:
            is_valid = response.data.get("is_valid", False)
            discount_amount = response.data.get("discount_amount")
            restrictions_violated = response.data.get("restrictions_violated", [])
            
            if is_valid:
                response_text = f"✅ Offer {offer_id} is valid!\n\n"
                if discount_amount:
                    response_text += f"**Discount Amount**: ${discount_amount}\n"
                response_text += f"**Merchant**: {merchant_id}\n"
            else:
                response_text = f"❌ Offer {offer_id} is not valid\n\n"
                if restrictions_violated:
                    response_text += f"**Violated Restrictions**: {', '.join(restrictions_violated)}\n"
                response_text += f"**Merchant**: {merchant_id}\n"
        else:
            response_text = f"❌ Offer validation failed: {response.error_message}"
        
        return [TextContent(
            type="text",
            text=response_text
        )]
        
    except Exception as e:
        logger.error(f"Validate offer failed: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Offer validation failed: {str(e)}"
        )]


async def handle_process_payment(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle process_payment tool call"""
    try:
        merchant_id = arguments["merchant_id"]
        order_id = arguments["order_id"]
        amount = arguments["amount"]
        payment_method = arguments["payment_method"]
        payment_details = arguments.get("payment_details", {})
        
        # Create payment request
        request = PaymentRequest(
            merchant_id=merchant_id,
            order_id=order_id,
            amount=amount,
            payment_method=payment_method,
            payment_details=payment_details
        )
        
        # Execute payment
        response = await acp_client.process_payment(request)
        
        if response.success:
            response_text = f"✅ Payment processed successfully!\n\n"
            response_text += f"**Payment ID**: {response.data.get('payment_id', 'N/A')}\n"
            response_text += f"**Order ID**: {order_id}\n"
            response_text += f"**Amount**: ${amount}\n"
            response_text += f"**Status**: {response.data.get('status', 'N/A')}\n"
            response_text += f"**Method**: {payment_method}\n"
            response_text += f"**Merchant**: {merchant_id}\n"
            
            if response.data.get('transaction_id'):
                response_text += f"**Transaction ID**: {response.data['transaction_id']}\n"
        else:
            response_text = f"❌ Payment failed: {response.error_message}"
        
        return [TextContent(
            type="text",
            text=response_text
        )]
        
    except Exception as e:
        logger.error(f"Process payment failed: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Payment failed: {str(e)}"
        )]


async def handle_get_menu(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle get_menu tool call"""
    try:
        merchant_id = arguments["merchant_id"]
        category = arguments.get("category")
        
        # Execute menu request
        response = await acp_client.get_menu(merchant_id, category)
        
        if response.success:
            menu_items = response.data.get("menu_items", [])
            categories = response.data.get("categories", [])
            
            response_text = f"🍽️ Menu for {merchant_id}\n\n"
            
            if category:
                response_text += f"**Category**: {category}\n\n"
            
            if categories:
                response_text += f"**Available Categories**: {', '.join(categories)}\n\n"
            
            if menu_items:
                response_text += f"**Menu Items** ({len(menu_items)} items):\n\n"
                for i, item in enumerate(menu_items, 1):
                    response_text += f"{i}. **{item.get('name', 'N/A')}**\n"
                    if item.get('description'):
                        response_text += f"   📝 {item['description']}\n"
                    response_text += f"   💰 ${item.get('price', 'N/A')}\n"
                    if item.get('category'):
                        response_text += f"   📂 {item['category']}\n"
                    if not item.get('available', True):
                        response_text += f"   ❌ Not available\n"
                    response_text += "\n"
            else:
                response_text += "No menu items found."
        else:
            response_text = f"❌ Menu retrieval failed: {response.error_message}"
        
        return [TextContent(
            type="text",
            text=response_text
        )]
        
    except Exception as e:
        logger.error(f"Get menu failed: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Menu retrieval failed: {str(e)}"
        )]


def handle_track_order(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle track_order tool call"""
    try:
        merchant_id = arguments["merchant_id"]
        order_id = arguments["order_id"]
        
        # For now, return mock tracking info
        # In a real implementation, this would query the merchant agent
        response_text = f"📦 Order Tracking\n\n"
        response_text += f"**Order ID**: {order_id}\n"
        response_text += f"**Merchant**: {merchant_id}\n"
        response_text += f"**Status**: Preparing\n"
        response_text += f"**Estimated Ready Time**: 2024-01-15T19:30:00Z\n"
        response_text += f"**Last Updated**: 2024-01-15T19:15:00Z\n"
        
        return [TextContent(
            type="text",
            text=response_text
        )]
        
    except Exception as e:
        logger.error(f"Track order failed: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Order tracking failed: {str(e)}"
        )]


# Offer Discovery Handlers
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


def main(a2a_server_url: str = None):
    """Initialize ACP client and run MCP server."""
    global acp_client
    
    try:
        acp_client = ACPClient(a2a_server_url)
        logger.info(f"ACP client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize ACP client: {e}")
        acp_client = None
    
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
