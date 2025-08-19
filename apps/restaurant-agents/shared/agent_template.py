import asyncio
import json
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

from .models import (
    AgentState, OrderState, RestaurantConfig, A2AEnvelope,
    PresentOfferRequest, PresentOfferResponse,
    InitiateCheckoutRequest, InitiateCheckoutResponse,
    ConfirmOrderRequest, ConfirmOrderResponse
)

class RestaurantAgentTemplate:
    """Template for LangGraph-based restaurant agents"""
    
    def __init__(self, config: RestaurantConfig):
        self.config = config
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
        self.graph = self._build_graph()
        
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        # Define the state graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("discover_offers", self._discover_offers)
        workflow.add_node("present_offer", self._present_offer)
        workflow.add_node("gather_intent", self._gather_intent)
        workflow.add_node("initiate_checkout", self._initiate_checkout)
        workflow.add_node("confirm_order", self._confirm_order)
        workflow.add_node("complete_transaction", self._complete_transaction)
        
        # Define edges
        workflow.set_entry_point("discover_offers")
        workflow.add_edge("discover_offers", "present_offer")
        workflow.add_edge("present_offer", "gather_intent")
        workflow.add_edge("gather_intent", "initiate_checkout")
        workflow.add_edge("initiate_checkout", "confirm_order")
        workflow.add_edge("confirm_order", "complete_transaction")
        workflow.add_edge("complete_transaction", END)
        
        # Add conditional edges for error handling
        workflow.add_conditional_edges(
            "gather_intent",
            self._should_proceed_to_checkout,
            {
                "checkout": "initiate_checkout",
                "failed": END
            }
        )
        
        return workflow.compile()
    
    async def _discover_offers(self, state: AgentState) -> AgentState:
        """Discover available offers from OSF endpoint"""
        try:
            response = requests.get(self.config.osf_endpoint)
            if response.status_code == 200:
                osf_data = response.json()
                offers = osf_data.get("offers", [])
                
                if offers:
                    # Select the first available offer for demo
                    offer = offers[0]
                    state.current_offer = offer
                    state.order_state = OrderState.DISCOVERED
                    
                    # Add to conversation history
                    state.conversation_history.append({
                        "role": "system",
                        "content": f"Discovered offer: {offer.get('offer_id', 'Unknown')}",
                        "timestamp": datetime.now().isoformat()
                    })
            
        except Exception as e:
            state.conversation_history.append({
                "role": "system",
                "content": f"Error discovering offers: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })
        
        return state
    
    async def _present_offer(self, state: AgentState) -> AgentState:
        """Present offer to user via A2A"""
        if not state.current_offer:
            return state
        
        try:
            # Create A2A envelope for presenting offer
            envelope = A2AEnvelope(
                agent_id=f"agt_{self.config.restaurant_id}",
                audience="agt_consumer_demo",
                capabilities=["present_offer"],
                payload={
                    "offer_id": state.current_offer.get("offer_id"),
                    "user_context": state.user_preferences
                }
            )
            
            # Call A2A endpoint
            response = requests.post(
                f"{self.config.a2a_endpoints['present_offer']}",
                json=envelope.dict()
            )
            
            if response.status_code == 200:
                present_response = PresentOfferResponse(**response.json())
                state.order_state = OrderState.PRESENTED
                
                # Add to conversation history
                state.conversation_history.append({
                    "role": "assistant",
                    "content": f"Presented offer: {present_response.offer_summary}",
                    "timestamp": datetime.now().isoformat()
                })
        
        except Exception as e:
            state.conversation_history.append({
                "role": "system",
                "content": f"Error presenting offer: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })
        
        return state
    
    async def _gather_intent(self, state: AgentState) -> AgentState:
        """Gather user intent using LLM conversation"""
        if not state.current_offer:
            return state
        
        # Create conversation context
        messages = [
            SystemMessage(content=f"""You are a helpful restaurant agent for {self.config.name}. 
            You help customers understand offers and gather their order preferences.
            Be friendly, helpful, and guide them through the ordering process."""),
        ]
        
        # Add conversation history
        for msg in state.conversation_history[-5:]:  # Last 5 messages
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        
        # Add current offer context
        offer_info = f"""
        Current offer: {state.current_offer.get('title', 'Unknown')}
        Description: {state.current_offer.get('description', 'No description')}
        Minimum spend: ${state.current_offer.get('terms', {}).get('min_spend', 0)}
        """
        
        messages.append(HumanMessage(content=f"""
        {offer_info}
        
        Please help the customer understand this offer and gather their order preferences.
        Ask about their food preferences, dietary restrictions, and order details.
        """))
        
        # Get LLM response
        response = await self.llm.ainvoke(messages)
        
        # Update state
        state.conversation_history.append({
            "role": "assistant",
            "content": response.content,
            "timestamp": datetime.now().isoformat()
        })
        
        # For demo, assume user expresses intent
        state.order_state = OrderState.INTENT
        state.user_preferences.update({
            "dietary_restrictions": [],
            "preferred_items": [],
            "order_type": "dine-in"
        })
        
        return state
    
    def _should_proceed_to_checkout(self, state: AgentState) -> str:
        """Determine if we should proceed to checkout"""
        if state.order_state == OrderState.INTENT:
            return "checkout"
        return "failed"
    
    async def _initiate_checkout(self, state: AgentState) -> AgentState:
        """Initiate checkout process via A2A"""
        if not state.current_offer:
            return state
        
        try:
            # Create checkout request
            checkout_request = InitiateCheckoutRequest(
                offer_id=state.current_offer.get("offer_id"),
                items=[],  # Would be populated from user preferences
                pickup=False,
                notes="Demo order"
            )
            
            # Create A2A envelope
            envelope = A2AEnvelope(
                agent_id=f"agt_{self.config.restaurant_id}",
                audience="agt_consumer_demo",
                capabilities=["initiate_checkout"],
                payload=checkout_request.dict()
            )
            
            # Call A2A endpoint
            response = requests.post(
                f"{self.config.a2a_endpoints['initiate_checkout']}",
                json=envelope.dict()
            )
            
            if response.status_code == 200:
                checkout_response = InitiateCheckoutResponse(**response.json())
                state.current_order = checkout_response.dict()
                state.order_state = OrderState.CREATED
                
                # Add to conversation history
                state.conversation_history.append({
                    "role": "assistant",
                    "content": f"Order created: {checkout_response.order_id} - Total: ${checkout_response.total_amount}",
                    "timestamp": datetime.now().isoformat()
                })
        
        except Exception as e:
            state.conversation_history.append({
                "role": "system",
                "content": f"Error initiating checkout: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })
        
        return state
    
    async def _confirm_order(self, state: AgentState) -> AgentState:
        """Confirm order via A2A"""
        if not state.current_order:
            return state
        
        try:
            # Create confirmation request
            confirm_request = ConfirmOrderRequest(
                order_id=state.current_order.get("order_id")
            )
            
            # Create A2A envelope
            envelope = A2AEnvelope(
                agent_id=f"agt_{self.config.restaurant_id}",
                audience="agt_consumer_demo",
                capabilities=["confirm_order"],
                payload=confirm_request.dict()
            )
            
            # Call A2A endpoint
            response = requests.post(
                f"{self.config.a2a_endpoints['confirm_order']}",
                json=envelope.dict()
            )
            
            if response.status_code == 200:
                confirm_response = ConfirmOrderResponse(**response.json())
                state.order_state = OrderState.CONFIRMED
                
                # Add to conversation history
                state.conversation_history.append({
                    "role": "assistant",
                    "content": f"Order confirmed: {confirm_response.order_id}",
                    "timestamp": datetime.now().isoformat()
                })
        
        except Exception as e:
            state.conversation_history.append({
                "role": "system",
                "content": f"Error confirming order: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })
        
        return state
    
    async def _complete_transaction(self, state: AgentState) -> AgentState:
        """Complete the transaction"""
        state.order_state = OrderState.SETTLED
        
        # Add final message
        state.conversation_history.append({
            "role": "assistant",
            "content": f"Transaction completed! Your order is confirmed and will be ready soon.",
            "timestamp": datetime.now().isoformat()
        })
        
        return state
    
    async def process_user_message(self, message: str, session_id: str) -> str:
        """Process a user message and return agent response"""
        # Initialize or get state
        state = AgentState(session_id=session_id)
        
        # Add user message to history
        state.conversation_history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Run the graph
        result = await self.graph.ainvoke(state)
        
        # Return the last assistant message
        for msg in reversed(result["conversation_history"]):
            if msg["role"] == "assistant":
                return msg["content"]
        
        return "I'm here to help with your order!"
