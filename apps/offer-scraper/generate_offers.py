#!/usr/bin/env python3
"""
ACP Offer Generator using LangGraph
Generates realistic offer documents from scraped restaurant data
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import requests
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from langchain_core.messages import HumanMessage, AIMessage
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RestaurantData:
    """Structured restaurant data"""
    name: str
    url: str
    address: str
    phone: str
    hours: List[str]
    menu_items: List[Dict[str, Any]]
    cuisine_type: str
    price_range: str
    description: str

@dataclass
class OfferDocument:
    """Structured offer document"""
    offer_id: str
    title: str
    description: str
    restaurant_description: str
    featured_items: List[str]
    min_spend: float
    bounty_amount: float
    location: Dict[str, Any]
    labels: List[str]
    content: Dict[str, Any]

class GeocodingTool:
    """Mapbox geocoding tool"""
    
    def __init__(self, mapbox_token: str):
        self.mapbox_token = mapbox_token
        self.base_url = "https://api.mapbox.com/geocoding/v5/mapbox.places"
    
    def geocode_address(self, address: str) -> Dict[str, Any]:
        """Geocode an address using Mapbox"""
        try:
            params = {
                'access_token': self.mapbox_token,
                'query': address,
                'country': 'US',
                'types': 'address'
            }
            
            response = requests.get(f"{self.base_url}/{address}.json", params=params)
            response.raise_for_status()
            
            data = response.json()
            if data['features']:
                feature = data['features'][0]
                center = feature['center']
                return {
                    'lat': center[1],
                    'lng': center[0],
                    'formatted_address': feature['place_name'],
                    'confidence': feature.get('relevance', 0)
                }
            else:
                logger.warning(f"No geocoding results for: {address}")
                return None
                
        except Exception as e:
            logger.error(f"Geocoding error for {address}: {e}")
            return None

class RestaurantAnalyzer:
    """Analyzes restaurant data to extract key information"""
    
    def analyze_menu(self, menu_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze menu items to determine cuisine, price range, etc."""
        if not menu_items:
            return {'cuisine': 'unknown', 'price_range': '$$', 'popular_items': []}
        
        # Extract all item names and prices
        all_names = ' '.join([item.get('name', '') for item in menu_items]).lower()
        prices = []
        popular_items = []
        
        for item in menu_items:
            price_str = item.get('price', '')
            if price_str and '$' in price_str:
                try:
                    price = float(price_str.replace('$', '').replace(',', ''))
                    prices.append(price)
                    if price > 10:  # Consider items over $10 as "popular"
                        popular_items.append(f"{item.get('name', '')} - {price_str}")
                except ValueError:
                    continue
        
        # Determine cuisine type
        cuisine = 'casual dining'
        if any(word in all_names for word in ['pizza', 'margherita', 'pepperoni']):
            cuisine = 'Italian pizza'
        elif any(word in all_names for word in ['lobster', 'clam', 'haddock', 'scallop', 'fish']):
            cuisine = 'seafood'
        elif any(word in all_names for word in ['bibimbap', 'curry', 'taco', 'burrito']):
            cuisine = 'international fusion'
        elif any(word in all_names for word in ['burger', 'sandwich']):
            cuisine = 'American'
        
        # Determine price range
        price_range = '$$'
        if prices:
            max_price = max(prices)
            if max_price <= 15:
                price_range = '$'
            elif max_price <= 30:
                price_range = '$$'
            elif max_price <= 60:
                price_range = '$$$'
            else:
                price_range = '$$$$'
        
        return {
            'cuisine': cuisine,
            'price_range': price_range,
            'popular_items': popular_items[:5],  # Top 5 popular items
            'avg_price': sum(prices) / len(prices) if prices else 0
        }
    
    def generate_restaurant_description(self, restaurant_data: RestaurantData) -> str:
        """Generate a rich description for the restaurant"""
        popular_items = restaurant_data.menu_items[:5]
        item_names = [item.get('name', '') for item in popular_items]
        
        description = f"{restaurant_data.name} is a {restaurant_data.cuisine_type} restaurant "
        description += f"serving {', '.join(item_names)} and more. "
        description += f"Open {restaurant_data.hours[0] if restaurant_data.hours else '11:00 AM - 10:00 PM'}. "
        description += f"Located in {restaurant_data.address}."
        
        return description

