"""
ACP SDK - Standardized commerce capabilities for A2A agents.

This package provides a complete framework for creating A2A agents with
standardized commerce capabilities while maintaining compliance with the ACP protocol.
"""

from .core import ACPAgent
from ..models.a2a_connector import (
    ACPConfig,
    AgentCapability,
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
    OrderItem,
    OrderSummary,
    OfferDetails,
    PaymentRequest,
    PaymentDetails,
    TaskType,
    OrderStatus,
    PaymentStatus,
    PaymentMethod,
)
from .skills import (
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
)
from .executor import ACPBaseExecutor
from .server import ACPServer, create_acp_server
from .exceptions import (
    ACPError,
    ConfigurationError,
    SkillExecutionError,
    ValidationError,
    HITLRequiredError,
)

# Protocol standards
from ..models.osf import OSFFeed, OSFOffer
from ..models.offers import Offer, OfferContent, OfferTerms, OfferBounty, Merchant, MerchantLocation
from ..models.receipts import AttributionReceipt, PublicReceiptData, PrivateReceiptData
from ..models.postbacks import SettlementPostback, PublicSettlementData, PrivateSettlementData
from ..models.wallets import UserWallet, AgentWallet, GORWallet, MerchantWallet, PublicWalletData, PrivateWalletData, MerchantWalletPublicData, MerchantWalletPrivateData

# Discovery and indexing
from ..discovery import (
    OfferRegistry,
    VectorSearchService,
    OSFIngestionService,
)

# MCP tools and server
from ..mcp.acp_mcp import mcp as ACPMCPServer
from .server import create_acp_server
MCPTools = None  # Not implemented yet

# Agent framework integrations
from .agent_frameworks import (
    AgentFrameworkAdapter,
    LangGraphACPAdapter,
    LlamaIndexACPAdapter,
    AutoGenACPAdapter,
    ACPAgentFrameworkExecutor,
    create_langgraph_acp_agent,
    create_llamaindex_acp_agent,
    create_autogen_acp_agent,
)

__version__ = "1.0.0"

__all__ = [
    # Core classes
    "ACPAgent",
    "ACPBaseExecutor",
    "ACPServer",
    "create_acp_server",
    
    # Configuration and models
    "ACPConfig",
    "AgentCapability",
    
    # Task models
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
    
    # Data models
    "OrderItem",
    "OrderSummary",
    "OfferDetails",
    "PaymentRequest",
    "PaymentDetails",
    
    # Enums
    "TaskType",
    "OrderStatus",
    "PaymentStatus",
    "PaymentMethod",
    
    # Skills
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
    
    # Protocol standards
    "OSFFeed", "OSFOffer",
    "Offer", "OfferContent", "OfferTerms", "OfferBounty", "Merchant", "MerchantLocation",
    "AttributionReceipt", "PublicReceiptData", "PrivateReceiptData",
    "SettlementPostback", "PublicSettlementData", "PrivateSettlementData",
    "UserWallet", "AgentWallet", "GORWallet", "MerchantWallet",
    "PublicWalletData", "PrivateWalletData",
    "MerchantWalletPublicData", "MerchantWalletPrivateData",
    
    # Discovery and indexing
    "OfferRegistry",
    "VectorSearchService",
    "OSFIngestionService",
    
    # MCP tools and server
    "ACPMCPServer",
    "create_acp_server",
    "MCPTools",
    
    # Exceptions
    "ACPError",
    "ConfigurationError",
    "SkillExecutionError",
    "ValidationError",
    "HITLRequiredError",
    
    # Agent Framework Integrations
    "AgentFrameworkAdapter",
    "LangGraphACPAdapter",
    "LlamaIndexACPAdapter",
    "AutoGenACPAdapter",
    "ACPAgentFrameworkExecutor",
    "create_langgraph_acp_agent",
    "create_llamaindex_acp_agent",
    "create_autogen_acp_agent",
]
