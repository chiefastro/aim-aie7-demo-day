### Demo Day Project Plan — Agentic Offers and Restaurant Agents (v0)

---

#### 1) Goal

Ship an end-to-end prototype of the Agentic Commerce Protocol (ACP) for restaurants (Toast-powered online ordering as examples) that:
- Defines and publishes an open, machine-readable offer feed on merchant sites
- Indexes those feeds into a Global Offer Registry (GOR)
- Exposes the index via an MCP server for consumer agents
- Runs a mesh of per-restaurant agents speaking A2A to accept buying intents and “simulate” checkout
- Issues a mocked Attribution Receipt and settles a mocked bounty split to a consumer wallet

Success = live demo where a consumer agent discovers offers, “orders” from a restaurant agent, and receives a bounty credit.

---

#### 2) Naming: Agentic Commerce Protocol (ACP)

**Protocol Name**: Agentic Commerce Protocol (ACP)
- Clear scope: "Agentic" signals AI agent integration
- Industry standard: follows web protocol naming conventions (HTTP, SMTP, etc.)
- Future-proof: can encompass both commerce and content sides
- Professional: sounds like a real standard that could gain adoption
- Clean acronym: ACP

**Feed Format**: Offer Syndication Feed (OSF)
- Purpose: machine-readable feed for publishing offers
- Endpoint: `/.well-known/osf.json`
- Individual items: ACP Offer Document (v0)

**Hierarchy**:
- **ACP** = overall protocol for agent-commerce interactions
- **OSF** = feed format for publishing offers
- **Offer Document** = individual offer within an OSF
- **Attribution Receipt** = transaction proof document
- **Settlement Postback** = merchant confirmation document

---

#### 3) Architecture Overview (mapped to whitepaper)

- Publisher side (merchant):
  - Hosts an OSF endpoint that lists active offers (Offer Documents)
  - Optionally hosts a simple postback handler (mocked for demo)
- Global Offer Registry:
  - Crawls/ingests OSF endpoints
  - Normalizes, signs (demo key), and indexes offers with metadata (time, location, merchant)
  - Provides a search API to agents
- MCP Server:
  - Wraps the GOR search API as MCP tools for agent consumption
- Restaurant Agents (per merchant):
  - Receive buying intents over A2A
  - Present offers, “simulate” checkout and order lifecycle
  - Emit Settlement Postbacks to Transaction Simulator
- Transaction Simulator:
  - Issues Attribution Receipts on intent acceptance
  - Processes merchant postbacks
  - Computes and applies mock bounty splits to wallets
- Consumer Agent:
  - Uses MCP to discover offers and drive the flow end-to-end

---

#### 4) Data Model (v0)

4.1 ACP Offer Document (JSON)
```json
{
  "offer_id": "ofr_123",
  "merchant": {
    "id": "toast_acme_001",
    "name": "Acme Pizza",
    "domain": "order.acmepizza.com",
    "location": { "lat": 42.3601, "lng": -71.0589, "city": "Boston", "country": "US" }
  },
  "terms": {
    "trigger": "checkout_complete",
    "bounty": { "currency": "USD", "amount": 2.50, "rev_share_split": { "user": 0.5, "agent": 0.4, "associate": 0.1 } },
    "eligibility": ["US-MA"],
    "sku_scope": ["menu:*"],
    "schedule": { "days": ["Mon","Tue","Wed","Thu","Fri"], "local_time": { "start": "11:00", "end": "21:00" } },
    "expiration": "2026-12-31T23:59:59Z"
  },
  "attribution": {
    "method": "server_postback",
    "postback_url": "https://tx-sim.example.com/postbacks",
    "required_fields": ["order_id", "agent_id", "signature", "timestamp"],
    "signature_alg": "ed25519"
  },
  "provenance": {
    "publisher": "merchant_first_party",
    "published_at": "2025-08-13T01:02:03Z",
    "signature": "base64-edsig..."
  },
  "labels": ["pizza", "delivery", "lunch"],
  "geo": { "radius_m": 16000 }
}
```

