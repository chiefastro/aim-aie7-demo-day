# Transaction Simulator Specification - Day 5 Implementation

## Overview

The Transaction Simulator is the central hub for managing attribution receipts, settlement postbacks, and wallet operations in the Agentic Commerce Protocol (ACP) ecosystem. It handles the complete transaction lifecycle from checkout initiation to bounty distribution while maintaining privacy through encryption and zero-knowledge proofs.

## Architecture

### Core Components

1. **Transaction Simulator Service** (Port 3003)
   - FastAPI-based Python service
   - Central hub for all transaction operations
   - Handles receipts, postbacks, and wallet management

2. **Identity System** (Demo Version)
   - Simplified identity management for demo purposes
   - Extensible to full identity provider architecture

3. **Wallet/Ledger System**
   - Encrypted in-memory storage for demo (SQLite for production)
   - Private transaction history with public audit proofs
   - Multi-entity wallet management with privacy protection

## Data Models

### Attribution Receipt

Issued when checkout is initiated by restaurant agents.

```json
{
  "receipt_id": "rcpt_456",
  "public_data": {
    "offer_id": "ofr_123",
    "order_id": "ord_90210",
    "agent_id": "agt_claude_demo",
    "user_id": "usr_demo_001",
    "gor_operator_id": "gor_acme_demo",
    "timestamp": "2025-08-13T01:15:00Z",
    "status": "reserved"
  },
  "private_data": {
    "bounty_amount": "encrypted_2.50",
    "zk_proof": "proof_that_bounty_was_reserved",
    "signature": "base64-edsig..."
  }
}
```

### Settlement Postback

Received from restaurant agents after order confirmation.

```json
{
  "public_data": {
    "order_id": "ord_90210",
    "status": "success",
    "timestamp": "2025-08-13T01:17:42Z"
  },
  "private_data": {
    "order_amount": "encrypted_28.00",
    "bounty_split": {
      "user": { "user_id": "usr_demo_001", "amount": "encrypted_1.25" },
      "agent": { "agent_id": "agt_claude_demo", "amount": "encrypted_1.00" },
      "gor": { "gor_operator_id": "gor_acme_demo", "amount": "encrypted_0.25" }
    },
    "zk_proof": "proof_that_split_is_fair_and_complete",
    "signature": "base64-merchant-edsig"
  }
}
```

### Wallet Models

#### User Wallet
```json
{
  "public_data": {
    "user_id": "usr_demo_001",
    "transactions_count": 8,
    "last_updated": "2025-08-13T01:17:42Z"
  },
  "private_data": {
    "balance": "encrypted_15.75",
    "total_earned": "encrypted_25.50",
    "zk_proof": "proof_that_balance_is_accurate"
  }
}
```

#### Agent Wallet
```json
{
  "public_data": {
    "agent_id": "agt_claude_demo",
    "transactions_count": 8,
    "last_updated": "2025-08-13T01:17:42Z"
  },
  "private_data": {
    "balance": "encrypted_12.40",
    "total_earned": "encrypted_20.00",
    "zk_proof": "proof_that_balance_is_accurate"
  }
}
```

#### GOR Operator Wallet
```json
{
  "public_data": {
    "gor_operator_id": "gor_acme_demo",
    "transactions_count": 8,
    "last_updated": "2025-08-13T01:17:42Z"
  },
  "private_data": {
    "balance": "encrypted_3.10",
    "total_earned": "encrypted_5.00",
    "zk_proof": "proof_that_balance_is_accurate"
  }
}
```

#### Merchant Wallet
```json
{
  "public_data": {
    "merchant_id": "toast_otto_portland",
    "bounties_paid": 25,
    "last_updated": "2025-08-13T01:17:42Z"
  },
  "private_data": {
    "balance": "encrypted_150.25",
    "total_funded": "encrypted_500.00",
    "total_spent": "encrypted_349.75",
    "zk_proof": "proof_that_balance_is_accurate"
  }
}
```

## Bounty Split Model

### Revenue Distribution

**User (50%)**: End customer who made the purchase
- Incentivizes users to use AI agents for commerce
- Provides cashback/rewards for purchases
- Creates user adoption of agentic commerce

**Agent (40%)**: Consumer AI agent that facilitated the transaction
- Compensates the AI agent for facilitating the transaction
- Incentivizes agents to discover and present relevant offers
- Creates economic model for AI agent providers

**GOR (10%)**: Global Offer Registry operator
- Funds the GOR infrastructure
- Compensates for offer discovery, indexing, and search services
- Creates sustainable business model for ACP ecosystem

### Example Calculation

For a $2.50 bounty:
- **User**: $1.25 (50%)
- **Agent**: $1.00 (40%)
- **GOR**: $0.25 (10%)

## Privacy Architecture

### Privacy Model

The Transaction Simulator implements a privacy-aware architecture that protects sensitive financial data while maintaining protocol transparency and auditability.

