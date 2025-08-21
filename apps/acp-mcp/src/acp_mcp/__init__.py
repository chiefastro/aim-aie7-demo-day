"""
ACP MCP Server - Universal commerce MCP server for ACP-compliant merchants.

This MCP server provides standardized commerce tools that work with any
ACP-compliant merchant agent, enabling universal commerce integration.
"""

from .client import ACPClient
from .models import (
    CommerceRequest,
    CommerceResponse,
    MerchantInfo,
    OrderRequest,
    PaymentRequest,
    OfferValidationRequest,
)

__version__ = "0.1.0"
__author__ = "ACP Team"
__email__ = "team@acp.dev"

__all__ = [
    "ACPClient",
    "CommerceRequest",
    "CommerceResponse", 
    "MerchantInfo",
    "OrderRequest",
    "PaymentRequest",
    "OfferValidationRequest",
]
