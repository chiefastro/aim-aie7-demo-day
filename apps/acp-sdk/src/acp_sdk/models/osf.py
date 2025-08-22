"""OSF (Offer Syndication Feed) Models for ACP Protocol

This module defines the standardized models for Offer Syndication Feeds
that merchants publish to make their offers discoverable.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class OSFOffer(BaseModel):
    """Individual offer reference within an OSF"""
    href: str = Field(..., description="URL to the offer document")
    offer_id: str = Field(..., description="Unique offer identifier")
    updated_at: datetime = Field(..., description="Last update timestamp")


class OSFPublisher(BaseModel):
    """Publisher information for the OSF"""
    merchant_id: str = Field(..., description="Unique merchant identifier")
    name: str = Field(..., description="Merchant name")
    domain: str = Field(..., description="Merchant domain")


class OSFFeed(BaseModel):
    """Offer Syndication Feed (OSF) - the main feed document"""
    osf_version: str = Field("0.1", description="OSF protocol version")
    publisher: OSFPublisher = Field(..., description="Publisher information")
    updated_at: datetime = Field(..., description="Last feed update timestamp")
    offers: List[OSFOffer] = Field(default_factory=list, description="List of available offers")
    
    class Config:
        json_schema_extra = {
            "example": {
                "osf_version": "0.1",
                "publisher": {
                    "merchant_id": "toast_otto_portland",
                    "name": "OTTO Portland",
                    "domain": "order.ottoportland.com"
                },
                "updated_at": "2025-01-13T12:00:00Z",
                "offers": [
                    {
                        "href": "https://order.ottoportland.com/.well-known/offers/ofr_001.json",
                        "offer_id": "ofr_001",
                        "updated_at": "2025-01-13T12:00:00Z"
                    }
                ]
            }
        }
