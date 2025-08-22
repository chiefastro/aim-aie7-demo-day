"""
ACP Server - Standardized A2A server with minimal boilerplate.

This module provides a standardized server class that handles all the A2A
protocol boilerplate while allowing merchants to focus on their business logic.
"""

import logging
import os
import sys
import asyncio
from typing import Any, Dict, Optional, Type

import click
import httpx
import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import (
    BasePushNotificationSender,
    InMemoryPushNotificationConfigStore,
    InMemoryTaskStore,
)
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)

from .models import ACPConfig, AgentCapability
from .executor import ACPBaseExecutor
from .core import ACPAgent

logger = logging.getLogger(__name__)


class ACPServer:
    """
    Standardized ACP server that handles all A2A protocol boilerplate.
    
    This class provides a complete A2A server implementation that merchants
    can use with minimal configuration.
    """
    
    def __init__(self, config: ACPConfig, executor_class: Optional[Type[ACPBaseExecutor]] = None):
        self.config = config
        self.executor_class = executor_class or ACPBaseExecutor
        
        # Initialize ACP agent for skill generation
        self.acp_agent = ACPAgent(
            agent_id=config.agent_id,
            name=config.name,
            description=config.description
        )
        
        logger.info(f"ACP Server initialized for {config.name}")
    
    def get_agent_card(self) -> AgentCard:
        """Generate the A2A agent card with all capabilities."""
        # Define agent capabilities
        capabilities = AgentCapabilities(streaming=True, push_notifications=False)
        
        # Generate skills from capabilities
        skills = self._generate_skills_from_capabilities()
        
        # Create agent card
        agent_card = AgentCard(
            name=self.config.name,
            description=self.config.description,
            url=f"http://{self.config.host}:{self.config.port}/",
            version=self.config.version,
            default_input_modes=['text', 'text/plain'],
            default_output_modes=['text', 'text/plain'],
            capabilities=capabilities,
            skills=skills,
        )
        
        return agent_card
    
    def _generate_skills_from_capabilities(self) -> list[AgentSkill]:
        """Generate A2A skills from ACP capabilities."""
        skills = []
        
        # Only generate ACP-compliant skills - these are the standardized ones
        # that all ACP agents should support
        skills.extend([
            AgentSkill(
                id='acp_order_management',
                name='ACP Order Management',
                description='Standardized order management using ACP protocol',
                tags=['acp', 'commerce', 'order'],
                examples=['order food', 'place order', 'create order'],
            ),
            AgentSkill(
                id='acp_payment_processing',
                name='ACP Payment Processing',
                description='Standardized payment processing using ACP protocol',
                tags=['acp', 'commerce', 'payment'],
                examples=['process payment', 'make payment', 'pay for order'],
            ),
            AgentSkill(
                id='acp_offer_management',
                name='ACP Offer Management',
                description='Standardized offer management using ACP protocol',
                tags=['acp', 'commerce', 'offer'],
                examples=['validate offer', 'check offer', 'apply offer'],
            ),
            AgentSkill(
                id='acp_inventory_management',
                name='ACP Inventory Management',
                description='Standardized inventory management using ACP protocol',
                tags=['acp', 'commerce', 'inventory'],
                examples=['get menu', 'show menu', 'menu items'],
            ),
        ])
        
        # Add merchant-specific skills based on capabilities
        # These provide natural language examples for the merchant's specific operations
        for capability in self.config.capabilities:
            skill = self._create_merchant_skill_from_capability(capability)
            if skill:
                skills.append(skill)
        
        return skills
    
    def _create_merchant_skill_from_capability(self, capability: AgentCapability) -> Optional[AgentSkill]:
        """Create a merchant-specific skill from an ACP capability."""
        # Map capabilities to merchant-specific skills that provide natural language examples
        capability_skills = {
            AgentCapability.PRESENT_OFFER: AgentSkill(
                id=f'{self.config.agent_id}_present_offer',
                name=f'{self.config.name} - Present Offers',
                description=f'Present offers and specials from {self.config.name}',
                tags=['merchant', 'offers', 'specials'],
                examples=[
                    f'Show me {self.config.name} specials',
                    f'What offers does {self.config.name} have?',
                    'Show me today\'s deals',
                    'What\'s on special?'
                ],
            ),
            AgentCapability.INITIATE_CHECKOUT: AgentSkill(
                id=f'{self.config.agent_id}_initiate_checkout',
                name=f'{self.config.name} - Start Order',
                description=f'Start ordering from {self.config.name}',
                tags=['merchant', 'ordering', 'checkout'],
                examples=[
                    f'I want to order from {self.config.name}',
                    'Let\'s start my order',
                    'I\'m ready to checkout',
                    'Begin my order'
                ],
            ),
            AgentCapability.CONFIRM_ORDER: AgentSkill(
                id=f'{self.config.agent_id}_confirm_order',
                name=f'{self.config.name} - Confirm Order',
                description=f'Confirm and finalize your order with {self.config.name}',
                tags=['merchant', 'confirmation', 'order'],
                examples=[
                    'Confirm my order',
                    'Finalize my purchase',
                    'Complete my order',
                    'Place my order'
                ],
            ),
            AgentCapability.VALIDATE_OFFER: AgentSkill(
                id=f'{self.config.agent_id}_validate_offer',
                name=f'{self.config.name} - Validate Offers',
                description=f'Check if offers can be applied to your {self.config.name} order',
                tags=['merchant', 'validation', 'offers'],
                examples=[
                    'Can I use this coupon?',
                    'Is this offer valid?',
                    'Check if my discount applies',
                    'Validate my promo code'
                ],
            ),
            AgentCapability.PROCESS_PAYMENT: AgentSkill(
                id=f'{self.config.agent_id}_process_payment',
                name=f'{self.config.name} - Process Payment',
                description=f'Process payment for your {self.config.name} order',
                tags=['merchant', 'payment', 'checkout'],
                examples=[
                    'Pay for my order',
                    'Process my payment',
                    'Complete payment',
                    'Charge my card'
                ],
            ),
            AgentCapability.GET_MENU: AgentSkill(
                id=f'{self.config.agent_id}_get_menu',
                name=f'{self.config.name} - Menu',
                description=f'View the menu and offerings from {self.config.name}',
                tags=['merchant', 'menu', 'food'],
                examples=[
                    f'Show me {self.config.name} menu',
                    'What\'s on the menu?',
                    'What do you serve?',
                    'Show me your food'
                ],
            ),
            AgentCapability.TRACK_ORDER: AgentSkill(
                id=f'{self.config.agent_id}_track_order',
                name=f'{self.config.name} - Track Order',
                description=f'Track the status of your {self.config.name} order',
                tags=['merchant', 'tracking', 'status'],
                examples=[
                    'Where is my order?',
                    'Track my order',
                    'What\'s the status?',
                    'When will it be ready?'
                ],
            ),
        }
        
        return capability_skills.get(capability)
    
    def create_app(self):
        """Create the A2A Starlette application."""
        # Initialize A2A components
        httpx_client = httpx.AsyncClient()
        push_config_store = InMemoryPushNotificationConfigStore()
        push_sender = BasePushNotificationSender(
            httpx_client=httpx_client,
            config_store=push_config_store
        )
        
        # Create executor instance
        executor = self.executor_class(self.config)
        
        # Create request handler
        request_handler = DefaultRequestHandler(
            agent_executor=executor,
            task_store=InMemoryTaskStore(),
            push_config_store=push_config_store,
            push_sender=push_sender
        )
        
        # Create and return A2A server
        server = A2AStarletteApplication(
            agent_card=self.get_agent_card(), 
            http_handler=request_handler
        )
        
        app = server.build()
        
        # Add additional well-known endpoint for compatibility
        from starlette.responses import JSONResponse
        
        @app.route("/.well-known/agent-card.json", methods=["GET"])
        async def agent_card_alt(request):
            """Alternative agent card endpoint for compatibility"""
            return JSONResponse(self.get_agent_card().model_dump())
        
        return app
    
    def run(self, host: Optional[str] = None, port: Optional[int] = None):
        """Run the A2A server."""
        host = host or self.config.host
        port = port or self.config.port
        
        app = self.create_app()
        
        logger.info(f"Starting {self.config.name} A2A server on {host}:{port}")
        uvicorn.run(app, host=host, port=port)