4.2 ACP Offer Syndication Feed (OSF)
```json
{
  "osf_version": "0.1",
  "publisher": {
    "merchant_id": "toast_acme_001",
    "name": "Acme Pizza",
    "domain": "order.acmepizza.com"
  },
  "updated_at": "2025-08-13T01:02:03Z",
  "offers": [
    { "href": "https://order.acmepizza.com/.well-known/offers/ofr_123.json", "offer_id": "ofr_123", "updated_at": "2025-08-13T01:02:03Z" },
    { "href": "https://order.acmepizza.com/.well-known/offers/ofr_124.json", "offer_id": "ofr_124", "updated_at": "2025-08-13T01:02:03Z" }
  ]
}
```

4.3 ACP Attribution Receipt (Transaction Simulator → GOR)
```json
{
  "receipt_id": "rcpt_456",
  "offer_id": "ofr_123",
  "order_id": "ord_90210",
  "agent_id": "agt_consumer_demo",
  "user_id": "usr_demo",
  "timestamp": "2025-08-13T01:15:00Z",
  "bounty_reserved": { "currency": "USD", "amount": 2.50 },
  "signature": "base64-edsig..."
}
```

4.4 ACP Settlement Postback (Restaurant Agent → Transaction Simulator)
```json
{
  "order_id": "ord_90210",
  "status": "success",
  "amount": { "currency": "USD", "total": 28.00 },
  "split": { "user": 1.25, "agent": 1.00, "associate": 0.25 },
  "timestamp": "2025-08-13T01:17:42Z",
  "signature": "base64-merchant-edsig"
}
```

---

#### 5) Components & Deliverables

1. Offer Scraper (Toast examples)
- Input: list of Toast restaurant ordering URLs
- Output: extracted merchant metadata, hours, menu categories, and heuristics to generate offers
- Tech: Python + Playwright or Node + Playwright; store raw snapshots as JSON for repeatability

2. ACP OSF Generator
- Generates `/.well-known/osf.json` and individual ACP Offer Documents per merchant from scraped data
- For demo, serve these statically via a tiny HTTP server

3. Global Offer Registry (GOR)
- Ingests OSF endpoints (seed list), fetches referenced ACP Offer Documents
- Normalizes, validates, and indexes into Qdrant vector database
- Hybrid search with custom scoring: semantic relevance + geo proximity decay + time freshness decay
- Search API: semantic queries with geo and time weighting

4. MCP Server (Offers)
- Tools:
  - `offers.search(query, lat, lng, radius_m, labels[])`
  - `offers.getById(offer_id)`
  - `offers.nearby(lat, lng, radius_m)`
- Backed by GOR Search API

5. Restaurant Agents (one per merchant)
- HTTP service exposing A2A endpoints:
  - POST /a2a/present_offer → returns offer summary and constraints
  - POST /a2a/initiate_checkout → allocates mock order_id, returns payment instructions (mock)
  - POST /a2a/confirm_order → finalizes, triggers Settlement Postback to Transaction Simulator
- Minimal state machine: CREATED → CONFIRMED → SETTLED (or FAILED)

6. Transaction Simulator
- Issues Attribution Receipts on initiate_checkout
- Accepts Settlement Postbacks, computes split, and writes to a ledger
- Exposes /wallets/:user_id to read balances

7. Consumer Agent (demo driver)
- Uses MCP tools to discover offers and call restaurant A2A endpoints
- CLI or simple web UI to show steps, receipt, and wallet balance

Deliverables checklist
- ACP OSF schema docs + example
- At least 3 merchants with generated OSFs
- GOR search API + DB
- MCP server
- 3 restaurant agents
- Transaction Simulator + wallet UI/CLI
- Demo script that runs E2E

---

#### 6) APIs (v0)

GOR HTTP API
- GET /offers?query=...&lat=...&lng=...&radius_m=...&labels=pizza,delivery
- GET /offers/:offer_id
- GET /merchants/:merchant_id/offers
- Custom scoring: semantic relevance + geo proximity decay + time freshness decay

