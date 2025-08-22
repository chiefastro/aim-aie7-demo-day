"""
Agent Framework Integration Examples

This module shows how merchants can integrate different agent frameworks
with the ACP SDK to create true AI agents with reasoning capabilities.
"""

import asyncio
from typing import Any, Dict, List, Optional, Type
from abc import ABC, abstractmethod

from ..models.a2a_connector import ACPConfig, CommerceTask, CommerceResult
from .core import ACPAgent
from .skills import BaseCommerceSkill


class AgentFrameworkAdapter(ABC):
    """
    Abstract base class for integrating agent frameworks with ACP SDK.
    
    This allows merchants to use their preferred agent framework (LangGraph,
    LlamaIndex, AutoGen, etc.) while maintaining ACP compliance.
    """
    
    def __init__(self, acp_config: ACPConfig, acp_agent: ACPAgent):
        self.acp_config = acp_config
        self.acp_agent = acp_agent
        self.framework_agent = None
        
    @abstractmethod
    async def initialize(self):
        """Initialize the agent framework."""
        pass
        
    @abstractmethod
    async def process_query(self, query: str, context: Dict[str, Any]) -> str:
        """Process a query using the agent framework."""
        pass
        
    @abstractmethod
    async def execute_commerce_task(self, task: CommerceTask) -> CommerceResult:
        """Execute a commerce task through the agent framework."""
        pass


class LangGraphACPAdapter(AgentFrameworkAdapter):
    """
    LangGraph integration with ACP SDK.
    
    Example usage:
    ```python
    from langchain_openai import ChatOpenAI
    from langgraph.graph import StateGraph, END
    
    # Create LangGraph agent
    llm = ChatOpenAI(model="gpt-4")
    
    # Define state
    class AgentState(TypedDict):
        query: str
        context: Dict[str, Any]
        commerce_task: Optional[CommerceTask]
        response: str
        
    # Build graph
    workflow = StateGraph(AgentState)
    workflow.add_node("analyze", analyze_query)
    workflow.add_node("execute_commerce", execute_commerce_task)
    workflow.add_node("generate_response", generate_response)
    
    # Create adapter
    adapter = LangGraphACPAdapter(acp_config, acp_agent, workflow)
    ```
    """
    
    def __init__(self, acp_config: ACPConfig, acp_agent: ACPAgent, graph: Any):
        super().__init__(acp_config, acp_agent)
        self.graph = graph
        
    async def initialize(self):
        """Initialize LangGraph agent."""
        # Compile the graph
        self.framework_agent = self.graph.compile()
        
    async def process_query(self, query: str, context: Dict[str, Any]) -> str:
        """Process query through LangGraph."""
        if not self.framework_agent:
            await self.initialize()
            
        # Create initial state
        initial_state = {
            "query": query,
            "context": context,
            "commerce_task": None,
            "response": ""
        }
        
        # Execute graph
        result = await self.framework_agent.ainvoke(initial_state)
        return result["response"]
        
    async def execute_commerce_task(self, task: CommerceTask) -> CommerceResult:
        """Execute commerce task through LangGraph."""
        # This would integrate with LangGraph's task execution
        # The graph could have nodes for different commerce operations
        return await self.acp_agent.execute_commerce_task(task)


class LlamaIndexACPAdapter(AgentFrameworkAdapter):
    """
    LlamaIndex integration with ACP SDK.
    
    Example usage:
    ```python
    from llama_index.agent import ReActAgent
    from llama_index.llms import OpenAI
    
    # Create LlamaIndex agent
    llm = OpenAI(model="gpt-4")
    agent = ReActAgent.from_tools(tools, llm=llm)
    
    # Create adapter
    adapter = LlamaIndexACPAdapter(acp_config, acp_agent, agent)
    ```
    """
    
    def __init__(self, acp_config: ACPConfig, acp_agent: ACPAgent, llama_agent: Any):
        super().__init__(acp_config, acp_agent)
        self.llama_agent = llama_agent
        
    async def initialize(self):
        """Initialize LlamaIndex agent."""
        self.framework_agent = self.llama_agent
        
    async def process_query(self, query: str, context: Dict[str, Any]) -> str:
        """Process query through LlamaIndex."""
        if not self.framework_agent:
            await self.initialize()
            
        # Add context to query
        enhanced_query = f"""
        Context: {context}
        Query: {query}
        
        Please help with this request using the available tools.
        """
        
        # Execute LlamaIndex agent
        response = await self.framework_agent.achat(enhanced_query)
        return str(response)
        
    async def execute_commerce_task(self, task: CommerceTask) -> CommerceResult:
        """Execute commerce task through LlamaIndex."""
        # Convert ACP task to LlamaIndex tool call
        tool_query = f"Execute commerce task: {task.task_type} with data: {task.data}"
        response = await self.framework_agent.achat(tool_query)
        
        # Parse response and convert back to ACP format
        # This is a simplified example
        return CommerceResult(
            task_id=task.task_id,
            success=True,
            data={"response": str(response)}
        )