def create_acp_server(
    agent_id: str,
    name: str,
    description: str,
    osf_endpoint: str,
    menu_endpoint: str,
    capabilities: list[AgentCapability],
    a2a_endpoints: Optional[Dict[str, str]] = None,
    executor_class: Optional[Type[ACPBaseExecutor]] = None,
    **kwargs
) -> ACPServer:
    """
    Factory function to create an ACP server with minimal configuration.
    
    Args:
        agent_id: Unique agent identifier
        name: Agent display name
        description: Agent description
        osf_endpoint: OSF discovery endpoint
        menu_endpoint: Menu retrieval endpoint
        capabilities: List of supported capabilities
        a2a_endpoints: Optional A2A operation endpoints
        executor_class: Optional custom executor class
        **kwargs: Additional configuration options
    
    Returns:
        Configured ACPServer instance
    """
    config = ACPConfig(
        agent_id=agent_id,
        name=name,
        description=description,
        osf_endpoint=osf_endpoint,
        menu_endpoint=menu_endpoint,
        capabilities=capabilities,
        a2a_endpoints=a2a_endpoints or {},
        **kwargs
    )
    
    return ACPServer(config, executor_class)


@click.command()
@click.option('--host', 'host', default='localhost')
@click.option('--port', 'port', default=4001)
@click.option('--agent-id', 'agent_id', required=True, help='Agent ID')
@click.option('--name', 'name', required=True, help='Agent name')
@click.option('--description', 'description', required=True, help='Agent description')
@click.option('--osf-endpoint', 'osf_endpoint', required=True, help='OSF endpoint')
@click.option('--menu-endpoint', 'menu_endpoint', required=True, help='Menu endpoint')
@click.option('--capabilities', 'capabilities', required=True, help='Comma-separated list of capabilities')
def main(host, port, agent_id, name, description, osf_endpoint, menu_endpoint, capabilities):
    """Start an ACP A2A server with minimal configuration."""
    # Parse capabilities
    capability_list = [
        AgentCapability(cap.strip()) 
        for cap in capabilities.split(',')
    ]
    
    # Create and run server
    server = create_acp_server(
        agent_id=agent_id,
        name=name,
        description=description,
        osf_endpoint=osf_endpoint,
        menu_endpoint=menu_endpoint,
        capabilities=capability_list,
        host=host,
        port=port
    )
    
    server.run(host=host, port=port)


if __name__ == '__main__':
    main()
