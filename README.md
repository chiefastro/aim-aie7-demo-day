# Agentic Commerce Protocol (ACP) Demo

This repository contains a working prototype of the Agentic Commerce Protocol (ACP) for restaurants, demonstrating how AI agents can discover and interact with merchant offers.

## What We've Built So Far

### ✅ Day 1 Complete: ACP OSF and Offer Document Generation

1. **Restaurant Scraper** (`apps/offer-scraper/`)
   - ✅ **Successfully scrapes real restaurant data from Toast URLs**
   - ✅ **Extracts real merchant info, menu items, location, and hours**
   - ✅ **Handles Cloudflare protection with improved stealth techniques**
   - ✅ **Organizes menu into proper categories (Pizza, Salads, Drinks, etc.)**
   - ✅ **Deduplicates menu items and cleans data**

2. **ACP Document Generator**
   - ✅ **Converts real scraped restaurant data into ACP Offer Documents**
   - ✅ **Generates OSF (Offer Syndication Feed) endpoints**
   - ✅ **Creates proper `.well-known/osf.json` structure**

3. **Demo HTTP Server**
   - ✅ **Serves ACP documents at `http://localhost:3000`**
   - ✅ **Provides REST API endpoints for OSF and offer discovery**
   - ✅ **Includes CORS support for cross-origin access**

### 📁 Generated ACP Structure

```
data/osf/toast_otto_portland/
├── .well-known/
│   ├── osf.json                    # Offer Syndication Feed
│   └── offers/
│       ├── ofr_001.json           # ACP Offer Document
│       └── ofr_002.json           # ACP Offer Document
```

### 🌐 Live Demo Endpoints

- **Demo Info**: http://localhost:3000/demo
- **Available Merchants**: http://localhost:3000/merchants
- **OSF Examples**:
  - OTTO Portland: http://localhost:3000/osf/toast_otto_portland/.well-known/osf.json
  - Street Exeter: http://localhost:3000/osf/toast_street_exeter_8_clifford_street/.well-known/osf.json
  - Newick's Lobster: http://localhost:3000/osf/toast_newick's_lobster_house/.well-known/osf.json
- **Offer Examples**:
  - OTTO Portland: http://localhost:3000/osf/toast_otto_portland/.well-known/offers/ofr_001.json
  - Street Exeter: http://localhost:3000/osf/toast_street_exeter_8_clifford_street/.well-known/offers/ofr_001.json
  - Newick's Lobster: http://localhost:3000/osf/toast_newick's_lobster_house/.well-known/offers/ofr_001.json

## Real Restaurant Data Successfully Scraped

### 🍕 **OTTO Portland - Dover, NH** (Pizza/Italian)
- **URL**: https://www.toasttab.com/local/order/otto-portland-dover-nh
- **Address**: 431 Central Avenue, Dover, NH 03820
- **Hours**: 11:00 am - 10:00 pm daily
- **Real Menu Categories**:
  - **Pizza**: Cheese Pizza ($13.00), OTTO Four Cheese ($16.50), Margherita ($16.50)
  - **Salads**: House Salad ($7.25), Caesar ($8.25), Cobb ($10.25), Pesto Mozzarella ($11.75)
  - **Appetizers & Sides**: Meatball Sub ($13.00), Garlic Sticks ($9.00), Stuffed Mushrooms ($11.50)
  - **Drinks**: Coke ($2.95), Smart Water ($3.00), Sprite ($2.95)
  - **Desserts**: Chocolate Cookies ($8.00), Cheesecake ($12.00), Tiramisu ($8.50)
- **ACP Labels**: pizza, italian, salad, dine-in, takeout