#### Public Data (Protocol Transparency)
- Offer terms and bounty structures
- Transaction status and timestamps
- Aggregate statistics and protocol health
- Entity identifiers (without financial details)

#### Private Data (Encrypted)
- Wallet balances and transaction amounts
- Individual transaction details
- Personal financial information
- Merchant revenue and performance data

#### Verifiable Data (Zero-Knowledge Proofs)
- Proof that bounty was paid without revealing amount
- Proof that wallet balance is accurate without exposing balance
- Proof that fair split was applied without showing individual shares
- Audit trail verification without data exposure

### Demo Identity Architecture

#### Agent IDs
- `agt_claude_demo` - Demo Claude agent
- `agt_gpt_demo` - Demo GPT agent
- `agt_consumer_demo` - Generic consumer agent

#### User IDs
- `usr_demo_001` - Demo user 1
- `usr_demo_002` - Demo user 2
- `usr_anonymous` - Anonymous user

#### GOR Operator IDs
- `gor_acme_demo` - Demo GOR operator
- `gor_toast_demo` - Toast GOR operator

#### Merchant IDs
- `toast_otto_portland` - OTTO Portland restaurant
- `toast_street_exeter` - Street Exeter restaurant
- `toast_newicks_lobster` - Newick's Lobster House restaurant

### Production Identity Vision

#### Agent Registry
- **Purpose**: Register and verify consumer AI agents
- **Provider**: OpenAI, Anthropic, or independent registry
- **Format**: `agent://openai/claude-3.5-sonnet`
- **Verification**: Digital signatures, API keys, or blockchain-based identity

#### User Identity Providers
- **Purpose**: Authenticate and identify end users
- **Providers**: OAuth providers (Google, Apple, GitHub), crypto wallets
- **Format**: `user://google/123456789`
- **Verification**: OAuth tokens, wallet signatures

#### GOR Operator Registry
- **Purpose**: Register competing Global Offer Registry operators
- **Format**: `gor://acme-gor/instance-1`
- **Verification**: Domain ownership, SSL certificates, or blockchain identity

## API Endpoints

### Receipt Management

#### Create Attribution Receipt
```
POST /receipts
Content-Type: application/json

{
  "offer_id": "ofr_123",
  "order_id": "ord_90210",
  "agent_id": "agt_claude_demo",
  "user_id": "usr_demo_001",
  "gor_operator_id": "gor_acme_demo",
  "bounty_amount": 2.50
}
```

**Response**:
```json
{
  "receipt_id": "rcpt_456",
  "public_data": {
    "status": "created",
    "timestamp": "2025-08-13T01:15:00Z"
  },
  "private_data": {
    "bounty_reserved": "encrypted_2.50",
    "zk_proof": "proof_that_bounty_was_reserved"
  }
}
```

### Settlement Processing

#### Process Settlement Postback
```
POST /postbacks
Content-Type: application/json

{
  "order_id": "ord_90210",
  "status": "success",
  "amount": { "currency": "USD", "total": 28.00 },
  "split": {
    "user": { "user_id": "usr_demo_001", "amount": 1.25 },
    "agent": { "agent_id": "agt_claude_demo", "amount": 1.00 },
    "gor": { "gor_operator_id": "gor_acme_demo", "amount": 0.25 }
  }
}
```

**Response**:
```json
{
  "public_data": {
    "status": "processed",
    "timestamp": "2025-08-13T01:17:42Z"
  },
  "private_data": {
    "wallets_updated": ["usr_demo_001", "agt_claude_demo", "gor_acme_demo"],
    "zk_proof": "proof_that_all_wallets_were_updated_correctly"
  }
}
```

### Wallet Management

#### Get User Wallet
```
GET /wallets/users/:user_id
```

**Response**:
```json
{
  "public_data": {
    "user_id": "usr_demo_001",
    "transactions_count": 8,
    "last_updated": "2025-08-13T01:17:42Z"
  },
  "private_data": {
    "balance": "encrypted_15.75",
    "total_earned": "encrypted_25.50",
    "zk_proof": "proof_that_balance_is_accurate"
  }
}
```

#### Get Agent Wallet
```
GET /wallets/agents/:agent_id
```

#### Get GOR Operator Wallet
```
GET /wallets/gor/:gor_operator_id
```

#### Get Merchant Wallet
```
GET /wallets/merchants/:merchant_id
```

#### Get Transaction History
```
GET /wallets/users/:user_id/transactions
GET /wallets/agents/:agent_id/transactions
GET /wallets/gor/:gor_operator_id/transactions
GET /wallets/merchants/:merchant_id/transactions
```

**Response**:
```json
{
  "public_data": {
    "transactions": [
      {
        "transaction_id": "txn_789",
        "type": "bounty_credit",
        "order_id": "ord_90210",
        "timestamp": "2025-08-13T01:17:42Z"
      }
    ]
  },
  "private_data": {
    "transaction_amounts": ["encrypted_1.25"],
    "zk_proof": "proof_that_transactions_are_accurate"
  }
}
```

