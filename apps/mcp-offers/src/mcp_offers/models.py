"""Data models for MCP Offers server"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SearchParams(BaseModel):
    """Search parameters for offer queries"""
    query: str = Field("", description="Search query text")
    lat: Optional[float] = Field(None, description="Latitude for geo search")
    lng: Optional[float] = Field(None, description="Longitude for geo search")
    radius_m: int = Field(50000, description="Search radius in meters")
    labels: List[str] = Field(default_factory=list, description="Labels to filter by")
    limit: int = Field(20, description="Maximum number of results")
    offset: int = Field(0, description="Number of results to skip")


class OfferContent(BaseModel):
    """Offer content details"""
    restaurant_description: Optional[str] = None
    featured_items: Optional[List[str]] = None
    cuisine_type: Optional[str] = None
    price_range: Optional[str] = None
    dietary_options: Optional[List[str]] = None


class OfferTerms(BaseModel):
    """Offer terms and conditions"""
    min_spend: Optional[float] = None
    max_discount: Optional[float] = None
    valid_days: Optional[List[str]] = None
    valid_hours: Optional[Dict[str, str]] = None
    restrictions: Optional[List[str]] = None


class OfferBounty(BaseModel):
    """Bounty and revenue split information"""
    amount: float
    currency: str = "USD"
    revenue_split: Dict[str, int]


class MerchantLocation(BaseModel):
    """Merchant location information"""
    lat: Optional[float] = None
    lng: Optional[float] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None


class Merchant(BaseModel):
    """Merchant information"""
    id: str
    name: str
    location: Optional[MerchantLocation] = None
    phone: Optional[str] = None
    hours: Optional[List[str]] = None


class Offer(BaseModel):
    """ACP Offer Document"""
    offer_id: str
    offer_version: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    expires_at: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[OfferContent] = None
    terms: Optional[OfferTerms] = None
    bounty: Optional[OfferBounty] = None
    merchant: Optional[Merchant] = None
    attribution: Optional[Dict[str, Any]] = None
    provenance: Optional[Dict[str, Any]] = None
    labels: List[str] = Field(default_factory=list)
    search_metadata: Optional[Dict[str, Any]] = None


class SearchResults(BaseModel):
    """Search results container"""
    offers: List[Offer]
    total: int
    limit: int
    offset: int


class SearchResponse(BaseModel):
    """API response for search queries"""
    success: bool
    query: SearchParams
    results: SearchResults
    metadata: Dict[str, Any]


class OfferResponse(BaseModel):
    """API response for single offer"""
    success: bool
    offer: Offer


# MCP Tool Input/Output Models
class SearchOffersInput(BaseModel):
    """Input for offers.search tool"""
    query: Optional[str] = Field(None, description="Search query text")
    lat: Optional[float] = Field(None, description="Latitude for geo search")
    lng: Optional[float] = Field(None, description="Longitude for geo search")
    radius_m: Optional[int] = Field(50000, description="Search radius in meters")
    labels: Optional[List[str]] = Field(None, description="Labels to filter by")
    limit: Optional[int] = Field(20, description="Maximum number of results")


class GetOfferByIdInput(BaseModel):
    """Input for offers.getById tool"""
    offer_id: str = Field(..., description="Offer ID to retrieve")


class NearbyOffersInput(BaseModel):
    """Input for offers.nearby tool"""
    lat: float = Field(..., description="Latitude for geo search")
    lng: float = Field(..., description="Longitude for geo search")
    radius_m: Optional[int] = Field(50000, description="Search radius in meters")
    limit: Optional[int] = Field(20, description="Maximum number of results")