### 🍔 **Street Exeter - Exeter, NH** (American/Comfort Food)
- **URL**: https://www.toasttab.com/local/order/street-exeter-8-clifford-street-cmaxy
- **Address**: 8 Clifford Street, Exeter, NH
- **Real Menu Items**:
  - **Featured Items**: Korean BBQ Beef Bibimbap ($23.00), Chicken Cemita ($17.00)
  - **Fries**: Curry Fries ($13.00), Subarashi Fries ($13.00), Reg Fries ($5.20)
  - **Tenders**: Korean Tenders ($14.00), Southern Tenders ($14.00)
  - **Tacos**: Fish Taco ($8.00), Shrimp Con Pow! ($17.00)
- **ACP Labels**: american, comfort-food, salad, burger, mexican, indian, asian

### 🦞 **Newick's Lobster House - Dover, NH** (Seafood)
- **URL**: https://www.toasttab.com/local/order/newicks-lobster-house-dover-431-dover-point-rd
- **Address**: 431 Dover Point Rd, Dover, NH
- **Real Menu Items**:
  - **Beverages**: Coffee ($3.00), Coke ($3.50), Hot Chocolate ($3.50)
  - **Seafood**: Lobster dishes, Fish entrees, Clam chowder
  - **Sides**: Fries, Coleslaw, Onion rings
- **ACP Labels**: seafood, lobster, fish, pizza, salad, burger, mexican, lunch, dinner

### 🎯 **ACP Offers Generated**
- **All Restaurants**: $2.50 bounty with 50/40/10 revenue split
- **Cuisine-Specific Labels**: Automatically generated based on restaurant type
- **Eligibility**: US-NH residents
- **Schedule**: Daily 11:00 AM - 10:00 PM

## Quick Start

### 🐳 Docker (Recommended)

The easiest way to run the complete ACP demo stack:

```bash
# Quick start - builds and runs everything
make start

# Or step by step:
make build          # Build all Docker images
make up             # Start core services (GOR + MCP + Qdrant)
make cli            # Run interactive consumer agent CLI

# View all available commands:
make help
```

**Available Docker Commands:**
- `make start` - Quick start (build + run core stack)
- `make demo` - Complete demo with all services
- `make workflow` - Full demo workflow
- `make status` - Check service status
- `make health` - Check service health
- `make logs` - View service logs
- `make clean` - Clean up everything

### 🔧 Manual Setup

If you prefer to run services manually:

#### 1. Scrape Restaurant Data

```bash
# Install dependencies
cd apps/offer-scraper
npm install

# Scrape all restaurants from config (recommended)
npm run batch-scrape

# Or scrape a single restaurant
npm run scrape

# Generate ACP documents from scraped data
npm run generate

# Start demo server
npm run server
```

#### 2. Start Global Offer Registry

```bash
# In a new terminal
cd apps/gor-api
uv sync
uv run python -m gor.main
```

#### 3. Start MCP Offers Server

```bash
# In a new terminal
cd apps/mcp-offers
uv sync
uv run python -m mcp_offers
```



### Configuration

**Simple Text File (Recommended)**
Edit `config/restaurants.txt` with one URL per line:

```txt
# Restaurant URLs - one per line
# Lines starting with # are comments

https://www.toasttab.com/local/order/otto-portland-dover-nh
https://www.toasttab.com/local/order/street-exeter-8-clifford-street-cmaxy
https://www.toasttab.com/local/order/newicks-lobster-house-dover-431-dover-point-rd
```

**Add URLs via CLI**
```bash
npm run add-url https://www.toasttab.com/local/order/restaurant-url
```



**Auto-Detection Features:**
- Restaurant names extracted from scraped data
- Cuisine types automatically detected from menu items
- IDs generated from URLs
- Location data extracted from restaurant pages

## Next Steps (Days 2-7)

### Day 2: Global Offer Registry (GOR) ✅
- [x] Set up Qdrant vector database
- [x] Implement offer ingestion and indexing
- [x] Create hybrid search with geo/time scoring
- [x] Build GOR HTTP API

### Day 3: MCP Server ✅
- [x] **MCP Offers Server**: Wraps GOR API with standardized MCP tools
- [x] **Semantic Search Tools**: `offers.search`, `offers.getById`, `offers.nearby`
- [x] **GOR Integration**: Direct connection to Global Offer Registry


