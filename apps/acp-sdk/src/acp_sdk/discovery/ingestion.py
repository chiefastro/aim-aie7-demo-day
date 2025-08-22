"""OSF Ingestion Service for ACP Protocol

This module provides services for ingesting and processing
Offer Syndication Feeds (OSF) from merchants.
"""

import asyncio
import aiohttp
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..models.osf import OSFFeed, OSFOffer
from ..models.offers import Offer

logger = logging.getLogger(__name__)


class OSFIngestionService:
    """Service for ingesting OSF feeds and offers"""
    
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def get_merchants(self) -> List[Dict[str, Any]]:
        """Get list of available merchants from demo server"""
        try:
            if not self.session:
                raise RuntimeError("Session not initialized. Use async context manager.")
            
            async with self.session.get(f"{self.base_url}/merchants") as response:
                response.raise_for_status()
                data = await response.json()
                merchants = data.get("merchants", [])
                logger.info(f"📋 Found {len(merchants)} merchants")
                return merchants
                
        except Exception as e:
            logger.error(f"❌ Failed to get merchants: {e}")
            return []
    
    async def get_osf_feed(self, merchant_id: str, osf_url: str) -> Optional[OSFFeed]:
        """Get OSF feed for a specific merchant"""
        try:
            if not self.session:
                raise RuntimeError("Session not initialized. Use async context manager.")
            
            # Fix URL if it's using localhost
            if "localhost:3000" in osf_url:
                osf_url = osf_url.replace("localhost:3000", self.base_url.replace("http://", ""))
            
            async with self.session.get(osf_url) as response:
                response.raise_for_status()
                osf_data = await response.json()
                
                # Parse OSF feed
                osf_feed = OSFFeed(**osf_data)
                logger.info(f"📄 Retrieved OSF feed for {merchant_id}: {len(osf_feed.offers)} offers")
                return osf_feed
                
        except Exception as e:
            logger.error(f"❌ Failed to get OSF feed for {merchant_id}: {e}")
            return None
    
    async def get_offer_document(self, offer_ref: OSFOffer) -> Optional[Offer]:
        """Get individual offer document from OSF reference"""
        try:
            if not self.session:
                raise RuntimeError("Session not initialized. Use async context manager.")
            
            # Fix URL if it's using localhost
            offer_url = offer_ref.href
            if "localhost:3000" in offer_url:
                offer_url = offer_url.replace("localhost:3000", self.base_url.replace("http://", ""))
            
            async with self.session.get(offer_url) as response:
                response.raise_for_status()
                offer_data = await response.json()
                
                # Parse offer document
                offer = Offer(**offer_data)
                logger.debug(f"📄 Retrieved offer document: {offer.offer_id}")
                return offer
                
        except Exception as e:
            logger.error(f"❌ Failed to get offer document {offer_ref.offer_id}: {e}")
            return None
    
    async def ingest_merchant_offers(self, merchant_id: str, osf_url: str) -> List[Offer]:
        """Ingest all offers for a specific merchant"""
        try:
            # Get OSF feed
            osf_feed = await self.get_osf_feed(merchant_id, osf_url)
            if not osf_feed:
                return []
            
            # Get all offer documents
            offers = []
            for offer_ref in osf_feed.offers:
                offer = await self.get_offer_document(offer_ref)
                if offer:
                    offers.append(offer)
            
            logger.info(f"🍕 Ingested {len(offers)} offers for {merchant_id}")
            return offers
            
        except Exception as e:
            logger.error(f"❌ Failed to ingest offers for {merchant_id}: {e}")
            return []
    
    async def ingest_all_merchants(self) -> Dict[str, List[Offer]]:
        """Ingest offers from all available merchants"""
        try:
            # Get all merchants
            merchants = await self.get_merchants()
            if not merchants:
                logger.warning("⚠️ No merchants found")
                return {}
            
            # Ingest offers for each merchant
            all_offers = {}
            total_offers = 0
            
            for merchant in merchants:
                merchant_id = merchant["id"]
                osf_url = merchant["osf_url"]
                
                logger.info(f"🔄 Ingesting offers for {merchant_id}...")
                offers = await self.ingest_merchant_offers(merchant_id, osf_url)
                
                if offers:
                    all_offers[merchant_id] = offers
                    total_offers += len(offers)
                
                # Small delay to avoid overwhelming the server
                await asyncio.sleep(0.1)
            
            logger.info(f"🎉 Completed ingestion: {total_offers} total offers from {len(all_offers)} merchants")
            return all_offers
            
        except Exception as e:
            logger.error(f"❌ Failed to ingest all merchants: {e}")
            return {}
    
    async def validate_osf_feed(self, osf_data: Dict[str, Any]) -> bool:
        """Validate OSF feed structure"""
        try:
            # Basic validation
            required_fields = ["osf_version", "publisher", "updated_at", "offers"]
            for field in required_fields:
                if field not in osf_data:
                    logger.error(f"❌ Missing required field: {field}")
                    return False
            
            # Validate publisher
            publisher = osf_data.get("publisher", {})
            if not all(field in publisher for field in ["merchant_id", "name", "domain"]):
                logger.error("❌ Invalid publisher structure")
                return False
            
            # Validate offers array
            offers = osf_data.get("offers", [])
            if not isinstance(offers, list):
                logger.error("❌ Offers must be an array")
                return False
            
            for offer in offers:
                if not all(field in offer for field in ["href", "offer_id", "updated_at"]):
                    logger.error(f"❌ Invalid offer structure: {offer}")
                    return False
            
            logger.info("✅ OSF feed validation passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ OSF validation failed: {e}")
            return False
    
    async def get_ingestion_stats(self) -> Dict[str, Any]:
        """Get ingestion statistics"""
        try:
            merchants = await self.get_merchants()
            
            stats = {
                "total_merchants": len(merchants),
                "merchants": [],
                "total_offers": 0,
                "last_updated": datetime.utcnow().isoformat()
            }
            
            for merchant in merchants:
                merchant_id = merchant["id"]
                osf_url = merchant["osf_url"]
                
                # Get OSF feed for stats
                osf_feed = await self.get_osf_feed(merchant_id, osf_url)
                if osf_feed:
                    offer_count = len(osf_feed.offers)
                    stats["total_offers"] += offer_count
                    stats["merchants"].append({
                        "id": merchant_id,
                        "name": merchant.get("name", "Unknown"),
                        "offers": offer_count,
                        "last_updated": osf_feed.updated_at.isoformat() if osf_feed.updated_at else None
                    })
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to get ingestion stats: {e}")
            return {"error": str(e)}
