# ACP Skill Architecture: Unified Design

This document explains the unified skill architecture in the ACP SDK and how merchants customize behavior.

## Overview

The ACP SDK uses a **unified skill architecture** where all operations go through standardized ACP skills, with merchant customization happening through custom skill implementations.

## Skill Types

### 1. **ACP Skills** (Standardized)
These are the core ACP protocol skills that all ACP-compliant agents must support:

- `acp_order_management` - Handle orders
- `acp_payment_processing` - Process payments  
- `acp_offer_management` - Manage offers
- `acp_inventory_management` - Handle menu/inventory

**Purpose**: Provide standardized interfaces for ACP-compliant clients.

### 2. **Merchant Skills** (Customizable)
These are merchant-specific skills generated from ACP capabilities:

- `{agent_id}_present_offer` - "Show me Otto Portland specials"
- `{agent_id}_initiate_checkout` - "I want to order from Otto Portland"
- `{agent_id}_get_menu` - "Show me Otto Portland menu"

**Purpose**: Provide natural language examples specific to the merchant.

## How It Works

### Skill Generation Flow

```python
# 1. Merchant declares capabilities
config = ACPConfig(
    capabilities=[
        AgentCapability.PRESENT_OFFER,
        AgentCapability.INITIATE_CHECKOUT,
    ]
)

# 2. ACP SDK generates skills
skills = [
    # Standard ACP skills (always present)
    AgentSkill(id='acp_order_management', ...),
    AgentSkill(id='acp_payment_processing', ...),
    AgentSkill(id='acp_offer_management', ...),
    AgentSkill(id='acp_inventory_management', ...),
    
    # Merchant-specific skills (based on capabilities)
    AgentSkill(id='otto_portland_present_offer', 
              name='Otto Portland - Present Offers',
              examples=['Show me Otto Portland specials', ...]),
    AgentSkill(id='otto_portland_initiate_checkout',
              name='Otto Portland - Start Order', 
              examples=['I want to order from Otto Portland', ...]),
]
```

### Request Routing

All requests are routed through the ACP skills:

```python
# Natural language: "Show me Otto Portland specials"
# 1. Detected as capability request
# 2. Routed to ACP inventory management skill
# 3. Custom skill implementation handles the business logic
```

## Merchant Customization

### Method 1: Custom Skills (Recommended)

Override `_create_custom_skills()` to provide custom implementations:

```python
class MyRestaurantExecutor(ACPBaseExecutor):
    def _create_custom_skills(self):
        return [
            MyCustomOrderSkill(self.config),
            MyCustomPaymentSkill(self.config),
            MyCustomOfferSkill(self.config),
        ]

class MyCustomOrderSkill(OrderManagementSkill):
    async def _handle_order_task(self, task):
        # Your custom order logic here
        return await super()._handle_order_task(task)

class MyCustomOfferSkill(OfferManagementSkill):
    async def _validate_offer(self, offer_id, items):
        # Your custom offer validation logic
        return {"is_valid": True, "discount": 2.50}
```

### Method 2: Override Base Methods

Override specific methods in the executor:

```python
class MyRestaurantExecutor(ACPBaseExecutor):
    async def _get_menu_structured(self) -> str:
        # Custom menu retrieval logic
        return json.dumps({"menu_items": my_custom_menu})
    
    async def _create_order_structured(self, items, offer_id, pickup, delivery_address, special_instructions) -> str:
        # Custom order creation logic
        return json.dumps({"order_id": my_custom_order_id})
```

## Key Benefits

### 1. **Unified Interface**
- All operations go through ACP skills
- Consistent behavior across all agents
- Standardized error handling

### 2. **Clear Customization Path**
- Custom skills override ACP skill behavior
- Base methods provide fallback implementations
- No confusion about which code path to use

### 3. **ACP Compliance**
- All agents support standard ACP operations
- Clients can rely on consistent interfaces
- Protocol compliance is automatic

### 4. **Merchant Branding**
- Merchant skills provide branded examples
- Natural language specific to the merchant
- Clear connection between capabilities and skills

## Example: Complete Customization

```python
from acp_sdk import (
    create_acp_server, 
    ACPBaseExecutor,
    OrderManagementSkill,
    AgentCapability
)

class CustomOrderSkill(OrderManagementSkill):
    async def _handle_order_task(self, task):
        # Custom order logic
        order_id = f"custom_{self.config.agent_id}_{len(self.orders) + 1}"
        
        # Apply custom business rules
        if task.total > 50:
            # Free delivery for orders over $50
            task.delivery_fee = 0
        
        return await super()._handle_order_task(task)

class MyRestaurantExecutor(ACPBaseExecutor):
    def _create_custom_skills(self):
        return [CustomOrderSkill(self.config)]
    
    async def _handle_general_conversation(self, query: str, context_id: str) -> str:
        return f"Welcome to {self.config.name}! How can I help you today?"

# Create server with custom executor
server = create_acp_server(
    agent_id="my_restaurant",
    name="My Restaurant", 
    description="A restaurant with custom ordering logic",
    capabilities=[AgentCapability.INITIATE_CHECKOUT, AgentCapability.PROCESS_PAYMENT],
    executor_class=MyRestaurantExecutor,
    # ... other config
)

server.run()
```

## Migration from Old Design

### Before (Confusing)
```python
# Two different skill types with unclear relationships
skills = [
    AgentSkill(id='present_offer', ...),  # From capability
    AgentSkill(id='acp_order_management', ...),  # Always present
]

# Different code paths
if "present offer":
    return await self._custom_capability_handler(...)
elif "order food":  
    return await self.acp_agent.execute_commerce_task(...)
```

### After (Unified)
```python
# All skills go through ACP agent
skills = [
    AgentSkill(id='acp_order_management', ...),  # Standard ACP
    AgentSkill(id='my_restaurant_present_offer', ...),  # Merchant-specific
]

# Single code path
return await self.acp_agent.execute_commerce_task(task)
```

This unified approach eliminates confusion and provides a clear path for merchant customization while maintaining ACP compliance.
