"""Global Offer Registry (GOR) for ACP Protocol

This module provides the core offer registry functionality including:
- Offer ingestion and indexing
- Vector search capabilities
- Registry statistics and management
"""

import asyncio
import aiohttp
import json
import os
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue, MatchAny
import logging

from ..models.offers import Offer, SearchParams, SearchResults, SearchResponse
from .vector_search import VectorSearchService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OfferRegistry:
    """Global Offer Registry for ACP offers"""
    
    def __init__(self):
        # Get configuration from environment variables
        qdrant_host = os.getenv("QDRANT_HOST", "localhost")
        qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
        demo_server_url = os.getenv("DEMO_SERVER_URL", "http://localhost:3000")
        
        self.qdrant = QdrantClient(qdrant_host, port=qdrant_port)
        self.vector_search = VectorSearchService()
        self.collection_name = "acp_offers"
        self.demo_server_url = demo_server_url
        
        # Don't initialize collection here - will be done when needed
    
    async def ensure_collection(self):
        """Ensure the Qdrant collection exists"""
        try:
            collections = self.qdrant.get_collections()
            exists = any(c.name == self.collection_name for c in collections.collections)
            
            if not exists:
                # Create collection for OpenAI embeddings
                self.qdrant.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=1536,  # OpenAI text-embedding-ada-002 dimension
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"📚 Created collection: {self.collection_name}")
            else:
                logger.info(f"✅ Collection {self.collection_name} already exists")
        except Exception as e:
            logger.error(f"❌ Collection creation error: {e}")
            raise
    
    async def ingest_offers(self) -> Dict[str, int]:
        """Ingest offers from the demo server"""
        try:
            logger.info("🔄 Starting offer ingestion...")
            
            async with aiohttp.ClientSession() as session:
                # Get merchants from demo server
                async with session.get(f"{self.demo_server_url}/merchants") as response:
                    merchants_data = await response.json()
                    merchants = merchants_data.get("merchants", [])
                
                logger.info(f"📋 Found {len(merchants)} merchants to ingest")
                
                total_offers = 0
                ingested_offers = 0
                
                for merchant in merchants:
                    try:
                        logger.info(f"🍕 Ingesting offers for {merchant['id']}...")
                        
                        # Fix the OSF URL to use the container's demo server URL
                        osf_url = merchant['osf_url'].replace('http://localhost:3000', self.demo_server_url)
                        
                        # Get OSF for merchant
                        async with session.get(osf_url) as response:
                            osf = await response.json()
                        
                        # Get individual offers
                        for offer_ref in osf.get("offers", []):
                            try:
                                # Fix the offer URL to use the container's demo server URL
                                offer_url = offer_ref['href'].replace('http://localhost:3000', self.demo_server_url)
                                async with session.get(offer_url) as response:
                                    offer = await response.json()
                                
                                # Normalize and index offer
                                await self.index_offer(offer)
                                ingested_offers += 1
                                
                                logger.info(f"  ✅ Indexed {offer['offer_id']}")
                            except Exception as offer_error:
                                logger.error(f"  ❌ Failed to ingest offer {offer_ref.get('offer_id', 'unknown')}: {offer_error}")
                        
                        total_offers += len(osf.get("offers", []))
                    except Exception as merchant_error:
                        logger.error(f"❌ Failed to ingest merchant {merchant['id']}: {merchant_error}")
                
                logger.info(f"🎉 Ingestion complete: {ingested_offers}/{total_offers} offers indexed")
                return {"total": total_offers, "ingested": ingested_offers}
                
        except Exception as e:
            logger.error(f"❌ Ingestion failed: {e}")
            raise
    
    async def index_offer(self, offer: Dict[str, Any]) -> bool:
        """Index an offer in the vector database"""
        try:
            # Generate embedding for search text
            search_text = self.generate_search_text(offer)
            embedding = await self.vector_search.get_embedding(search_text)
            
            # Create unique point ID by combining offer_id and merchant info
            offer_id = offer.get("offer_id", "")
            merchant_id = offer.get("merchant", {}).get("id", "unknown")
            merchant_name = offer.get("merchant", {}).get("name", "Unknown")
            
            # Create a unique identifier that combines offer_id and merchant info
            unique_id = f"{merchant_id}_{offer_id}"
            point_id = hash(unique_id) & 0x7fffffff  # Convert to positive 32-bit integer
            
            # Prepare payload for Qdrant
            payload = {
                "offer_id": offer_id,
                "merchant_id": merchant_id,
                "merchant_name": merchant_name,
                "title": offer.get("title", ""),
                "description": offer.get("description", ""),
                "content": offer.get("content", {}),
                "terms": offer.get("terms", {}),
                "bounty": offer.get("bounty", {}),
                "labels": offer.get("labels", []),
                "location": offer.get("merchant", {}).get("location", {}),
                "search_text": search_text,
                "created_at": offer.get("created_at", ""),
                "updated_at": offer.get("updated_at", ""),
                "expires_at": offer.get("expires_at"),
                "unique_id": unique_id  # Store the unique identifier for debugging
            }
            
            # Upsert to Qdrant
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload=payload
            )
            
            self.qdrant.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            return True
        except Exception as e:
            logger.error(f"Indexing error for {offer.get('offer_id', 'unknown')}: {e}")
            raise
    
    def generate_search_text(self, offer: Dict[str, Any]) -> str:
        """Generate searchable text from offer data"""
        parts = [
            # Primary content - cuisine and food
            offer.get("content", {}).get("cuisine_type", ""),
            offer.get("content", {}).get("restaurant_description", ""),
            " ".join(offer.get("content", {}).get("featured_items", [])),
            
            # Restaurant name and type
            offer.get("merchant", {}).get("name", ""),
            
            # Labels (cuisine-specific)
            " ".join([label for label in offer.get("labels", []) 
                     if label not in ["lunch", "dinner", "midday", "evening", "dine-in", "takeout", "dover-nh", "new-hampshire", "seacoast"]]),
            
            # Title and description (less weight)
            offer.get("title", ""),
            offer.get("description", ""),
            
            # Location (minimal weight)
            offer.get("merchant", {}).get("location", {}).get("city", ""),
            offer.get("merchant", {}).get("location", {}).get("state", "")
        ]
        
        return " ".join(filter(bool, parts)).lower()
    
    async def get_offer_by_id(self, offer_id: str) -> Optional[Dict[str, Any]]:
        """Get offer by ID - supports both simple offer_id and full unique_id"""
        print(f"DEBUG: Registry get_offer_by_id called with: {offer_id}")
        try:
            # First try to find by unique_id (merchant_id_offer_id format)
            if "_" in offer_id:
                # This is already a unique_id
                unique_id = offer_id
                point_id = hash(unique_id) & 0x7fffffff
                
                result = self.qdrant.retrieve(
                    collection_name=self.collection_name,
                    ids=[point_id]
                )
                
                if result:
                    return result[0].payload
            
            # If not found or no underscore, search by offer_id in payload
            print(f"DEBUG: About to call Qdrant scroll for offer_id: {offer_id}")
            result = self.qdrant.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="offer_id",
                            match=MatchValue(value=offer_id)
                        )
                    ]
                ),
                limit=1
            )
            
            # Debug: Print to stdout since logging might not be working
            print(f"DEBUG: Scroll result type: {type(result)}")
            print(f"DEBUG: Scroll result for offer_id {offer_id}: {result}")
            
            # Handle Qdrant scroll response structure: (points, next_page_offset)
            if result and len(result) > 0 and result[0] and len(result[0]) > 0:
                print(f"DEBUG: Found offer payload: {result[0][0].payload}")
                return result[0][0].payload
            
            print(f"DEBUG: No offer found for offer_id: {offer_id}")
            return None
        except Exception as e:
            logger.error(f"Get offer error: {e}")
            return None
    
    async def get_offers_by_merchant(self, merchant_id: str) -> List[Dict[str, Any]]:
        """Get all offers for a specific merchant"""
        try:
            result = self.qdrant.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="merchant_id",
                            match=MatchValue(value=merchant_id)
                        )
                    ]
                ),
                limit=100
            )
            
            return [point.payload for point in result[0]]
        except Exception as e:
            logger.error(f"Get merchant offers error: {e}")
            return []
    
    async def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        try:
            collection_info = self.qdrant.get_collection(self.collection_name)
            
            return {
                "total_offers": collection_info.points_count,
                "collection_name": self.collection_name,
                "vector_size": collection_info.config.params.vectors.size,
                "distance_metric": collection_info.config.params.vectors.distance.value,
                "last_updated": collection_info.config.params.vectors.on_disk
            }
        except Exception as e:
            logger.error(f"Stats error: {e}")
            return {"error": str(e)}
    
    async def search_offers(self, query: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search offers with vector similarity and filters"""
        try:
            filter_conditions = []
            
            if filters and filters.get("merchant_id"):
                filter_conditions.append(
                    FieldCondition(
                        key="merchant_id",
                        match=MatchValue(value=filters["merchant_id"])
                    )
                )
            
            if filters and filters.get("labels") and len(filters["labels"]) > 0:
                filter_conditions.append(
                    FieldCondition(
                        key="labels",
                        match=MatchAny(any=filters["labels"])
                    )
                )
            
            scroll_filter = Filter(must=filter_conditions) if filter_conditions else None
            
            if query and query.strip():
                # Use vector similarity search for semantic queries
                search_text = query.strip().lower()
                query_embedding = await self.vector_search.get_embedding(search_text)
                
                # Search with vector similarity
                result = self.qdrant.search(
                    collection_name=self.collection_name,
                    query_vector=query_embedding,
                    query_filter=scroll_filter,
                    limit=filters.get("limit", 20) if filters else 20,
                    offset=filters.get("offset", 0) if filters else 0,
                    with_payload=True,
                    score_threshold=0.75  # High threshold for semantic similarity
                )
                
                # Log similarity scores for debugging
                if result:
                    logger.info(f"Vector search results for '{query}':")
                    for i, point in enumerate(result[:3]):  # Log top 3 results
                        logger.info(f"  {i+1}. Score: {point.score:.3f}, Offer: {point.payload.get('offer_id', 'unknown')}")
                
                # Return offers sorted by similarity score
                return [point.payload for point in result]
            else:
                # No query - just return filtered results without ranking
                result = self.qdrant.scroll(
                    collection_name=self.collection_name,
                    scroll_filter=scroll_filter,
                    limit=filters.get("limit", 20) if filters else 20,
                    offset=filters.get("offset", 0) if filters else 0
                )
                
                return [point.payload for point in result[0]]
                
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
