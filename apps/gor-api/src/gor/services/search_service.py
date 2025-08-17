import asyncio
import math
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import logging

from gor.services.gor_service import GORService
from gor.models.offer_models import SearchParams

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self, gor_service: GORService):
        self.gor_service = gor_service
    
    async def search_offers(self, search_params: SearchParams) -> Dict[str, Any]:
        """Search offers with hybrid ranking: semantic + geo + time"""
        start_time = time.time()
        
        try:
            # Get base results from GOR
            base_results = await self.gor_service.search_offers(
                search_params.query,
                {
                    "labels": search_params.labels,
                    "limit": search_params.limit * 2,  # Get more for ranking
                    "offset": search_params.offset
                }
            )
            
            if not base_results:
                return {
                    "offers": [],
                    "total": 0,
                    "limit": search_params.limit,
                    "offset": search_params.offset,
                    "search_time": int((time.time() - start_time) * 1000)
                }
            
            # Apply hybrid ranking
            ranked_results = await self.apply_hybrid_ranking(
                base_results, 
                search_params
            )
            
            # Apply pagination
            paginated_results = ranked_results[
                search_params.offset:search_params.offset + search_params.limit
            ]
            
            search_time = int((time.time() - start_time) * 1000)
            logger.info(f"Search completed in {search_time}ms, found {len(ranked_results)} results")
            
            return {
                "offers": paginated_results,
                "total": len(ranked_results),
                "limit": search_params.limit,
                "offset": search_params.offset,
                "search_time": search_time
            }
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return {
                "offers": [],
                "total": 0,
                "limit": search_params.limit,
                "offset": search_params.offset,
                "search_time": int((time.time() - start_time) * 1000),
                "error": str(e)
            }
    
    async def apply_hybrid_ranking(
        self, 
        offers: List[Dict[str, Any]], 
        search_params: SearchParams
    ) -> List[Dict[str, Any]]:
        """Apply hybrid ranking: semantic relevance + geo proximity + time freshness"""
        
        scored_offers = []
        
        for offer in offers:
            # Calculate semantic score (placeholder - would use vector similarity)
            semantic_score = self.calculate_semantic_score(offer, search_params.query)
            
            # Calculate geo score
            geo_score = self.calculate_geo_score(offer, search_params.lat, search_params.lng, search_params.radius_m)
            
            # Calculate time score
            time_score = self.calculate_time_score(offer)
            
            # Combine scores with weights
            combined_score = (
                semantic_score * 0.5 +      # 50% semantic relevance
                geo_score * 0.3 +           # 30% geographic proximity
                time_score * 0.2            # 20% time freshness
            )
            
            scored_offers.append({
                **offer,
                "_scores": {
                    "semantic": semantic_score,
                    "geo": geo_score,
                    "time": time_score,
                    "combined": combined_score
                }
            })
        
        # Sort by combined score (highest first)
        scored_offers.sort(key=lambda x: x["_scores"]["combined"], reverse=True)
        
        # Remove score metadata for final output
        for offer in scored_offers:
            offer.pop("_scores", None)
        
        return scored_offers
    
    def calculate_semantic_score(self, offer: Dict[str, Any], query: str) -> float:
        """Calculate semantic relevance score (0.0 to 1.0)"""
        if not query:
            return 0.5  # Neutral score for no query
        
        query_lower = query.lower()
        offer_text = offer.get("search_text", "").lower()
        
        # Simple text matching score
        score = 0.0
        
        # Exact phrase matches
        if query in offer_text:
            score += 0.4
        
        # Word matches
        query_words = query_lower.split()
        offer_words = offer_text.split()
        
        word_matches = sum(1 for word in query_words if word in offer_words)
        if query_words:
            score += (word_matches / len(query_words)) * 0.3
        
        # Label matches
        offer_labels = [label.lower() for label in offer.get("labels", [])]
        label_matches = sum(1 for word in query_words if word in offer_labels)
        if query_words:
            score += (label_matches / len(query_words)) * 0.2
        
        # Title/description boost
        title = offer.get("title", "").lower()
        description = offer.get("description", "").lower()
        
        if query in title:
            score += 0.1
        if query in description:
            score += 0.05
        
        return min(score, 1.0)
    
    def calculate_geo_score(
        self, 
        offer: Dict[str, Any], 
        lat: Optional[float], 
        lng: Optional[float], 
        radius_m: int
    ) -> float:
        """Calculate geographic proximity score (0.0 to 1.0)"""
        if not lat or not lng:
            return 0.5  # Neutral score for no location
        
        offer_location = offer.get("location", {})
        offer_lat = offer_location.get("lat")
        offer_lng = offer_location.get("lng")
        
        if not offer_lat or not offer_lng:
            return 0.3  # Lower score for offers without location
        
        # Calculate distance using Haversine formula
        distance_km = self.haversine_distance(lat, lng, offer_lat, offer_lng)
        distance_m = distance_km * 1000
        
        # Score based on distance (closer = higher score)
        if distance_m <= radius_m:
            # Within radius: score from 0.8 to 1.0
            score = 1.0 - (distance_m / radius_m) * 0.2
        else:
            # Outside radius: score from 0.0 to 0.8
            score = max(0.0, 0.8 - (distance_m - radius_m) / radius_m * 0.8)
        
        return max(0.0, min(score, 1.0))
    
    def calculate_time_score(self, offer: Dict[str, Any]) -> float:
        """Calculate time freshness score (0.0 to 1.0)"""
        try:
            # Check if offer has expiration
            expires_at = offer.get("expires_at")
            if not expires_at:
                return 0.5  # Neutral score for no expiration
            
            # Parse expiration date
            if isinstance(expires_at, str):
                expiration = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            else:
                expiration = expires_at
            
            now = datetime.now(timezone.utc)
            
            # Calculate days until expiration
            days_until_expiry = (expiration - now).days
            
            if days_until_expiry < 0:
                return 0.0  # Expired
            elif days_until_expiry <= 7:
                return 1.0  # Expires soon - high score
            elif days_until_expiry <= 30:
                return 0.8  # Expires this month
            elif days_until_expiry <= 90:
                return 0.6  # Expires this quarter
            else:
                return 0.4  # Expires later
                
        except Exception as e:
            logger.warning(f"Time score calculation error: {e}")
            return 0.5  # Neutral score on error
    
    def haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula"""
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (
            math.sin(delta_lat / 2) ** 2 +
            math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
