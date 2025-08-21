# ACP SDK - Agentic Commerce Protocol for Python

The ACP SDK provides standardized commerce skills for A2A agents, enabling universal commerce integration across all merchants. This SDK extends the A2A protocol with commerce-specific capabilities while maintaining full flexibility for merchant customization.

## 🚀 What is ACP?

**ACP (Agentic Commerce Protocol)** is an extension of the A2A protocol that standardizes commerce capabilities across all merchants. Instead of every merchant building their own MCP integration, they can:

- **Implement standardized commerce skills** that any ACP-compliant client can use
- **Customize business logic** while maintaining protocol compliance
- **Get instant access** to all ACP-enabled chat clients and MCP servers
- **Focus on their core business** instead of integration complexity

## 🏗️ Architecture

```
Consumer Chat Client → Universal Commerce MCP Server → ACP-Compliant A2A Agent
       ↓                           ↓                           ↓
   MCP Tools              Standardized Commerce Tasks    Merchant-Specific Logic
                                                              (via ACP SDK)
```

## ✨ Key Features

- **Standardized Commerce Skills**: Order management, payment, inventory, offers
- **A2A Integration**: Seamlessly extends existing A2A agents
- **Merchant Customization**: Full flexibility while maintaining compliance
- **HITL Support**: Built-in human-in-the-loop workflows
- **Multi-language Foundation**: Python SDK with TypeScript roadmap

## 📦 Installation

```bash
# Install from PyPI (when published)
pip install acp-sdk

# Or install from source
git clone https://github.com/acp-org/acp-sdk-python
cd acp-sdk-python
pip install -e .
```

## 🚀 Quick Start

### 1. Create an ACP Agent

```python
from acp_sdk import ACPAgent, OrderManagementSkill, PaymentProcessingSkill

# Create your restaurant agent
restaurant_agent = ACPAgent(
    agent_id="agt_my_restaurant",
    name="My Restaurant",
    description="Delicious food for everyone",
    custom_skills=[
        MyCustomOrderSkill(),  # Your custom implementation
        MyCustomPaymentSkill(), # Your custom implementation
    ]
)

# Check if you're ACP compliant
print(f"ACP Compliant: {restaurant_agent.is_acp_compliant()}")
```

### 2. Implement Custom Skills

```python
from acp_sdk import OrderManagementSkill, OrderSummary, OrderStatus
from decimal import Decimal

class MyCustomOrderSkill(OrderManagementSkill):
    """Your restaurant's custom order management."""
    
    async def _create_order(self, task):
        # Your custom business logic here
        subtotal = sum(item.total for item in task.items)
        tax = subtotal * Decimal("0.08")  # Your tax rate
        total = subtotal + tax
        
        return OrderSummary(
            order_id=f"order_{task.task_id}",
            restaurant_id=task.restaurant_id,
            items=task.items,
            subtotal=subtotal,
            tax=tax,
            total=total,
            status=OrderStatus.CREATED
        )
    
    async def _apply_offer(self, offer_id, items):
        # Your custom offer logic here
        if offer_id == "lunch_special":
            # Apply 10% discount
            return {"discount": "10%", "type": "percentage"}
        return None
```

### 3. Use with A2A

```python
# Generate A2A agent card with ACP capabilities
agent_card = restaurant_agent.get_agent_card()

# Execute commerce tasks
result = await restaurant_agent.execute_commerce_task(order_task)
```

## 🛠️ Available Skills

### Core Commerce Skills

| Skill | Description | Required Methods |
|-------|-------------|------------------|
| **Order Management** | Handle food orders and modifications | `_create_order()`, `_apply_offer()` |
| **Payment Processing** | Process payments and refunds | `_process_payment()` |
| **Offer Management** | Validate and apply offers | `_validate_offer()` |
| **Inventory Management** | Query menu and availability | `_get_menu()` |
| **Customer Service** | Handle inquiries and tracking | `_handle_inquiry()` |

### Skill Implementation Pattern

```python
class MyCustomSkill(BaseCommerceSkill):
    async def execute(self, task):
        # 1. Validate input
        await self._validate_input(task)
        
        # 2. Execute business logic
        result = await self._execute_business_logic(task)
        
        # 3. Return standardized result
        return CommerceResult(
            task_id=task.task_id,
            success=True,
            data=result
        )
    
    async def _execute_business_logic(self, task):
        # Your custom implementation here
        pass
```

## 🔧 Configuration

### Agent Configuration

