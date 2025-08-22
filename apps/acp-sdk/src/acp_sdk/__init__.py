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

# A2A module - Core functionality for restaurant agents
from .a2a import (
    # Core classes
    ACPAgent,
    ACPBaseExecutor,
    ACPServer,
    create_acp_server,
    
    # Configuration and models
    ACPConfig,
    AgentCapability,
    
    # Task models
    CommerceTask,
    CommerceResult,
    OrderTask,
    PaymentTask,
    OfferTask,
    InventoryTask,
    CustomerServiceTask,
    OrderResult,
    PaymentResult,
    OfferValidationResult,
    InventoryResult,
    CustomerServiceResult,
    
    # Data models
    OrderItem,
    OrderSummary,
    OfferDetails,
    PaymentRequest,
    PaymentDetails,
    
    # Enums
    TaskType,
    OrderStatus,
    PaymentStatus,
    PaymentMethod,
    
    # Skills
    BaseCommerceSkill,
    OrderManagementSkill,
    PaymentProcessingSkill,
    OfferManagementSkill,
    InventoryManagementSkill,
    CustomerServiceSkill,
    CommerceSkills,
    LLMEnhancedSkill,
    LLMEnhancedOrderSkill,
    LLMEnhancedPaymentSkill,
    
    # Exceptions
    ACPError,
    ConfigurationError,
    SkillExecutionError,
    ValidationError,
    HITLRequiredError,
)

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
    
    # A2A Core classes
    "ACPAgent",
    "ACPBaseExecutor",
    "ACPServer",
    "create_acp_server",
    
    # A2A Configuration and models
    "ACPConfig",
    "AgentCapability",
    
    # A2A Task models
    "CommerceTask",
    "CommerceResult",
    "OrderTask",
    "PaymentTask",
    "OfferTask",
    "InventoryTask",
    "CustomerServiceTask",
    "OrderResult",
    "PaymentResult",
    "OfferValidationResult",
    "InventoryResult",
    "CustomerServiceResult",
    
    # A2A Data models
    "OrderItem",
    "OrderSummary",
    "OfferDetails",
    "PaymentRequest",
    "PaymentDetails",
    
    # A2A Enums
    "TaskType",
    "OrderStatus",
    "PaymentStatus",
    "PaymentMethod",
    
    # A2A Skills
    "BaseCommerceSkill",
    "OrderManagementSkill",
    "PaymentProcessingSkill",
    "OfferManagementSkill",
    "InventoryManagementSkill",
    "CustomerServiceSkill",
    "CommerceSkills",
    "LLMEnhancedSkill",
    "LLMEnhancedOrderSkill",
    "LLMEnhancedPaymentSkill",
    
    # A2A Exceptions
    "ACPError",
    "ConfigurationError",
    "SkillExecutionError",
    "ValidationError",
    "HITLRequiredError",
    
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
