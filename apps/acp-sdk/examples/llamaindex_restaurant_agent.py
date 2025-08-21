#!/usr/bin/env python3
"""
LlamaIndex + ACP SDK Restaurant Agent Example

This example shows how a merchant can integrate LlamaIndex with the ACP SDK
to create a true AI agent with reasoning capabilities while maintaining
ACP compliance.
"""

import asyncio
import click
from typing import Dict, Any

# LlamaIndex imports
from llama_index.agent import ReActAgent
from llama_index.llms import OpenAI
from llama_index.tools import FunctionTool
from llama_index.core.tools import BaseTool

# ACP SDK imports
from acp_sdk import (
    ACPConfig, 
    AgentCapability,
    create_llamaindex_acp_agent,
    LLMEnhancedOrderSkill,
    LLMEnhancedPaymentSkill,
    LLMEnhancedOfferSkill
)

# Mock restaurant config
RESTAURANT_CONFIG = ACPConfig(
    agent_id="llamaindex_restaurant",
    name="AI-Powered Restaurant",
    description="Restaurant agent with LlamaIndex reasoning capabilities",
    osf_endpoint="http://localhost:8001/.well-known/osf.json",
    menu_endpoint="http://localhost:8001/menu",
    capabilities=[
        AgentCapability.PRESENT_OFFER,
        AgentCapability.INITIATE_CHECKOUT,
        AgentCapability.CONFIRM_ORDER,
        AgentCapability.VALIDATE_OFFER
    ]
)


class LlamaIndexRestaurantTools:
    """Custom tools for LlamaIndex restaurant agent."""
    
    def __init__(self, config: ACPConfig):
        self.config = config
        self.order_history = []
        self.customer_preferences = {}
        
    def get_menu_recommendations(self, customer_id: str, dietary_restrictions: str = None) -> str:
        """Get personalized menu recommendations based on customer preferences."""
        preferences = self.customer_preferences.get(customer_id, {})
        
        # Mock menu with recommendations
        menu = {
            "appetizers": ["Bruschetta", "Calamari", "Caprese Salad"],
            "main_courses": ["Margherita Pizza", "Pasta Carbonara", "Grilled Salmon"],
            "desserts": ["Tiramisu", "Gelato", "Cannoli"]
        }
        
        # Apply dietary restrictions
        if dietary_restrictions:
            if "vegetarian" in dietary_restrictions.lower():
                menu["main_courses"] = ["Margherita Pizza", "Pasta Carbonara", "Vegetable Risotto"]
            if "gluten-free" in dietary_restrictions.lower():
                menu["main_courses"] = ["Grilled Salmon", "Vegetable Risotto", "Gluten-Free Pizza"]
        
        # Add personalized recommendations
        if preferences.get("likes_spicy"):
            menu["main_courses"].append("Spicy Arrabbiata Pasta")
        
        return f"Personalized menu for {customer_id}:\n" + \
               "\n".join([f"{category}: {', '.join(items)}" for category, items in menu.items()])
    
    def analyze_customer_sentiment(self, customer_feedback: str) -> str:
        """Analyze customer feedback sentiment and extract insights."""
        # Mock sentiment analysis
        positive_words = ["great", "amazing", "delicious", "wonderful", "excellent"]
        negative_words = ["bad", "terrible", "awful", "disgusting", "poor"]
        
        feedback_lower = customer_feedback.lower()
        positive_count = sum(1 for word in positive_words if word in feedback_lower)
        negative_count = sum(1 for word in negative_words if word in feedback_lower)
        
        if positive_count > negative_count:
            sentiment = "positive"
            action = "Consider offering loyalty rewards"
        elif negative_count > positive_count:
            sentiment = "negative"
            action = "Follow up with customer service"
        else:
            sentiment = "neutral"
            action = "Monitor for improvement opportunities"
        
        return f"Sentiment: {sentiment}\nRecommended Action: {action}"
    
    def suggest_upselling_opportunities(self, current_order: str, customer_id: str) -> str:
        """Suggest upselling opportunities based on current order and customer history."""
        order_lower = current_order.lower()
        suggestions = []
        
        # Analyze order for upselling opportunities
        if "pizza" in order_lower:
            suggestions.append("Add extra cheese or premium toppings")
        if "pasta" in order_lower:
            suggestions.append("Add garlic bread or side salad")
        if "salad" in order_lower:
            suggestions.append("Add protein (chicken, shrimp, or salmon)")
        
        # Check customer history for preferences
        preferences = self.customer_preferences.get(customer_id, {})
        if preferences.get("likes_dessert"):
            suggestions.append("Add tiramisu or gelato for dessert")
        
        if not suggestions:
            suggestions.append("Add a beverage or appetizer")
        
        return f"Upselling suggestions for {customer_id}:\n" + "\n".join(f"- {s}" for s in suggestions)