```python
config = {
    "merchant_type": "restaurant",
    "cuisine": "italian",
    "location": "New York, NY",
    "payment_methods": ["credit_card", "cash"],
    "delivery_radius": 5000,  # meters
    "business_hours": {
        "monday": "9:00-22:00",
        "tuesday": "9:00-22:00",
        # ... etc
    }
}

agent = ACPAgent(
    agent_id="agt_my_restaurant",
    name="My Restaurant",
    description="Delicious food",
    config=config
)
```

### Skill Configuration

```python
class MySkill(BaseCommerceSkill):
    def __init__(self, config=None):
        super().__init__(
            skill_name="My Skill",
            description="My custom skill",
            tags=["custom", "restaurant"]
        )
        self.config = config or {}
        self.minimum_amount = self.config.get("minimum_amount", 10.00)
```

## 🧪 Testing

### Run the Example

```bash
cd examples
python otto_portland_example.py
```

### Expected Output

```
🍕 OTTO Portland ACP SDK Example
==================================================

🏪 Agent: OTTO Portland
   ID: agt_otto_portland
   ACP Compliant: True
   Skills: 5

🛠️  Available Skills:
   • Order Management: Handle food orders, modifications, and cancellations
   • Payment Processing: Process payments and handle refunds
   • Offer Management: Validate and apply offers to orders
   • Inventory Management: Query menu items and check availability
   • Customer Service: Handle customer inquiries and order tracking

📝 Creating Sample Order:
✅ OTTO Portland order created: otto_12345
   Items: 2
   Subtotal: $40.97
   Tax: $3.48
   Total: $44.45

💳 Payment processed: pay_otto_12345
   Method: credit_card
   Amount: $44.45
   Status: completed

✅ Order completed successfully!
   Task ID: 12345
   Order ID: otto_12345

✅ Payment completed successfully!

🏥 Agent Health Check:
   Status: healthy
   Skills: 5

🎉 Example completed!
```

## 🔍 HITL (Human-in-the-Loop) Support

ACP SDK includes built-in support for human intervention workflows:

```python
class MySkill(BaseCommerceSkill):
    async def execute(self, task):
        # Check if human approval is needed
        if task.amount > 1000:
            approval = await self.request_human_input(
                "Large order requires approval. Approve?",
                options=["Yes", "No"]
            )
            
            if approval != "Yes":
                raise ValueError("Order not approved")
        
        # Continue with processing
        return await self._process_order(task)
```

## 📚 API Reference

### Core Classes

- **`ACPAgent`**: Main agent class that integrates ACP skills with A2A
- **`BaseCommerceSkill`**: Base class for all commerce skills
- **`CommerceSkills`**: Container for managing multiple skills
- **`ACPAgentBuilder`**: Builder pattern for creating agents

### Data Models

- **`CommerceTask`**: Base class for all commerce tasks
- **`CommerceResult`**: Base class for all commerce results
- **`OrderTask`**, **`PaymentTask`**, etc.: Specific task types
- **`OrderSummary`**, **`PaymentResult`**, etc.: Specific result types

### Exceptions

- **`ACPError`**: Base exception for all ACP errors
- **`SkillExecutionError`**: When skill execution fails
- **`ValidationError`**: When input validation fails
- **`HITLRequiredError`**: When human intervention is needed

## 🚧 Roadmap

### v0.2.0 (Next)
- [ ] Advanced HITL workflows
- [ ] Skill marketplace support
- [ ] Performance monitoring
- [ ] More commerce skill types

### v0.3.0
- [ ] TypeScript SDK
- [ ] Go SDK
- [ ] Rust SDK
- [ ] Advanced analytics

### v1.0.0
- [ ] Production-ready
- [ ] Full ACP specification compliance
- [ ] Enterprise features
- [ ] Cloud deployment support

## 🤝 Contributing

We welcome contributions! Here are some ways to help:

1. **Implement new skills** for different commerce types
2. **Add examples** for different merchant types
3. **Improve documentation** and add tutorials
4. **Report bugs** and suggest features
5. **Help with testing** and validation

### Development Setup

```bash
# Clone the repository
git clone https://github.com/acp-org/acp-sdk-python
cd acp-sdk-python

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check .
black .
mypy src/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Documentation**: [Coming Soon]
- **ACP Specification**: [Coming Soon]
- **A2A Protocol**: [a2a-protocol.org](https://a2a-protocol.org/)
- **Issues**: [GitHub Issues](https://github.com/acp-org/acp-sdk-python/issues)
- **Discussions**: [GitHub Discussions](https://github.com/acp-org/acp-sdk-python/discussions)

## 🙏 Acknowledgments

- Built on top of the [A2A Protocol](https://a2a-protocol.org/)
- Inspired by the need for universal commerce integration
- Community-driven development and feedback

---

**Ready to build universal commerce?** Start with the ACP SDK and join the future of agentic commerce! 🚀