## Business Logic

### Transaction Flow

1. **Receipt Creation**
   - Restaurant agent calls `/receipts` during `initiate_checkout`
   - Transaction Simulator validates offer and creates receipt
   - Bounty is reserved from merchant wallet (but not yet distributed)

2. **Postback Processing**
   - Restaurant agent calls `/postbacks` after `confirm_order`
   - Transaction Simulator validates receipt and processes settlement
   - Bounty split is calculated and applied to recipient wallets
   - Merchant wallet is debited for the bounty amount

3. **Wallet Updates**
   - Merchant wallet is debited for the bounty amount
   - User wallet is credited with their share
   - Agent wallet is credited with their share
   - GOR operator wallet is credited with their share

4. **Ledger Entry**
   - Transaction is recorded in audit trail
   - Receipt and postback are correlated
   - Balance updates are logged for all wallets

### Error Handling

#### Duplicate Receipts
- Reject duplicate receipt creation for same order_id
- Return existing receipt if already created

#### Invalid Postbacks
- Validate postback against existing receipt
- Reject postbacks for non-existent orders
- Handle partial failures gracefully

#### Merchant Wallet Issues
- Validate merchant has sufficient balance for bounty
- Reject transactions if merchant wallet is insufficient
- Handle merchant wallet funding requirements

#### Wallet Errors
- Ensure atomic wallet updates across all entities
- Rollback on partial failures
- Maintain data consistency across all wallets

## Implementation Plan

### Step 1: Project Setup
```bash
cd apps/tx-simulator
# Create FastAPI project structure
# Set up dependencies (FastAPI, Pydantic, etc.)
# Create Dockerfile
```

### Step 2: Data Models
- Define Pydantic models for receipts, postbacks, wallets with privacy separation
- Implement validation and serialization for public/private data
- Add demo signature generation and ZK proof simulation (deterministic for demo)

### Step 3: Core API Endpoints
- Implement `/receipts` endpoint for attribution receipt creation
- Implement `/postbacks` endpoint for settlement processing
- Implement wallet query endpoints

### Step 4: Business Logic
- Implement bounty split calculation with privacy protection
- Create encrypted wallet management system (users, agents, GOR operators, merchants)
- Build private transaction ledger with public audit proofs
- Implement merchant wallet funding and validation
- Add ZK proof generation for transaction verification

### Step 5: Integration Testing
- Test with existing restaurant agents
- Verify end-to-end flow: receipt → postback → wallet credit
- Test error handling and edge cases

### Step 6: Demo Integration
- Update docker-compose.yml to include tx-simulator
- Wire restaurant agents to call transaction simulator
- Add wallet display to demo UI/CLI

## Technical Considerations

### Privacy & Security
- Use deterministic demo keys for consistent signatures and ZK proofs
- Document as non-production for security
- Implement signature validation and ZK proof verification framework
- Encrypt sensitive financial data while maintaining auditability

### State Management
- In-memory storage for demo simplicity
- SQLite option for persistence if needed
- Consider Redis for production scaling

### Performance
- Fast response times for demo flow
- Minimal latency for wallet queries
- Efficient transaction processing

### Security (Future)
- Production-grade encryption for wallet data
- Real zero-knowledge proof implementation
- Privacy-preserving transaction tracking
- Compliance with financial regulations
- Blockchain integration for immutability

## Success Criteria

✅ **Receipt Generation**: Successfully creates attribution receipts  
✅ **Postback Processing**: Correctly processes settlement postbacks  
✅ **Bounty Splitting**: Accurately calculates and applies splits  
✅ **Privacy Protection**: Encrypts sensitive financial data while maintaining auditability  
✅ **Wallet Management**: Maintains accurate encrypted balances and history for all entities  
✅ **Merchant Funding**: Properly manages merchant wallet funding and bounty payments  
✅ **Integration**: Seamlessly works with restaurant agents  
✅ **Demo Flow**: Complete end-to-end transaction flow operational  

## Future Enhancements

### Production Privacy System
- Real zero-knowledge proof implementation
- Production-grade encryption for all sensitive data
- Digital signatures for agent authentication
- OAuth integration for user authentication
- Domain verification for GOR operators

### Registry Services
- Agent registry API for verification
- User identity provider integration
- GOR operator registry with reputation scoring

### Scalability
- Distributed wallet storage
- Multi-currency support
- Cross-border transaction handling

### Advanced Features
- Real-time encrypted wallet balance updates
- Privacy-preserving transaction notifications
- Advanced analytics and reporting with data protection
- Multi-tenant support for competing GOR operators
- Merchant dashboard for bounty management (private data)
- Automated merchant wallet funding alerts
- Bounty performance analytics for merchants (aggregate only)
- Zero-knowledge proof verification tools
