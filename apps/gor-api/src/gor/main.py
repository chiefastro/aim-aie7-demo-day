from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import uvicorn
from datetime import datetime
import logging

from acp_sdk.discovery.registry import OfferRegistry
from acp_sdk.models.offers import (
    SearchParams, SearchResults, SearchResponse, OfferResponse, Offer,
    SearchOffersInput, GetOfferByIdInput, NearbyOffersInput
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Global Offer Registry API",
    description="ACP Demo - Global Offer Registry for restaurant offers",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
gor_service = OfferRegistry()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        await gor_service.ensure_collection()
        logger.info("✅ GOR service initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize GOR service: {e}")
        raise

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Global Offer Registry API",
        "version": "1.0.0"
    }

@app.get("/offers", response_model=SearchResponse)
async def search_offers(
    query: str = Query("", description="Search query text"),
    lat: Optional[float] = Query(None, description="Latitude for geo search"),
    lng: Optional[float] = Query(None, description="Longitude for geo search"),
    radius_m: int = Query(50000, description="Search radius in meters"),
    labels: Optional[str] = Query(None, description="Comma-separated labels to filter by"),
    limit: int = Query(20, description="Maximum number of results"),
    offset: int = Query(0, description="Number of results to skip")
):
    """Search offers with hybrid semantic + geo + time ranking"""
    try:
        # Parse labels
        label_list = []
        if labels:
            label_list = [label.strip() for label in labels.split(",") if label.strip()]
        
        # Create SearchParams
        search_params = SearchParams(
            query=query.strip(),
            lat=lat,
            lng=lng,
            radius_m=radius_m,
            labels=label_list,
            limit=limit,
            offset=offset
        )
        
        # Get raw results from registry
        raw_results = await gor_service.search_offers(query.strip(), {
            "lat": lat,
            "lng": lng,
            "radius_m": radius_m,
            "labels": label_list,
            "limit": limit,
            "offset": offset
        })
        
        # Convert raw results to Offer models
        offers = []
        for raw_offer in raw_results:
            try:
                # Convert raw offer data to Offer model
                offer = Offer(
                    offer_id=raw_offer.get("offer_id"),
                    title=raw_offer.get("title"),
                    description=raw_offer.get("description"),
                    content=raw_offer.get("content"),
                    terms=raw_offer.get("terms"),
                    bounty=raw_offer.get("bounty"),
                    merchant=raw_offer.get("merchant"),
                    labels=raw_offer.get("labels", []),
                    created_at=raw_offer.get("created_at"),
                    updated_at=raw_offer.get("updated_at"),
                    expires_at=raw_offer.get("expires_at")
                )
                offers.append(offer)
            except Exception as e:
                logger.warning(f"Failed to parse offer {raw_offer.get('offer_id')}: {e}")
                continue
        
        # Create SearchResults
        search_results = SearchResults(
            offers=offers,
            total=len(offers),
            limit=limit,
            offset=offset
        )
        
        # Return proper SearchResponse
        return SearchResponse(
            success=True,
            query=search_params,
            results=search_results,
            metadata={
                "search_time_ms": 0,
                "ranking_method": "hybrid_semantic_geo_time"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/offers/{offer_id}", response_model=OfferResponse)
async def get_offer(offer_id: str):
    """Get offer by ID"""
    try:
        print(f"DEBUG: GOR API called with offer_id: {offer_id}")
        print(f"DEBUG: gor_service type: {type(gor_service)}")
        
        raw_offer = await gor_service.get_offer_by_id(offer_id)
        
        print(f"DEBUG: raw_offer result: {raw_offer}")
        
        if not raw_offer:
            raise HTTPException(status_code=404, detail="Offer not found")
        
        # Convert raw offer data to Offer model
        offer = Offer(
            offer_id=raw_offer.get("offer_id"),
            title=raw_offer.get("title"),
            description=raw_offer.get("description"),
            content=raw_offer.get("content"),
            terms=raw_offer.get("terms"),
            bounty=raw_offer.get("bounty"),
            merchant=raw_offer.get("merchant"),
            labels=raw_offer.get("labels", []),
            created_at=raw_offer.get("created_at"),
            updated_at=raw_offer.get("updated_at"),
            expires_at=raw_offer.get("expires_at")
        )
        
        return OfferResponse(
            success=True,
            offer=offer
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/merchants/{merchant_id}/offers")
async def get_merchant_offers(merchant_id: str):
    """Get all offers for a specific merchant"""
    try:
        offers = await gor_service.get_offers_by_merchant(merchant_id)
        
        return {
            "success": True,
            "merchant_id": merchant_id,
            "offers": offers,
            "total": len(offers)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_registry_stats():
    """Get registry statistics"""
    try:
        stats = await gor_service.get_registry_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest")
async def ingest_offers():
    """Trigger offer ingestion from demo server"""
    try:
        result = await gor_service.ingest_offers()
        return {
            "success": True,
            "message": "Ingestion completed",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "gor.main:app",
        host="0.0.0.0",
        port=3001,
        reload=True,
        log_level="info"
    )
