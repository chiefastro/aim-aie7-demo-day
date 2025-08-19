import os
import json
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import sys

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from shared.models import (
    CreateOrderRequest, OrderResponse, ConfirmOrderRequest, SettleOrderRequest,
    ValidateOfferRequest, ValidateOfferResponse, MenuResponse, ErrorResponse,
    A2AEnvelope, PresentOfferRequest, PresentOfferResponse,
    InitiateCheckoutRequest, InitiateCheckoutResponse,
    ConfirmOrderRequest as A2AConfirmOrderRequest, ConfirmOrderResponse as A2AConfirmOrderResponse
)
from shared.transaction_logic import MockTransactionLogic

app = FastAPI(
    title="OTTO Portland - Mock Restaurant Server",
    description="Mock web server for OTTO Portland restaurant with A2A endpoints",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize transaction logic
data_dir = os.path.join(os.path.dirname(__file__), "data")
transaction_logic = MockTransactionLogic("otto_portland", data_dir)

# Restaurant info
RESTAURANT_INFO = {
    "name": "OTTO Portland",
    "description": "Italian pizza restaurant serving authentic Neapolitan-style pizzas",
    "address": "431 Central Avenue, Dover, NH 03820",
    "phone": "(603) 555-0123",
    "hours": "11:00 AM - 10:00 PM",
    "website": "http://localhost:8001"
}

@app.get("/")
async def root():
    """Root endpoint with restaurant info"""
    return {
        "restaurant": "OTTO Portland",
        "description": "Italian pizza restaurant",
        "endpoints": {
            "osf": "/.well-known/osf.json",
            "menu": "/a2a/menu",
            "order": "/a2a/order/create",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "restaurant": "OTTO Portland"}

# OSF Endpoints
@app.get("/.well-known/osf.json")
async def get_osf():
    """Get Open Source Food specification"""
    osf_file = os.path.join(data_dir, ".well-known", "osf.json")
    if os.path.exists(osf_file):
        with open(osf_file, 'r') as f:
            osf_data = json.load(f)
            # Update URLs to use this server's port
            osf_data["publisher"]["domain"] = "localhost:8001"
            for offer in osf_data.get("offers", []):
                offer["href"] = offer["href"].replace("localhost:3000", "localhost:8001")
            return osf_data
    else:
        raise HTTPException(status_code=404, detail="OSF file not found")

@app.get("/.well-known/offers/{offer_id}.json")
async def get_offer(offer_id: str):
    """Get individual offer document"""
    offer_file = os.path.join(data_dir, ".well-known", "offers", f"{offer_id}.json")
    if os.path.exists(offer_file):
        with open(offer_file, 'r') as f:
            return json.load(f)
    else:
        raise HTTPException(status_code=404, detail="Offer not found")

# A2A Endpoints
@app.get("/a2a/menu")
async def get_menu():
    """Get restaurant menu"""
    categories = transaction_logic.get_menu()
    return MenuResponse(
        categories=categories,
        restaurant_info=RESTAURANT_INFO
    )

@app.post("/a2a/order/create")
async def create_order(request: CreateOrderRequest):
    """Create a new order"""
    try:
        order = transaction_logic.create_order(request)
        return order
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/a2a/order/{order_id}")
async def get_order(order_id: str):
    """Get order status"""
    order = transaction_logic.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.post("/a2a/order/{order_id}/confirm")
async def confirm_order(order_id: str, request: ConfirmOrderRequest):
    """Confirm an order"""
    order = transaction_logic.confirm_order(order_id, request)
    if not order:
        raise HTTPException(status_code=400, detail="Cannot confirm order")
    return order

@app.post("/a2a/order/{order_id}/settle")
async def settle_order(order_id: str, request: SettleOrderRequest):
    """Settle payment for an order"""
    order = transaction_logic.settle_order(order_id, request)
    if not order:
        raise HTTPException(status_code=400, detail="Cannot settle order")
    return order

@app.post("/a2a/validate-offer")
async def validate_offer(request: ValidateOfferRequest):
    """Validate if an offer can be applied"""
    validation = transaction_logic.validate_offer(
        request.offer_id, request.items, request.order_type
    )
    return validation

# A2A Protocol Endpoints
@app.post("/a2a/present_offer")
async def present_offer(envelope: A2AEnvelope):
    """Present offer details via A2A"""
    try:
        payload = envelope.payload
        offer_id = payload.get("offer_id")
        
        # Get offer details
        offer_file = os.path.join(data_dir, ".well-known", "offers", f"{offer_id}.json")
        if not os.path.exists(offer_file):
            raise HTTPException(status_code=404, detail="Offer not found")
        
        with open(offer_file, 'r') as f:
            offer_data = json.load(f)
        
        # Create response
        response = PresentOfferResponse(
            offer_id=offer_id,
            offer_summary=f"{offer_data.get('title', 'Unknown')} - {offer_data.get('description', 'No description')}",
            constraints=offer_data.get("terms", {}).get("restrictions", []),
            estimated_total=offer_data.get("terms", {}).get("min_spend", 15.0),
            valid_until=datetime.fromisoformat(offer_data.get("expires_at", "2025-02-15T00:00:00Z"))
        )
        
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/a2a/initiate_checkout")
async def initiate_checkout(envelope: A2AEnvelope):
    """Initiate checkout process via A2A"""
    try:
        payload = envelope.payload
        offer_id = payload.get("offer_id")
        items = payload.get("items", [])
        
        # Create order request
        order_request = CreateOrderRequest(
            items=[OrderItem(**item) for item in items],
            offer_id=offer_id,
            customer_name="Demo Customer",
            order_type="dine-in" if not payload.get("pickup", False) else "takeout"
        )
        
        # Create order
        order = transaction_logic.create_order(order_request)
        
        # Create response
        response = InitiateCheckoutResponse(
            order_id=order.order_id,
            status=order.status.value,
            total_amount=order.total,
            payment_instructions={
                "method": "credit_card",
                "amount": order.total,
                "currency": "USD"
            },
            estimated_ready_time=datetime.now() + timedelta(minutes=25)
        )
        
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/a2a/confirm_order")
async def confirm_order(envelope: A2AEnvelope):
    """Confirm order via A2A"""
    try:
        payload = envelope.payload
        order_id = payload.get("order_id")
        
        # Get order
        order = transaction_logic.get_order(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Confirm order
        confirm_request = ConfirmOrderRequest()
        confirmed_order = transaction_logic.confirm_order(order_id, confirm_request)
        
        if not confirmed_order:
            raise HTTPException(status_code=400, detail="Cannot confirm order")
        
        # Create response
        response = A2AConfirmOrderResponse(
            order_id=order_id,
            status=confirmed_order.status.value,
            confirmation_details={
                "order_id": order_id,
                "total": confirmed_order.total,
                "estimated_ready_time": confirmed_order.estimated_ready_time.isoformat() if confirmed_order.estimated_ready_time else None
            },
            receipt_url=f"http://localhost:8001/receipt/{order_id}"
        )
        
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
