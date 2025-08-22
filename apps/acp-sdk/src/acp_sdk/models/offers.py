"""Offer Document Models for ACP Protocol

This module defines the standardized models for ACP Offer Documents
that merchants publish to describe their offers and bounties.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


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
    amount: float = Field(..., description="Bounty amount in currency units")
    currency: str = Field("USD", description="Currency code")
    revenue_split: Dict[str, float] = Field(..., description="Revenue split percentages")


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
    id: str = Field(..., description="Unique merchant identifier")
    name: str = Field(..., description="Merchant name")
    location: Optional[MerchantLocation] = None
    phone: Optional[str] = None
    hours: Optional[List[str]] = None


class Offer(BaseModel):
    """ACP Offer Document - the main offer specification"""
    offer_id: str = Field(..., description="Unique offer identifier")
    offer_version: Optional[str] = Field("0.1", description="Offer document version")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[OfferContent] = None
    terms: Optional[OfferTerms] = None
    bounty: Optional[OfferBounty] = None
    merchant: Optional[Merchant] = None
    attribution: Optional[Dict[str, Any]] = None
    provenance: Optional[Dict[str, Any]] = None
    labels: List[str] = Field(default_factory=list, description="Searchable labels")
    search_metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "offer_id": "ofr_001",
                "offer_version": "0.1",
                "title": "Lunch Special",
                "description": "Get 10% off all lunch orders",
                "bounty": {
                    "amount": 2.50,
                    "currency": "USD",
                    "revenue_split": {"user": 0.5, "agent": 0.4, "gor": 0.1}
                },
                "merchant": {
                    "id": "toast_otto_portland",
                    "name": "OTTO Portland",
                    "location": {"city": "Dover", "state": "NH"}
                },
                "labels": ["lunch", "pizza", "italian"]
            }
        }


# Search and API Models
class SearchParams(BaseModel):
    """Search parameters for offer queries"""
    query: str = Field("", description="Search query text")
    lat: Optional[float] = Field(None, description="Latitude for geo search")
    lng: Optional[float] = Field(None, description="Longitude for geo search")
    radius_m: int = Field(50000, description="Search radius in meters")
    labels: List[str] = Field(default_factory=list, description="Labels to filter by")
    limit: int = Field(20, description="Maximum number of results")
    offset: int = Field(0, description="Number of results to skip")


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