class AutoGenACPAdapter(AgentFrameworkAdapter):
    """
    AutoGen integration with ACP SDK.
    
    Example usage:
    ```python
    import autogen
    
    # Create AutoGen agents
    config_list = [{"model": "gpt-4", "api_key": "your-key"}]
    
    assistant = autogen.AssistantAgent(
        name="assistant",
        llm_config={"config_list": config_list}
    )
    
    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10
    )
    
    # Create adapter
    adapter = AutoGenACPAdapter(acp_config, acp_agent, assistant, user_proxy)
    ```
    """
    
    def __init__(self, acp_config: ACPConfig, acp_agent: ACPAgent, 
                 assistant_agent: Any, user_proxy: Any):
        super().__init__(acp_config, acp_agent)
        self.assistant_agent = assistant_agent
        self.user_proxy = user_proxy
        
    async def initialize(self):
        """Initialize AutoGen agents."""
        # AutoGen agents are typically initialized in constructor
        pass
        
    async def process_query(self, query: str, context: Dict[str, Any]) -> str:
        """Process query through AutoGen."""
        # Create chat with context
        enhanced_query = f"""
        Context: {context}
        User Query: {query}
        """
        
        # Initiate chat between agents
        chat_result = await self.user_proxy.ainitiate_chat(
            self.assistant_agent,
            message=enhanced_query
        )
        
        # Extract response from chat
        return str(chat_result)
        
    async def execute_commerce_task(self, task: CommerceTask) -> CommerceResult:
        """Execute commerce task through AutoGen."""
        # Create task-specific prompt
        task_prompt = f"""
        Execute the following commerce task:
        Type: {task.task_type}
        Data: {task.data}
        
        Use the available ACP skills to complete this task.
        """
        
        # Execute through AutoGen
        result = await self.user_proxy.ainitiate_chat(
            self.assistant_agent,
            message=task_prompt
        )
        
        return CommerceResult(
            task_id=task.task_id,
            success=True,
            data={"response": str(result)}
        )


class ACPAgentFrameworkExecutor:
    """
    Enhanced ACP executor that integrates with agent frameworks.
    
    This allows merchants to use their preferred agent framework while
    maintaining ACP compliance and standardized commerce capabilities.
    """
    
    def __init__(self, acp_config: ACPConfig, framework_adapter: AgentFrameworkAdapter):
        self.acp_config = acp_config
        self.framework_adapter = framework_adapter
        self.acp_agent = ACPAgent(
            agent_id=acp_config.agent_id,
            name=acp_config.name,
            description=acp_config.description
        )
        
    async def initialize(self):
        """Initialize the agent framework."""
        await self.framework_adapter.initialize()
        
    async def process_query(self, query: str, context: Dict[str, Any] = None) -> str:
        """Process a query using the agent framework."""
        if context is None:
            context = {}
            
        return await self.framework_adapter.process_query(query, context)
        
    async def execute_commerce_task(self, task: CommerceTask) -> CommerceResult:
        """Execute a commerce task through the agent framework."""
        return await self.framework_adapter.execute_commerce_task(task)
        
    def get_acp_agent(self) -> ACPAgent:
        """Get the underlying ACP agent."""
        return self.acp_agent


# Factory functions for easy integration
def create_langgraph_acp_agent(acp_config: ACPConfig, graph: Any) -> ACPAgentFrameworkExecutor:
    """Create a LangGraph-powered ACP agent."""
    acp_agent = ACPAgent(
        agent_id=acp_config.agent_id,
        name=acp_config.name,
        description=acp_config.description
    )
    adapter = LangGraphACPAdapter(acp_config, acp_agent, graph)
    return ACPAgentFrameworkExecutor(acp_config, adapter)


def create_llamaindex_acp_agent(acp_config: ACPConfig, llama_agent: Any) -> ACPAgentFrameworkExecutor:
    """Create a LlamaIndex-powered ACP agent."""
    acp_agent = ACPAgent(
        agent_id=acp_config.agent_id,
        name=acp_config.name,
        description=acp_config.description
    )
    adapter = LlamaIndexACPAdapter(acp_config, acp_agent, llama_agent)
    return ACPAgentFrameworkExecutor(acp_config, adapter)


def create_autogen_acp_agent(acp_config: ACPConfig, assistant_agent: Any, 
                           user_proxy: Any) -> ACPAgentFrameworkExecutor:
    """Create an AutoGen-powered ACP agent."""
    acp_agent = ACPAgent(
        agent_id=acp_config.agent_id,
        name=acp_config.name,
        description=acp_config.description
    )
    adapter = AutoGenACPAdapter(acp_config, acp_agent, assistant_agent, user_proxy)
    return ACPAgentFrameworkExecutor(acp_config, adapter)