class LlamaIndexRestaurantAgent:
    """Restaurant agent powered by LlamaIndex with ACP compliance."""
    
    def __init__(self, config: ACPConfig, openai_api_key: str):
        self.config = config
        self.tools = LlamaIndexRestaurantTools(config)
        
        # Initialize LlamaIndex agent
        self.llm = OpenAI(model="gpt-4", api_key=openai_api_key)
        
        # Create LlamaIndex tools
        self.llama_tools = [
            FunctionTool.from_defaults(
                fn=self.tools.get_menu_recommendations,
                name="get_menu_recommendations",
                description="Get personalized menu recommendations based on customer preferences and dietary restrictions"
            ),
            FunctionTool.from_defaults(
                fn=self.tools.analyze_customer_sentiment,
                name="analyze_customer_sentiment", 
                description="Analyze customer feedback sentiment and extract actionable insights"
            ),
            FunctionTool.from_defaults(
                fn=self.tools.suggest_upselling_opportunities,
                name="suggest_upselling_opportunities",
                description="Suggest upselling opportunities based on current order and customer history"
            )
        ]
        
        # Create LlamaIndex agent
        self.llama_agent = ReActAgent.from_tools(
            self.llama_tools,
            llm=self.llm,
            verbose=True
        )
        
        # Create ACP agent with LlamaIndex integration
        self.acp_agent = create_llamaindex_acp_agent(config, self.llama_agent)
        
        # Add LLM-enhanced skills
        self._setup_enhanced_skills()
    
    def _setup_enhanced_skills(self):
        """Setup LLM-enhanced ACP skills."""
        # Create enhanced skills with LLM capabilities
        enhanced_order_skill = LLMEnhancedOrderSkill(
            llm_client=self.llm,
            config=self.config
        )
        
        enhanced_payment_skill = LLMEnhancedPaymentSkill(
            llm_client=self.llm,
            config=self.config
        )
        
        enhanced_offer_skill = LLMEnhancedOfferSkill(
            llm_client=self.llm,
            config=self.config
        )
        
        # Add skills to ACP agent
        acp_core_agent = self.acp_agent.get_acp_agent()
        acp_core_agent.add_custom_skill(enhanced_order_skill)
        acp_core_agent.add_custom_skill(enhanced_payment_skill)
        acp_core_agent.add_custom_skill(enhanced_offer_skill)
    
    async def initialize(self):
        """Initialize the agent."""
        await self.acp_agent.initialize()
        print(f"🤖 LlamaIndex Restaurant Agent initialized: {self.config.name}")
    
    async def process_query(self, query: str, customer_id: str = None) -> str:
        """Process a customer query using LlamaIndex reasoning."""
        context = {
            "customer_id": customer_id,
            "restaurant_name": self.config.name,
            "available_capabilities": [cap.value for cap in self.config.capabilities]
        }
        
        # Add customer preferences to context if available
        if customer_id and customer_id in self.tools.customer_preferences:
            context["customer_preferences"] = self.tools.customer_preferences[customer_id]
        
        response = await self.acp_agent.process_query(query, context)
        return response
    
    async def handle_commerce_task(self, task_type: str, task_data: Dict[str, Any]) -> str:
        """Handle commerce tasks through ACP skills."""
        from acp_sdk.models import CommerceTask
        
        task = CommerceTask(
            task_type=task_type,
            task_id=f"task_{asyncio.get_event_loop().time()}",
            data=task_data
        )
        
        result = await self.acp_agent.execute_commerce_task(task)
        return f"Task completed: {result.success} - {result.data}"


@click.command()
@click.option('--openai-api-key', required=True, help='OpenAI API key for LlamaIndex')
@click.option('--customer-id', default='demo_customer', help='Customer ID for testing')
def main(openai_api_key: str, customer_id: str):
    """Run the LlamaIndex restaurant agent example."""
    
    async def run_example():
        # Create agent
        agent = LlamaIndexRestaurantAgent(RESTAURANT_CONFIG, openai_api_key)
        await agent.initialize()
        
        # Example queries to test the agent
        test_queries = [
            "I'm looking for a vegetarian dinner option",
            "What would you recommend for someone who likes spicy food?",
            "I had a great experience last time, the pizza was amazing!",
            "I'd like to order a margherita pizza",
            "What can I add to my pasta order to make it a complete meal?"
        ]
        
        print("\n🧪 Testing LlamaIndex Restaurant Agent:")
        print("=" * 50)
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Query: {query}")
            print("-" * 30)
            
            try:
                response = await agent.process_query(query, customer_id)
                print(f"Response: {response}")
            except Exception as e:
                print(f"Error: {e}")
        
        print("\n✅ Example completed!")
    
    # Run the example
    asyncio.run(run_example())


if __name__ == "__main__":
    main()
