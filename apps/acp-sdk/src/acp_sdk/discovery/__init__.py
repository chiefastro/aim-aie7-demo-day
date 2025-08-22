"""ACP Discovery Module

This module contains all the offer discovery and indexing functionality:
- Global Offer Registry (GOR)
- Vector search and semantic indexing
- OSF ingestion and processing
"""

from .registry import OfferRegistry
from .vector_search import VectorSearchService
from .ingestion import OSFIngestionService
from .gor_client import GORClient

__all__ = [
    "OfferRegistry",
    "VectorSearchService", 
    "OSFIngestionService",
    "GORClient",
]
