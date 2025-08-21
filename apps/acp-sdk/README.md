# ACP SDK - Standardized Commerce Capabilities for A2A Agents

The ACP SDK provides a complete framework for creating A2A agents with standardized commerce capabilities while maintaining compliance with the ACP protocol. This SDK dramatically reduces boilerplate code while maintaining full customizability.

## Key Features

- **Minimal Boilerplate**: Create a complete A2A agent with just a few lines of code
- **Standardized Capabilities**: Pre-defined commerce capabilities (orders, payments, offers, etc.)
- **Customizable**: Override specific methods to add custom business logic
- **ACP Compliant**: Full compliance with the Agentic Commerce Protocol
- **Production Ready**: Includes error handling, logging, and proper resource management

## Quick Start

### Basic Restaurant Agent (Minimal Code)

```python
from acp_sdk import create_acp_server, AgentCapability

# Create and run a restaurant agent with minimal configuration
server = create_acp_server(
    agent_id="my_restaurant",
    name="My Restaurant",
    description="A restaurant with ordering capabilities",
    osf_endpoint="http://localhost:8001/.well-known/osf.json",
    menu_endpoint="http://localhost:8001/a2a/menu",
    capabilities=[
        AgentCapability.PRESENT_OFFER,
        AgentCapability.INITIATE_CHECKOUT,
        AgentCapability.PROCESS_PAYMENT,
        AgentCapability.GET_MENU,
    ],
    host="localhost",
    port=4001
)

server.run()
```

### Custom Restaurant Agent (With Business Logic)

```python
from acp_sdk import (
    ACPBaseExecutor, 
    OrderManagementSkill, 
    PaymentProcessingSkill,
    create_acp_server,
    AgentCapability
)

class MyRestaurantSkill(OrderManagementSkill):
    async def _handle_order_task(self, task):
        # Your custom order logic here
        return await super()._handle_order_task(task)

class MyRestaurantExecutor(ACPBaseExecutor):
    def _create_custom_skills(self):
        return [MyRestaurantSkill(self.config)]
    
    async def _handle_general_conversation(self, query: str, context_id: str) -> str:
        return f"Welcome to {self.config.name}! How can I help you today?"

# Create server with custom executor
server = create_acp_server(
    agent_id="my_restaurant",
    name="My Restaurant",
    description="A restaurant with custom ordering logic",
    osf_endpoint="http://localhost:8001/.well-known/osf.json",
    menu_endpoint="http://localhost:8001/a2a/menu",
    capabilities=[AgentCapability.INITIATE_CHECKOUT, AgentCapability.PROCESS_PAYMENT],
    executor_class=MyRestaurantExecutor,
    host="localhost",
    port=4001
)

server.run()
```

## Architecture

### Core Components

1. **ACPConfig**: Standardized configuration model
2. **ACPBaseExecutor**: Base executor that handles all A2A boilerplate
3. **ACPServer**: Complete A2A server implementation
4. **ACP Skills**: Standardized commerce skill implementations

### Capability System

The SDK provides standardized capabilities that map to A2A skills:

- `PRESENT_OFFER`: Present offers to customers
- `INITIATE_CHECKOUT`: Start the checkout process
- `CONFIRM_ORDER`: Confirm and finalize orders
- `VALIDATE_OFFER`: Validate offer applicability
- `PROCESS_PAYMENT`: Process payments
- `GET_MENU`: Retrieve menu information
- `TRACK_ORDER`: Track order status

### Customization Points

Merchants can customize behavior by overriding these methods:

```python
class MyRestaurantExecutor(ACPBaseExecutor):
    def _create_custom_skills(self) -> List[Any]:
        """Create custom ACP skills for this agent."""
        return [MyCustomSkill(self.config)]
    
    async def _handle_general_conversation(self, query: str, context_id: str) -> str:
        """Handle general conversation queries."""
        return "Custom conversation response"
    
    async def _custom_capability_handler(
        self, 
        capability: AgentCapability, 
        payload: Dict[str, Any]
    ) -> Optional[str]:
        """Handle custom capability requests."""
        return "Custom capability response"
```

## Advanced Usage

### Custom Skills

Create custom skills by extending the base skill classes:

```python
from acp_sdk import OrderManagementSkill, OrderResult

class CustomOrderSkill(OrderManagementSkill):
    async def _handle_order_task(self, task):
        # Custom order processing logic
        order_id = self._generate_custom_order_id()
        
        return OrderResult(
            task_id=task.task_id,
            success=True,
            data={"order_id": order_id}
        )
```

### Custom Configuration

Extend the configuration for additional settings:

```python
from acp_sdk import ACPConfig

class RestaurantConfig(ACPConfig):
    tax_rate: float = 0.08
    delivery_fee: float = 5.00
    max_order_value: float = 100.00
```

### Command Line Usage

Run a server directly from command line:

```bash
python -m acp_sdk.server \
    --agent-id "my_restaurant" \
    --name "My Restaurant" \
    --description "A restaurant agent" \
    --osf-endpoint "http://localhost:8001/.well-known/osf.json" \
    --menu-endpoint "http://localhost:8001/a2a/menu" \
    --capabilities "present_offer,initiate_checkout,process_payment" \
    --host "localhost" \
    --port 4001
```

## Migration from Previous Version

If you're migrating from the previous version:

1. **Replace RestaurantConfig with ACPConfig**:
   ```python
   # Old
   from shared.models import RestaurantConfig
   
   # New
   from acp_sdk import ACPConfig
   ```

2. **Replace RestaurantAgentExecutor with ACPBaseExecutor**:
   ```python
   # Old
   class MyExecutor(RestaurantAgentExecutor):
   
   # New
   class MyExecutor(ACPBaseExecutor):
   ```

3. **Use create_acp_server factory function**:
   ```python
   # Old
   config = RestaurantConfig(...)
   server = A2AStarletteApplication(...)
   
   # New
   server = create_acp_server(
       agent_id="my_agent",
       name="My Agent",
       # ... other config
   )
   ```

## Examples

See the `examples/` directory for complete working examples:

- `simple_restaurant_agent.py`: Minimal restaurant agent
- `custom_restaurant_agent.py`: Restaurant with custom business logic
- `multi_capability_agent.py`: Agent with multiple capabilities

## API Reference

### Core Classes

- `ACPConfig`: Configuration model for ACP agents
- `ACPBaseExecutor`: Base executor with A2A boilerplate
- `ACPServer`: Complete A2A server implementation
- `ACPAgent`: ACP agent with skill management

### Factory Functions

- `create_acp_server()`: Create a server with minimal configuration

### Models

- `AgentCapability`: Enum of available capabilities
- `CommerceTask`: Base class for commerce tasks
- `OrderTask`, `PaymentTask`, etc.: Specific task types
- `CommerceResult`: Base class for task results

### Skills

- `BaseCommerceSkill`: Base class for all commerce skills
- `OrderManagementSkill`: Order processing skill
- `PaymentProcessingSkill`: Payment processing skill
- `OfferManagementSkill`: Offer management skill
- `InventoryManagementSkill`: Inventory/menu management skill

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