class OfferGenerator:
    """Generates realistic offer documents"""
    
    def __init__(self, mapbox_token: str):
        self.geocoder = GeocodingTool(mapbox_token)
        self.analyzer = RestaurantAnalyzer()
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
    
    def generate_labels(self, restaurant_data: RestaurantData, offer_type: str) -> List[str]:
        """Generate searchable labels for the offer"""
        labels = set()
        
        # Cuisine labels
        menu_text = ' '.join([item.get('name', '') for item in restaurant_data.menu_items]).lower()
        
        if 'pizza' in menu_text:
            labels.update(['pizza', 'italian'])
        if 'lobster' in menu_text or 'clam' in menu_text or 'haddock' in menu_text:
            labels.update(['seafood', 'lobster', 'fish'])
        if 'bibimbap' in menu_text:
            labels.update(['korean', 'asian'])
        if 'curry' in menu_text:
            labels.update(['indian', 'asian'])
        if 'taco' in menu_text:
            labels.update(['mexican'])
        if 'burger' in menu_text:
            labels.update(['burger', 'american'])
        
        # Meal type labels
        labels.add(offer_type)
        if offer_type == 'lunch':
            labels.update(['lunch', 'midday'])
        else:
            labels.update(['dinner', 'evening'])
        
        # Service labels
        labels.update(['dine-in', 'takeout'])
        
        # Location labels
        labels.update(['dover-nh', 'new-hampshire', 'seacoast'])
        
        return list(labels)
    
    def generate_offer(self, restaurant_data: RestaurantData, offer_type: str = 'lunch') -> OfferDocument:
        """Generate a realistic offer document"""
        
        # Geocode the address
        location_data = self.geocoder.geocode_address(restaurant_data.address)
        if not location_data:
            # Fallback coordinates for Dover, NH
            location_data = {
                'lat': 43.1979,
                'lng': -70.8737,
                'formatted_address': restaurant_data.address
            }
        
        # Analyze menu for offer generation
        menu_analysis = self.analyzer.analyze_menu(restaurant_data.menu_items)
        
        # Select featured items based on offer type
        if offer_type == 'lunch':
            featured_items = [item for item in restaurant_data.menu_items 
                            if item.get('price') and 
                            float(item.get('price', '0').replace('$', '')) <= 20]
            min_spend = 15
            description = f"Lunch special at {restaurant_data.name}. Get $2.50 back when you spend ${min_spend} or more on lunch items."
        else:
            featured_items = [item for item in restaurant_data.menu_items 
                            if item.get('price') and 
                            float(item.get('price', '0').replace('$', '')) > 15]
            min_spend = 25
            description = f"Dinner offer at {restaurant_data.name}. Get $2.50 back when you spend ${min_spend} or more on dinner entrees."
        
        # Take top 3 featured items
        featured_items = featured_items[:3]
        featured_descriptions = [f"{item.get('name', '')} - {item.get('price', '')}" 
                               for item in featured_items]
        
        # Generate restaurant description
        restaurant_description = self.analyzer.generate_restaurant_description(restaurant_data)
        
        # Generate labels
        labels = self.generate_labels(restaurant_data, offer_type)
        
        return OfferDocument(
            offer_id=f"ofr_001" if offer_type == 'lunch' else "ofr_002",
            title=f"{restaurant_data.name} {offer_type.title()} Offer",
            description=description,
            restaurant_description=restaurant_description,
            featured_items=featured_descriptions,
            min_spend=min_spend,
            bounty_amount=2.50,
            location={
                'lat': location_data['lat'],
                'lng': location_data['lng'],
                'address': location_data['formatted_address'],
                'city': 'Dover',
                'state': 'NH',
                'zip': '03820'
            },
            labels=labels,
            content={
                'cuisine_type': menu_analysis['cuisine'],
                'price_range': menu_analysis['price_range'],
                'popular_items': menu_analysis['popular_items'],
                'avg_price': menu_analysis['avg_price']
            }
        )
    
    def create_acp_offer_document(self, offer: OfferDocument, restaurant_data: RestaurantData) -> Dict[str, Any]:
        """Create the full ACP offer document structure"""
        
        return {
            "offer_id": offer.offer_id,
            "offer_version": "1.0",
            "created_at": "2025-01-15T00:00:00Z",
            "updated_at": "2025-01-15T00:00:00Z",
            "expires_at": "2025-02-15T00:00:00Z",
            
            "title": offer.title,
            "description": offer.description,
            
            "content": {
                "restaurant_description": offer.restaurant_description,
                "featured_items": offer.featured_items,
                "cuisine_type": offer.content['cuisine_type'],
                "price_range": offer.content['price_range'],
                "dietary_options": []
            },
            
            "terms": {
                "min_spend": offer.min_spend,
                "max_discount": offer.bounty_amount,
                "valid_days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
                "valid_hours": {
                    "start": "11:00",
                    "end": "22:00"
                },
                "restrictions": [
                    "Valid for dine-in and takeout orders",
                    "Cannot be combined with other offers",
                    "Valid only at this location"
                ]
            },
            
            "bounty": {
                "amount": offer.bounty_amount,
                "currency": "USD",
                "revenue_split": {
                    "consumer": 50,
                    "merchant": 40,
                    "platform": 10
                }
            },
            
            "merchant": {
                "id": f"toast_{restaurant_data.name.lower().replace(' ', '_').replace(\"'\", '')}",
                "name": restaurant_data.name,
                "location": offer.location,
                "phone": restaurant_data.phone,
                "hours": restaurant_data.hours
            },
            
            "attribution": {
                "method": "receipt_upload",
                "instructions": "Upload your receipt after dining to receive your bounty",
                "required_fields": ["total_amount", "date", "items"]
            },
            
            "provenance": {
                "source": "merchant_direct",
                "verified": True,
                "last_verified": "2025-01-15T00:00:00Z"
            },
            
            "labels": offer.labels,
            
            "search_metadata": {
                "cuisine": offer.content['cuisine_type'],
                "price_range": offer.content['price_range'],
                "location": {
                    "city": "Dover",
                    "state": "NH",
                    "coordinates": [offer.location['lng'], offer.location['lat']]
                },
                "meal_type": "lunch" if offer.offer_id == "ofr_001" else "dinner",
                "dietary_restrictions": [],
                "popular_items": offer.content['popular_items']
            }
        }

