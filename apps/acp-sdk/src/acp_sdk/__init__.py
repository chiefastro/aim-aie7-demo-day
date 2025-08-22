"""
ACP SDK - Standardized commerce capabilities for ACP protocol.

This package provides a complete framework for creating ACP-compliant services
with standardized commerce capabilities while maintaining compliance with the ACP protocol.
"""

# Transaction processing module
from .txns import WalletManager, PrivacyManager, create_txn_simulator_app

# Discovery module
from .discovery import GORClient, OfferRegistry, VectorSearchService, OSFIngestionService

# MCP module
from .mcp import mcp, main as mcp_main, ACPClient

# Models
from .models.offers import Offer, SearchOffersInput, GetOfferByIdInput, NearbyOffersInput
from .models.receipts import CreateReceiptRequest, CreateReceiptResponse, AttributionReceipt
from .models.postbacks import ProcessPostbackRequest, ProcessPostbackResponse, SettlementPostback
from .models.wallets import WalletResponse, ProtocolStats

__version__ = "1.0.0"

__all__ = [
    # Transaction processing
    "WalletManager",
    "PrivacyManager",
    "create_txn_simulator_app",
    
    # Discovery
    "GORClient",
    "OfferRegistry", 
    "VectorSearchService",
    "OSFIngestionService",
    
    # MCP
    "mcp",
    "mcp_main",
    "ACPClient",
    
    # Models
    "Offer",
    "SearchOffersInput",
    "GetOfferByIdInput", 
    "NearbyOffersInput",
    "CreateReceiptRequest",
    "CreateReceiptResponse",
    "AttributionReceipt",
    "ProcessPostbackRequest",
    "ProcessPostbackResponse",
    "SettlementPostback",
    "WalletResponse",
    "ProtocolStats",
]
