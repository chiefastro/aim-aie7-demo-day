# Global Offer Registry (GOR) API

This is the Global Offer Registry API for the ACP Demo, implemented in Python using FastAPI and Qdrant vector database.

## Features

- **Offer Ingestion**: Automatically ingests offers from the demo server
- **Vector Search**: Uses OpenAI embeddings for semantic search
- **Hybrid Ranking**: Combines semantic relevance + geographic proximity + time freshness
- **RESTful API**: FastAPI-based endpoints for offer discovery
- **Real-time Indexing**: Updates offer index as new offers are published

## Architecture

```
Demo Server (localhost:3000) → GOR API (localhost:3001) → Qdrant Vector DB (localhost:6333)
                                    ↓
                              FastAPI + Hybrid Search
```

## Prerequisites

1. **Qdrant Vector Database**: Running on localhost:6333
2. **Demo Server**: Running on localhost:3000 (from offer-scraper)
3. **Python 3.11+**: For modern async/await and performance features
4. **uv**: Fast Python package manager ([install here](https://docs.astral.sh/uv/getting-started/installation/))
5. **OpenAI API Key** (optional): For real embeddings, falls back to mock if not available

## Quick Start

### 1. Build Docker Image

```bash
cd apps/gor-api
make build
```

### 2. Start Services with Docker Compose

```bash
# Start Qdrant and GOR API
make up

# Or start just Qdrant if you want to run API locally
docker run -p 6333:6333 qdrant/qdrant
```

### 3. Ingest Offers

```bash
make ingest
```

### 4. Start the API Server

```bash
# Development mode with auto-reload
make dev

# Or manually
python src/main.py
```

## API Endpoints

### Health Check
- `GET /health` - Service status and version

### Search Offers
- `GET /offers` - Search offers with hybrid ranking
  - Query parameters:
    - `query`: Search text
    - `lat`, `lng`: Geographic coordinates
    - `radius_m`: Search radius in meters
    - `labels`: Comma-separated label filters
    - `limit`, `offset`: Pagination

### Individual Offers
- `GET /offers/{offer_id}` - Get offer by ID
- `GET /merchants/{merchant_id}/offers` - Get all offers for a merchant

### Registry Management
- `GET /stats` - Registry statistics
- `POST /ingest` - Trigger offer ingestion

## Example Usage

### Search for Pizza Near Boston

```bash
curl "http://localhost:3001/offers?query=pizza&lat=42.3601&lng=-71.0589&radius_m=50000"
```

### Get Registry Stats

```bash
curl "http://localhost:3001/stats"
```

### Ingest New Offers

```bash
curl -X POST "http://localhost:3001/ingest"
```

## Configuration

### Environment Variables

Create a `.env` file in the `gor-api` directory:

```env
# OpenAI API Key (optional - falls back to mock embeddings)
OPENAI_API_KEY=your_openai_api_key_here

# Qdrant connection (defaults to localhost:6333)
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Demo server URL (defaults to localhost:3000)
DEMO_SERVER_URL=http://localhost:3000
```

### Docker Environment

When using Docker Compose, environment variables are automatically configured:

```bash
# Start with Docker Compose (recommended for development)
make up

# Environment is automatically configured for:
# - QDRANT_HOST=qdrant (internal Docker network)
# - QDRANT_PORT=6333
# - DEMO_SERVER_URL=http://host.docker.internal:3000
```

### Mock Embeddings

If no OpenAI API key is provided, the system automatically falls back to deterministic mock embeddings. These are:

- **Deterministic**: Same text always produces same embedding
- **Hash-based**: Uses MD5 hash of text for pseudo-random generation
- **Normalized**: Properly normalized for cosine distance calculations
- **1536-dimensional**: Matches OpenAI's embedding dimensions

## Search Algorithm

The hybrid ranking system combines three scores:

1. **Semantic Relevance (50%)**: Text matching, label matching, title/description boost
2. **Geographic Proximity (30%)**: Haversine distance calculation with radius decay
3. **Time Freshness (20%)**: Days until expiration with urgency scoring

### Scoring Details

- **Semantic**: Word matches, exact phrases, label relevance
- **Geo**: Within radius (0.8-1.0), outside radius (0.0-0.8)
- **Time**: Expires soon (1.0), this month (0.8), this quarter (0.6), later (0.4)

## Data Flow

1. **Ingestion**: Fetches merchants from demo server → gets OSF feeds → downloads individual offers
2. **Processing**: Generates search text → creates embeddings → stores in Qdrant
3. **Search**: Receives query → applies filters → calculates hybrid scores → returns ranked results

## Development

### Development Tools

The project uses modern Python development tools:

- **pyproject.toml**: Dependency management and project configuration
- **uv**: Fast Python package manager and installer
- **Makefile**: Common development commands
- **Docker Compose**: Local development environment
- **Black**: Code formatting
- **isort**: Import sorting
- **mypy**: Type checking
- **pytest**: Testing framework

### Project Structure

```
src/
├── main.py              # FastAPI application
├── models/
│   └── offer_models.py  # Pydantic models
└── services/
    ├── gor_service.py    # Core GOR logic
    ├── search_service.py # Hybrid ranking
    └── embedding_service.py # Vector embeddings

# Configuration files
├── pyproject.toml       # Python project configuration
├── docker-compose.yml   # Local development services
├── Dockerfile          # GOR API container
└── Makefile            # Development commands
```

### Adding New Features

1. **New Endpoints**: Add to `main.py`
2. **New Models**: Extend `offer_models.py`
3. **New Logic**: Create services in `services/`
4. **New Search**: Extend `search_service.py`

### Development Commands

```bash
# See all available commands
make help

# Build Docker image
make build

# Start development server (in container)
make dev

# Run tests (in container)
make test

# Start Docker services
make up

# Stop Docker services
make down

# Ingest offers (in container)
make ingest

# Container access
make shell          # Open shell in container
make run CMD="..."  # Run command in container

# Clean up generated files
make clean
```

### Why uv?

The project uses `uv` for dependency management because it's:

- **Faster**: 10-100x faster than pip for dependency resolution
- **Reliable**: Deterministic lockfiles and reproducible builds
- **Modern**: Built-in virtual environment management
- **Compatible**: Works seamlessly with existing Python tooling

### Testing

```bash
# Run tests
make test

# Test ingestion
make ingest

# Manual API testing
curl http://localhost:3001/health
```

## Troubleshooting

### Common Issues

1. **Qdrant Connection Failed**
   - Ensure Qdrant is running on localhost:6333
   - Check firewall settings

2. **Demo Server Unreachable**
   - Verify offer-scraper server is running on localhost:3000
   - Check network connectivity

3. **Import Errors**
   - Ensure you're in the `gor-api` directory
   - Check Python path includes `src/`
   - Verify `uv` is installed: `uv --version`

4. **Embedding Issues**
   - Check OpenAI API key if using real embeddings
   - Mock embeddings will work without API key

### Logs

The API provides detailed logging for debugging:

- **INFO**: Normal operations and status
- **WARNING**: Non-critical issues (e.g., missing API key)
- **ERROR**: Critical failures and exceptions
- **DEBUG**: Detailed operation information

## Next Steps

This completes Day 2 of the ACP Demo plan. The next steps are:

- **Day 3**: MCP Server wrapping GOR
- **Day 4**: Restaurant Agents with A2A endpoints
- **Day 5**: Transaction Simulator
- **Day 6**: End-to-end integration
- **Day 7**: Hardening and documentation