def load_scraped_data(scraped_dir: Path) -> List[RestaurantData]:
    """Load and parse scraped restaurant data"""
    restaurants = []
    
    for json_file in scraped_dir.glob("*.json"):
        if json_file.name.startswith("batch-results"):
            continue
            
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            if data.get('error'):
                logger.warning(f"Skipping {json_file.name} due to error: {data['error']}")
                continue
            
            # Extract menu items
            menu_items = []
            for category in data.get('menu', []):
                menu_items.extend(category.get('items', []))
            
            # Create restaurant data
            restaurant = RestaurantData(
                name=data['merchant']['name'],
                url=data['url'],
                address=data['location']['address'],
                phone=data['merchant'].get('phone', 'Call'),
                hours=data.get('hours', ['11:00 am - 10:00 pm']),
                menu_items=menu_items,
                cuisine_type='',  # Will be determined by analyzer
                price_range='$$',
                description=''
            )
            
            restaurants.append(restaurant)
            logger.info(f"Loaded restaurant: {restaurant.name}")
            
        except Exception as e:
            logger.error(f"Error loading {json_file.name}: {e}")
    
    return restaurants

async def main():
    """Main function"""
    # Load environment variables
    mapbox_token = os.getenv('MAPBOX_TOKEN')
    if not mapbox_token:
        logger.error("MAPBOX_TOKEN environment variable not set")
        return
    
    # Setup paths
    base_dir = Path(__file__).parent.parent.parent
    scraped_dir = base_dir / "data" / "scraped"
    output_dir = base_dir / "data" / "osf"
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load scraped data
    restaurants = load_scraped_data(scraped_dir)
    logger.info(f"Loaded {len(restaurants)} restaurants")
    
    # Initialize offer generator
    generator = OfferGenerator(mapbox_token)
    
    # Generate offers for each restaurant
    for restaurant in restaurants:
        logger.info(f"Generating offers for {restaurant.name}")
        
        # Create merchant directory
        merchant_id = f"toast_{restaurant.name.lower().replace(' ', '_').replace(\"'\", '')}"
        merchant_dir = output_dir / merchant_id
        merchant_dir.mkdir(exist_ok=True)
        (merchant_dir / ".well-known" / "offers").mkdir(parents=True, exist_ok=True)
        
        # Generate lunch and dinner offers
        lunch_offer = generator.generate_offer(restaurant, 'lunch')
        dinner_offer = generator.generate_offer(restaurant, 'dinner')
        
        # Create ACP documents
        lunch_doc = generator.create_acp_offer_document(lunch_offer, restaurant)
        dinner_doc = generator.create_acp_offer_document(dinner_offer, restaurant)
        
        # Save offer documents
        with open(merchant_dir / ".well-known" / "offers" / "ofr_001.json", 'w') as f:
            json.dump(lunch_doc, f, indent=2)
        
        with open(merchant_dir / ".well-known" / "offers" / "ofr_002.json", 'w') as f:
            json.dump(dinner_doc, f, indent=2)
        
        # Create OSF document
        osf_doc = {
            "osf_version": "0.1",
            "publisher": {
                "merchant_id": merchant_id,
                "name": restaurant.name,
                "domain": "localhost:3000"
            },
            "updated_at": "2025-01-15T00:00:00Z",
            "offers": [
                {
                    "href": f"http://localhost:3000/osf/{merchant_id}/.well-known/offers/ofr_001.json",
                    "offer_id": "ofr_001",
                    "updated_at": "2025-01-15T00:00:00Z"
                },
                {
                    "href": f"http://localhost:3000/osf/{merchant_id}/.well-known/offers/ofr_002.json",
                    "offer_id": "ofr_002",
                    "updated_at": "2025-01-15T00:00:00Z"
                }
            ]
        }
        
        with open(merchant_dir / ".well-known" / "osf.json", 'w') as f:
            json.dump(osf_doc, f, indent=2)
        
        logger.info(f"Generated offers for {restaurant.name}:")
        logger.info(f"  Location: {lunch_offer.location['address']}")
        logger.info(f"  Coordinates: {lunch_offer.location['lat']}, {lunch_offer.location['lng']}")
        logger.info(f"  Featured items: {', '.join(lunch_offer.featured_items[:2])}")

if __name__ == "__main__":
    asyncio.run(main())