### Day 4: Restaurant Agents
- [ ] Implement A2A endpoints for restaurant agents
- [ ] Create order state machine (CREATED → CONFIRMED → SETTLED)
- [ ] Build 3 restaurant agent instances

### Day 5: Transaction Simulator
- [ ] Implement Attribution Receipt generation
- [ ] Create Settlement Postback handling
- [ ] Build wallet/ledger system

### Day 6: End-to-End Integration
- [ ] Wire all components together
- [ ] Test complete flow: discover → present → initiate → confirm → receipt
- [ ] Add demo UI/CLI polish

### Day 7: Hardening & Documentation
- [ ] Error handling and edge cases
- [ ] Documentation and schema validation
- [ ] Demo video recording

## Architecture Overview

```
Consumer Agent (MCP) → GOR (Search) → Restaurant Agents (A2A) → Transaction Simulator
       ↓                      ↓                    ↓                    ↓
   MCP Tools           Vector Search         Order Flow          Wallet/Ledger
```

### 🐳 Docker Architecture

The ACP demo uses Docker containers for easy deployment and consistency:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ACP Demo Stack                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  Port 3000    Port 3001    Port 3002    Port 6333                        │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐                      │
│  │Offer    │  │GOR API  │  │MCP      │  │Qdrant   │                      │
│  │Scraper  │  │(Search) │  │Server   │  │(Vector  │                      │
│  │(ACP     │  │         │  │(Semantic│  │DB)      │                      │
│  │Docs)    │  │         │  │Layer)   │  │         │                      │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘                      │
│       │             │             │             │                        │
│       └─────────────┼─────────────┼─────────────┘                        │
│                      ▼             ▼                                      │
│              ┌─────────────────────────────────┐                          │
│              │        Consumer Agent           │                          │
│              │         (Interactive            │                          │
│              │          CLI/Web)               │                          │
│              └─────────────────────────────────┘                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Service Ports:**
- **3000**: Offer Scraper (ACP documents)
- **3001**: GOR API (search endpoints)
- **3002**: MCP Server (semantic tools)
- **6333**: Qdrant (vector database)
- **4001-4003**: Restaurant Agents (future - Day 4)
- **3003**: Transaction Simulator (future - Day 5)

### MCP Server Architecture

The **MCP Offers Server** provides the semantic layer that connects consumer agents to the Global Offer Registry:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Consumer Agent  │───▶│  MCP Server      │───▶│  GOR API       │
│ (CLI/Web)      │    │  (Port 3002)     │    │  (Port 3001)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │  MCP Tools      │
                       │  • offers.search│
                       │  • offers.getById│
                       │  • offers.nearby │
                       └──────────────────┘
```

**Key Components:**
- **MCP Server**: Standardized interface for AI agents
- **GOR Client**: HTTP client for Global Offer Registry
- **Tool Handlers**: Process MCP tool calls and format responses
- **Data Models**: Pydantic models for type safety

## ACP Protocol Components

- **OSF**: Offer Syndication Feed (`.well-known/osf.json`)
- **Offer Document**: Individual offer with terms, attribution, provenance
- **Attribution Receipt**: Transaction proof from consumer to GOR
- **Settlement Postback**: Merchant confirmation to transaction simulator

## Technical Achievements

### ✅ **Real Data Scraping**
- Successfully bypassed Cloudflare protection
- Extracted real menu items with prices
- Organized data into proper categories
- Deduplicated and cleaned data
- **Simplified URL-only configuration**
- **Automatic cuisine detection from menu items**
- **Auto-generated restaurant IDs and metadata**

### ✅ **ACP Compliance**
- Generated valid OSF feeds
- Created proper offer documents
- Included all required fields (bounty, attribution, provenance)
- Used real merchant data (name, location, hours)

### ✅ **Demo Infrastructure**
- Live HTTP server serving ACP documents
- REST API for discovery
- CORS support for cross-origin access
- Screenshot and HTML capture for debugging