MCP Tools (namespaces: offers)
- search → params: query?, lat?, lng?, radius_m?, labels?[] → returns array of offers
- getById → params: offer_id → returns Offer Document
- nearby → params: lat, lng, radius_m → returns array of offers

A2A JSON (Restaurant Agent)
- Common envelope: { "a2a_version": "0.1", "agent_id": "agt_consumer_demo", "nonce": "...", "payload": { }, "signature": "..." }
- present_offer.payload: { "offer_id": "..." }
- initiate_checkout.payload: { "offer_id": "...", "items": [{"sku":"pizza_margherita","qty":1}], "pickup": false, "notes": "no onions" }
- confirm_order.payload: { "order_id": "..." }

Transaction Simulator
- POST /receipts (internal) — create Attribution Receipt
- POST /postbacks — receive Settlement Postbacks
- GET /wallets/:user_id — read wallet balance and history

---

#### 7) Implementation Plan & Timeline (7 days)

Day 1
- Finalize ACP OSF and Offer Document v0
- Build scraper for 3 Toast merchants and generate static OSFs + Offer Documents

Day 2
- Implement GOR ingester + validator
- Set up Qdrant collection with custom scoring function (geo + time decay)
- Implement vector embeddings for offer text (merchant name + labels + description)
- Expose GOR HTTP search API with hybrid ranking

Day 3
- Implement MCP server wrapping GOR
- Create demo Consumer Agent (CLI skeleton) calling MCP

Day 4
- Implement Restaurant Agent template and spin up 3 instances (configs per merchant)
- Implement A2A endpoints and order state machine

Day 5
- Implement Transaction Simulator: receipts, postbacks, ledger, wallet endpoint
- Wire Restaurant Agents → Transaction Simulator, and Consumer Agent → Restaurant Agents

Day 6
- End-to-end happy path: discover → present → initiate → confirm → receipt → wallet credit
- Add minimal UI/CLI polish and logs for demo clarity

Day 7
- Hardening, error paths (failed orders), geo/time filters, and documentation
- Record a backup demo video

---

#### 8) Demo Script (live)

1) Show ACP OSF on a merchant domain (static server) at `/.well-known/osf.json`
2) Show GOR search for "pizza near Boston"
3) In Consumer Agent CLI: run search via MCP and select an offer
4) Call Restaurant Agent present_offer then initiate_checkout (receipt is shown)
5) Confirm order; Settlement Postback arrives; wallet balance updates
6) Show receipt and ledger entries; highlight rev-share amounts

---

#### 9) Risks & Mitigations

- Scraping fragility → store HTML/JSON snapshots; use controlled examples
- Time/geo correctness → use mocked geolocation/time windows for determinism
- Multi-service complexity → use docker-compose or pm2 scripts to run all processes
- Signature/crypto → stub with deterministic demo keys; document as non-production

---

#### 10) Stretch Goals (nice-to-have if time)

- Basic agent disclosure UI (user sees rev-share and consents)
- Map view for nearby offers
- Simple policy-based selection (cheapest delivery fee, fastest prep time)
- Publisher-side OSF validator CLI

---

#### 11) Repo Layout (proposed)

```
apps/
  gor-api/                # GOR ingest + search HTTP API
  mcp-offers/             # MCP server exposing GOR
  tx-simulator/           # receipts, postbacks, wallet
  agent-restaurant-*/     # per-merchant agents (3 copies or one app with configs)
  consumer-agent-cli/     # demo driver
data/
  scraped/                # raw snapshots
  osf/                    # generated osf.json + offers
docs/
  schemas/                # JSON Schema for OSF/Offer/Receipt/Postback
```

---

#### 12) Acceptance Criteria

- At least 3 ACP OSF endpoints valid against schema
- GOR returns relevant offers by semantic search with geo/time decay ranking
- MCP tools operational from a consumer agent
- Restaurant Agent completes the state machine and emits postbacks
- Transaction Simulator produces a receipt and updates wallet
- Live demo runs in <5 minutes end-to-end


