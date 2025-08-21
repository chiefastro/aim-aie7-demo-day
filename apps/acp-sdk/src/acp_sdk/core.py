"""
ACP Core - Main integration point between ACP skills and A2A agents.

This module provides the ACPAgent class that merchants can use to
create A2A agents with standardized commerce capabilities.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union

from a2a.types import AgentCard, AgentCapabilities, AgentSkill

from .exceptions import ACPError, ConfigurationError, SkillExecutionError
from .models import CommerceResult, CommerceTask
from .skills import CommerceSkills, BaseCommerceSkill

logger = logging.getLogger(__name__)


class ACPAgent:
    """
    ACP Agent that extends A2A agents with standardized commerce capabilities.
    
    This class provides a bridge between A2A protocol and ACP commerce skills,
    allowing merchants to implement standardized commerce operations while
    maintaining full control over their business logic.
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        description: str,
        capabilities: Optional[List[str]] = None,
        custom_skills: Optional[List[BaseCommerceSkill]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.capabilities = capabilities or ["extensions", "push_notifications", "state_transition_history"]
        self.config = config or {}
        
        # Initialize ACP commerce skills
        self.commerce_skills = CommerceSkills()
        
        # Add custom skills if provided
        if custom_skills:
            for skill in custom_skills:
                self.commerce_skills.add_skill(skill)
        
        logger.info(f"ACP Agent initialized: {self.name} ({self.agent_id})")
    
    def get_agent_card(self) -> AgentCard:
        """Generate A2A agent card with ACP capabilities."""
        # Convert ACP skills to A2A format
        a2a_skills = self.commerce_skills.to_a2a_format()
        
        # Create agent card
        agent_card = AgentCard(
            name=self.name,
            description=self.description,
            url=f"http://localhost:4001/",  # Default URL
            version="1.0.0",
            default_input_modes=['text', 'text/plain'],
            default_output_modes=['text', 'text/plain'],
            capabilities=AgentCapabilities(streaming=True, push_notifications=False),
            skills=a2a_skills,
        )
        
        return agent_card
    
    async def execute_commerce_task(self, task: CommerceTask) -> CommerceResult:
        """Execute a commerce task using the appropriate ACP skill."""
        try:
            # Determine which skill to use based on task type
            skill_id = self._get_skill_id_for_task(task)
            
            if not skill_id:
                raise SkillExecutionError(
                    f"No suitable skill found for task type: {task.task_type}",
                    task_id=task.task_id
                )
            
            # Execute the skill
            logger.info(f"Executing skill '{skill_id}' for task {task.task_id}")
            result = await self.commerce_skills.execute_skill(skill_id, task)
            
            logger.info(f"Skill '{skill_id}' completed successfully for task {task.task_id}")
            return result
            
        except Exception as e:
            logger.error(f"Commerce task execution failed: {str(e)}")
            if isinstance(e, ACPError):
                raise
            
            # Wrap unexpected errors in ACP exceptions
            raise SkillExecutionError(
                f"Unexpected error during task execution: {str(e)}",
                task_id=task.task_id
            )
    
    def _get_skill_id_for_task(self, task: CommerceTask) -> Optional[str]:
        """Determine which skill should handle the given task."""
        task_type = task.task_type
        
        # Map task types to skill IDs
        skill_mapping = {
            "order_food": "acp_order_management",
            "validate_offer": "acp_offer_management",
            "process_payment": "acp_payment_processing",
            "track_order": "acp_customer_service",
            "get_menu": "acp_inventory_management",
        }
        
        return skill_mapping.get(task_type)
    
    def add_custom_skill(self, skill: BaseCommerceSkill):
        """Add a custom commerce skill to the agent."""
        self.commerce_skills.add_skill(skill)
        logger.info(f"Added custom skill: {skill.skill_name}")
    
    def remove_skill(self, skill_id: str):
        """Remove a skill from the agent."""
        if skill_id in self.commerce_skills.skills:
            del self.commerce_skills.skills[skill_id]
            logger.info(f"Removed skill: {skill_id}")
        else:
            logger.warning(f"Skill not found: {skill_id}")
    
    def get_skill_info(self, skill_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific skill."""
        skill = self.commerce_skills.get_skill(skill_id)
        if skill:
            return {
                "id": skill_id,
                "name": skill.skill_name,
                "description": skill.description,
                "tags": skill.tags,
                "requires_hitl": skill.requires_hitl,
            }
        return None
    
    def list_skills(self) -> List[Dict[str, Any]]:
        """List all available skills."""
        return [
            self.get_skill_info(skill_id)
            for skill_id in self.commerce_skills.skills.keys()
        ]
    
    def is_acp_compliant(self) -> bool:
        """Check if the agent is ACP compliant."""
        required_skills = [
            "acp_order_management",
            "acp_payment_processing",
            "acp_offer_management",
        ]
        
        available_skills = set(self.commerce_skills.skills.keys())
        return all(skill in available_skills for skill in required_skills)
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check of the ACP agent."""
        health_status = {
            "status": "healthy",
            "agent_id": self.agent_id,
            "name": self.name,
            "acp_compliant": self.is_acp_compliant(),
            "skills_count": len(self.commerce_skills.skills),
            "capabilities": self.capabilities,
            "timestamp": asyncio.get_event_loop().time(),
        }
        
        # Check each skill
        skill_health = {}
        for skill_id, skill in self.commerce_skills.skills.items():
            try:
                # Basic skill validation
                skill_health[skill_id] = {
                    "status": "healthy",
                    "name": skill.skill_name,
                    "description": skill.description,
                }
            except Exception as e:
                skill_health[skill_id] = {
                    "status": "unhealthy",
                    "error": str(e),
                }
                health_status["status"] = "degraded"
        
        health_status["skills"] = skill_health
        return health_status


class ACPAgentBuilder:
    """Builder pattern for creating ACP agents with custom configurations."""
    
    def __init__(self):
        self.agent_id = None
        self.name = None
        self.description = None
        self.capabilities = []
        self.custom_skills = []
        self.config = {}
    
    def with_agent_id(self, agent_id: str) -> 'ACPAgentBuilder':
        """Set the agent ID."""
        self.agent_id = agent_id
        return self
    
    def with_name(self, name: str) -> 'ACPAgentBuilder':
        """Set the agent name."""
        self.name = name
        return self
    
    def with_description(self, description: str) -> 'ACPAgentBuilder':
        """Set the agent description."""
        self.description = description
        return self
    
    def with_capability(self, capability: str) -> 'ACPAgentBuilder':
        """Add an A2A capability."""
        self.capabilities.append(capability)
        return self
    
    def with_custom_skill(self, skill: BaseCommerceSkill) -> 'ACPAgentBuilder':
        """Add a custom commerce skill."""
        self.custom_skills.append(skill)
        return self
    
    def with_config(self, key: str, value: Any) -> 'ACPAgentBuilder':
        """Add a configuration value."""
        self.config[key] = value
        return self
    
    def build(self) -> ACPAgent:
        """Build the ACP agent."""
        if not self.agent_id:
            raise ConfigurationError("Agent ID is required")
        if not self.name:
            raise ConfigurationError("Agent name is required")
        if not self.description:
            raise ConfigurationError("Agent description is required")
        
        return ACPAgent(
            agent_id=self.agent_id,
            name=self.name,
            description=self.description,
            capabilities=self.capabilities,
            custom_skills=self.custom_skills,
            config=self.config
        )
