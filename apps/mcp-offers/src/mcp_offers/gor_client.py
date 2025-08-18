"""GOR API client for MCP Offers server"""

import httpx
import logging
from typing import Optional, List, Dict, Any
from .models import (
    SearchOffersInput,
    GetOfferByIdInput,
    NearbyOffersInput,
    SearchResponse,
    OfferResponse,
    Offer,
)

logger = logging.getLogger(__name__)


class GORClient:
    """Client for communicating with the Global Offer Registry API"""
    
    def __init__(self, base_url: str = "http://localhost:3001"):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(timeout=30.0)
    
    def health_check(self) -> bool:
        """Check if GOR API is healthy"""
        try:
            response = self.client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def search_offers(self, params: SearchOffersInput) -> SearchResponse:
        """Search offers using the GOR API"""
        try:
            # Build query parameters
            query_params = {}
            if params.query:
                query_params["query"] = params.query
            if params.lat is not None:
                query_params["lat"] = params.lat
            if params.lng is not None:
                query_params["lng"] = params.lng
            if params.radius_m:
                query_params["radius_m"] = params.radius_m
            if params.labels:
                query_params["labels"] = ",".join(params.labels)
            if params.limit:
                query_params["limit"] = params.limit
            
            response = self.client.get(
                f"{self.base_url}/offers",
                params=query_params
            )
            response.raise_for_status()
            
            data = response.json()
            return SearchResponse(**data)
            
        except httpx.HTTPStatusError as e:
            logger.error(f"GOR API error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"GOR API error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Search offers failed: {e}")
            raise Exception(f"Search offers failed: {e}")
    
    def get_offer_by_id(self, params: GetOfferByIdInput) -> Offer:
        """Get a specific offer by ID"""
        try:
            response = self.client.get(
                f"{self.base_url}/offers/{params.offer_id}"
            )
            response.raise_for_status()
            
            data = response.json()
            offer_response = OfferResponse(**data)
            return offer_response.offer
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise Exception(f"Offer not found: {params.offer_id}")
            logger.error(f"GOR API error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"GOR API error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Get offer by ID failed: {e}")
            raise Exception(f"Get offer by ID failed: {e}")
    
    def get_nearby_offers(self, params: NearbyOffersInput) -> SearchResponse:
        """Get offers near a specific location"""
        try:
            # Build query parameters for nearby search
            query_params = {
                "lat": params.lat,
                "lng": params.lng,
                "radius_m": params.radius_m,
                "limit": params.limit,
                "query": "",  # Empty query for location-only search
            }
            
            response = self.client.get(
                f"{self.base_url}/offers",
                params=query_params
            )
            response.raise_for_status()
            
            data = response.json()
            return SearchResponse(**data)
            
        except httpx.HTTPStatusError as e:
            logger.error(f"GOR API error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"GOR API error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Get nearby offers failed: {e}")
            raise Exception(f"Get nearby offers failed: {e}")
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        try:
            response = self.client.get(f"{self.base_url}/stats")
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Get registry stats failed: {e}")
            raise Exception(f"Get registry stats failed: {e}")
