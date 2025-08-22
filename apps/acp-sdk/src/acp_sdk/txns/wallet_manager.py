"""Wallet manager for the Transaction Simulator."""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from ..models.wallets import (
    AgentWallet,
    GORWallet,
    MerchantWallet,
    PublicTransactionData,
    PublicWalletData,
    PrivateWalletData,
    UserWallet,
)
from ..models.receipts import (
    AttributionReceipt,
    CreateReceiptRequest,
    PublicReceiptData,
    PrivateReceiptData,
)
from ..models.postbacks import (
    ProcessPostbackRequest,
    PublicSettlementData,
    PrivateSettlementData,
    SettlementPostback,
)
from .privacy import privacy_manager


class WalletManager:
    """Manages encrypted wallets and transaction processing."""
    
    def __init__(self):
        """Initialize wallet manager with empty wallet storage."""
        self.receipts: Dict[str, AttributionReceipt] = {}
        self.user_wallets: Dict[str, UserWallet] = {}
        self.agent_wallets: Dict[str, AgentWallet] = {}
        self.gor_wallets: Dict[str, GORWallet] = {}
        self.merchant_wallets: Dict[str, MerchantWallet] = {}
        self.transactions: Dict[str, List[PublicTransactionData]] = {}
        
        # Initialize demo wallets
        self._initialize_demo_wallets()
    
    def _initialize_demo_wallets(self):
        """Initialize demo wallets with starting balances."""
        # Demo user wallets
        self._create_user_wallet("usr_demo_001", 0.0)
        self._create_user_wallet("usr_demo_002", 0.0)
        self._create_user_wallet("usr_anonymous", 0.0)
        
        # Demo agent wallets
        self._create_agent_wallet("agt_claude_demo", 0.0)
        self._create_agent_wallet("agt_gpt_demo", 0.0)
        self._create_agent_wallet("agt_consumer_demo", 0.0)
        
        # Demo GOR operator wallets
        self._create_gor_wallet("gor_acme_demo", 0.0)
        self._create_gor_wallet("gor_toast_demo", 0.0)
        
        # Demo merchant wallets (with funding)
        self._create_merchant_wallet("toast_otto_portland", 500.0)
        self._create_merchant_wallet("toast_street_exeter", 500.0)
        self._create_merchant_wallet("toast_newicks_lobster", 500.0)
    
    def _create_user_wallet(self, user_id: str, initial_balance: float):
        """Create a new user wallet."""
        public_data = PublicWalletData(
            entity_id=user_id,
            transactions_count=0,
            last_updated=datetime.utcnow()
        )
        private_data = PrivateWalletData(
            balance=privacy_manager.encrypt_amount(initial_balance),
            total_earned=privacy_manager.encrypt_amount(0.0),
            zk_proof=privacy_manager.generate_wallet_proof({"user_id": user_id, "balance": initial_balance})
        )
        self.user_wallets[user_id] = UserWallet(
            public_data=public_data,
            private_data=private_data
        )
        self.transactions[user_id] = []
    
    def _create_agent_wallet(self, agent_id: str, initial_balance: float):
        """Create a new agent wallet."""
        public_data = PublicWalletData(
            entity_id=agent_id,
            transactions_count=0,
            last_updated=datetime.utcnow()
        )
        private_data = PrivateWalletData(
            balance=privacy_manager.encrypt_amount(initial_balance),
            total_earned=privacy_manager.encrypt_amount(0.0),
            zk_proof=privacy_manager.generate_wallet_proof({"agent_id": agent_id, "balance": initial_balance})
        )
        self.agent_wallets[agent_id] = AgentWallet(
            public_data=public_data,
            private_data=private_data
        )
        self.transactions[agent_id] = []
    
    def _create_gor_wallet(self, gor_id: str, initial_balance: float):
        """Create a new GOR operator wallet."""
        public_data = PublicWalletData(
            entity_id=gor_id,
            transactions_count=0,
            last_updated=datetime.utcnow()
        )
        private_data = PrivateWalletData(
            balance=privacy_manager.encrypt_amount(initial_balance),
            total_earned=privacy_manager.encrypt_amount(0.0),
            zk_proof=privacy_manager.generate_wallet_proof({"gor_id": gor_id, "balance": initial_balance})
        )
        self.gor_wallets[gor_id] = GORWallet(
            public_data=public_data,
            private_data=private_data
        )
        self.transactions[gor_id] = []
    
    def _create_merchant_wallet(self, merchant_id: str, initial_funding: float):
        """Create a new merchant wallet with initial funding."""
        from ..models.wallets import MerchantWalletPublicData, MerchantWalletPrivateData
        
        public_data = MerchantWalletPublicData(
            merchant_id=merchant_id,
            bounties_paid=0,
            last_updated=datetime.utcnow()
        )
        private_data = MerchantWalletPrivateData(
            balance=privacy_manager.encrypt_amount(initial_funding),
            total_funded=privacy_manager.encrypt_amount(initial_funding),
            total_spent=privacy_manager.encrypt_amount(0.0),
            zk_proof=privacy_manager.generate_wallet_proof({"merchant_id": merchant_id, "balance": initial_funding})
        )
        self.merchant_wallets[merchant_id] = MerchantWallet(
            public_data=public_data,
            private_data=private_data
        )
        self.transactions[merchant_id] = []
    
    def create_receipt(self, request: CreateReceiptRequest) -> AttributionReceipt:
        """Create an attribution receipt with privacy protection."""
        # Validate merchant has sufficient balance
        merchant_id = self._get_merchant_from_offer(request.offer_id)
        if not self._validate_merchant_balance(merchant_id, request.bounty_amount):
            raise ValueError(f"Insufficient balance in merchant wallet {merchant_id}")
        
        # Create receipt
        public_data = PublicReceiptData(
            offer_id=request.offer_id,
            order_id=request.order_id,
            agent_id=request.agent_id,
            user_id=request.user_id,
            gor_operator_id=request.gor_operator_id,
            timestamp=datetime.utcnow(),
            status="reserved"
        )
        
        # Create a serializable dict for signature generation
        signature_data = {
            "offer_id": public_data.offer_id,
            "order_id": public_data.order_id,
            "agent_id": public_data.agent_id,
            "user_id": public_data.user_id,
            "gor_operator_id": public_data.gor_operator_id,
            "timestamp": public_data.timestamp.isoformat(),
            "status": public_data.status
        }
        
        private_data = PrivateReceiptData(
            bounty_amount=privacy_manager.encrypt_amount(request.bounty_amount),
            zk_proof=privacy_manager.generate_receipt_proof({
                "offer_id": request.offer_id,
                "bounty_amount": request.bounty_amount
            }),
            signature=privacy_manager.generate_signature(signature_data)
        )
        
        receipt = AttributionReceipt(
            public_data=public_data,
            private_data=private_data
        )
        
        # Store receipt
        self.receipts[receipt.receipt_id] = receipt
        
        return receipt
    
    def process_settlement(self, request: ProcessPostbackRequest) -> SettlementPostback:
        """Process a settlement postback and update wallets."""
        # Find corresponding receipt
        receipt = self._find_receipt_by_order_id(request.order_id)
        if not receipt:
            raise ValueError(f"No receipt found for order {request.order_id}")
        
        # Calculate bounty split
        bounty_amount = privacy_manager.decrypt_amount(receipt.private_data.bounty_amount)
        split = privacy_manager.calculate_bounty_split(bounty_amount)
        
        # Update wallets atomically
        self._update_wallets(receipt, split, request)
        
        # Create settlement postback
        public_data = PublicSettlementData(
            order_id=request.order_id,
            status=request.status,
            timestamp=datetime.utcnow()
        )
        
        # Create a serializable dict for signature generation
        settlement_signature_data = {
            "order_id": public_data.order_id,
            "status": public_data.status,
            "timestamp": public_data.timestamp.isoformat()
        }
        
        private_data = PrivateSettlementData(
            order_amount=privacy_manager.encrypt_amount(request.amount.amount),
            bounty_split=privacy_manager.encrypt_bounty_split(split),
            zk_proof=privacy_manager.generate_settlement_proof({
                "order_id": request.order_id,
                "split": split
            }),
            signature=privacy_manager.generate_signature(settlement_signature_data)
        )
        
        settlement = SettlementPostback(
            public_data=public_data,
            private_data=private_data
        )
        
        return settlement
    
    def _get_merchant_from_offer(self, offer_id: str) -> str:
        """Extract merchant ID from offer ID (demo implementation)."""
        # Demo implementation - in production, this would query the GOR
        if "otto" in offer_id.lower():
            return "toast_otto_portland"
        elif "street" in offer_id.lower():
            return "toast_street_exeter"
        elif "newick" in offer_id.lower():
            return "toast_newicks_lobster"
        else:
            return "toast_otto_portland"  # Default
    
    def _validate_merchant_balance(self, merchant_id: str, bounty_amount: float) -> bool:
        """Validate merchant has sufficient balance for bounty."""
        if merchant_id not in self.merchant_wallets:
            return False
        
        wallet = self.merchant_wallets[merchant_id]
        current_balance = privacy_manager.decrypt_amount(wallet.private_data.balance)
        return current_balance >= bounty_amount
    
    def _find_receipt_by_order_id(self, order_id: str) -> Optional[AttributionReceipt]:
        """Find receipt by order ID."""
        for receipt in self.receipts.values():
            if receipt.public_data.order_id == order_id:
                return receipt
        return None
    
    def _update_wallets(self, receipt: AttributionReceipt, split: Dict[str, float], request: ProcessPostbackRequest):
        """Update all wallets atomically."""
        bounty_amount = privacy_manager.decrypt_amount(receipt.private_data.bounty_amount)
        
        # Update merchant wallet (debit bounty)
        merchant_id = self._get_merchant_from_offer(receipt.public_data.offer_id)
        self._debit_merchant_wallet(merchant_id, bounty_amount, receipt.public_data.order_id)
        
        # Update recipient wallets (credit their shares)
        self._credit_user_wallet(receipt.public_data.user_id, split["user"], receipt.public_data.order_id)
        self._credit_agent_wallet(receipt.public_data.agent_id, split["agent"], receipt.public_data.order_id)
        self._credit_gor_wallet(receipt.public_data.gor_operator_id, split["gor"], receipt.public_data.order_id)
    
    def _debit_merchant_wallet(self, merchant_id: str, amount: float, order_id: str):
        """Debit merchant wallet."""
        wallet = self.merchant_wallets[merchant_id]
        current_balance = privacy_manager.decrypt_amount(wallet.private_data.balance)
        current_spent = privacy_manager.decrypt_amount(wallet.private_data.total_spent)
        
        new_balance = current_balance - amount
        new_spent = current_spent + amount
        
        wallet.private_data.balance = privacy_manager.encrypt_amount(new_balance)
        wallet.private_data.total_spent = privacy_manager.encrypt_amount(new_spent)
        wallet.public_data.bounties_paid += 1
        wallet.public_data.last_updated = datetime.utcnow()
        wallet.private_data.zk_proof = privacy_manager.generate_wallet_proof({
            "merchant_id": merchant_id,
            "balance": new_balance
        })
        
        # Record transaction
        transaction = PublicTransactionData(
            type="bounty_debit",
            order_id=order_id,
            timestamp=datetime.utcnow()
        )
        self.transactions[merchant_id].append(transaction)
        wallet.public_data.transactions_count = len(self.transactions[merchant_id])
    
    def _credit_user_wallet(self, user_id: str, amount: float, order_id: str):
        """Credit user wallet."""
        if user_id not in self.user_wallets:
            self._create_user_wallet(user_id, 0.0)
        
        wallet = self.user_wallets[user_id]
        current_balance = privacy_manager.decrypt_amount(wallet.private_data.balance)
        current_earned = privacy_manager.decrypt_amount(wallet.private_data.total_earned)
        
        new_balance = current_balance + amount
        new_earned = current_earned + amount
        
        wallet.private_data.balance = privacy_manager.encrypt_amount(new_balance)
        wallet.private_data.total_earned = privacy_manager.encrypt_amount(new_earned)
        wallet.public_data.last_updated = datetime.utcnow()
        wallet.private_data.zk_proof = privacy_manager.generate_wallet_proof({
            "user_id": user_id,
            "balance": new_balance
        })
        
        # Record transaction
        transaction = PublicTransactionData(
            type="bounty_credit",
            order_id=order_id,
            timestamp=datetime.utcnow()
        )
        self.transactions[user_id].append(transaction)
        wallet.public_data.transactions_count = len(self.transactions[user_id])
    
    def _credit_agent_wallet(self, agent_id: str, amount: float, order_id: str):
        """Credit agent wallet."""
        if agent_id not in self.agent_wallets:
            self._create_agent_wallet(agent_id, 0.0)
        
        wallet = self.agent_wallets[agent_id]
        current_balance = privacy_manager.decrypt_amount(wallet.private_data.balance)
        current_earned = privacy_manager.decrypt_amount(wallet.private_data.total_earned)
        
        new_balance = current_balance + amount
        new_earned = current_earned + amount
        
        wallet.private_data.balance = privacy_manager.encrypt_amount(new_balance)
        wallet.private_data.total_earned = privacy_manager.encrypt_amount(new_earned)
        wallet.public_data.last_updated = datetime.utcnow()
        wallet.private_data.zk_proof = privacy_manager.generate_wallet_proof({
            "agent_id": agent_id,
            "balance": new_balance
        })
        
        # Record transaction
        transaction = PublicTransactionData(
            type="bounty_credit",
            order_id=order_id,
            timestamp=datetime.utcnow()
        )
        self.transactions[agent_id].append(transaction)
        wallet.public_data.transactions_count = len(self.transactions[agent_id])
    
    def _credit_gor_wallet(self, gor_id: str, amount: float, order_id: str):
        """Credit GOR operator wallet."""
        if gor_id not in self.gor_wallets:
            self._create_gor_wallet(gor_id, 0.0)
        
        wallet = self.gor_wallets[gor_id]
        current_balance = privacy_manager.decrypt_amount(wallet.private_data.balance)
        current_earned = privacy_manager.decrypt_amount(wallet.private_data.total_earned)
        
        new_balance = current_balance + amount
        new_earned = current_earned + amount
        
        wallet.private_data.balance = privacy_manager.encrypt_amount(new_balance)
        wallet.private_data.total_earned = privacy_manager.encrypt_amount(new_earned)
        wallet.public_data.last_updated = datetime.utcnow()
        wallet.private_data.zk_proof = privacy_manager.generate_wallet_proof({
            "gor_id": gor_id,
            "balance": new_balance
        })
        
        # Record transaction
        transaction = PublicTransactionData(
            type="bounty_credit",
            order_id=order_id,
            timestamp=datetime.utcnow()
        )
        self.transactions[gor_id].append(transaction)
        wallet.public_data.transactions_count = len(self.transactions[gor_id])
    
    def get_user_wallet(self, user_id: str) -> Optional[UserWallet]:
        """Get user wallet."""
        return self.user_wallets.get(user_id)
    
    def get_agent_wallet(self, agent_id: str) -> Optional[AgentWallet]:
        """Get agent wallet."""
        return self.agent_wallets.get(agent_id)
    
    def get_gor_wallet(self, gor_id: str) -> Optional[GORWallet]:
        """Get GOR operator wallet."""
        return self.gor_wallets.get(gor_id)
    
    def get_merchant_wallet(self, merchant_id: str) -> Optional[MerchantWallet]:
        """Get merchant wallet."""
        return self.merchant_wallets.get(merchant_id)
    
    def get_transaction_history(self, entity_id: str) -> List[PublicTransactionData]:
        """Get transaction history for an entity."""
        return self.transactions.get(entity_id, [])
    
    def get_protocol_stats(self) -> Dict:
        """Get public protocol statistics."""
        total_bounties = sum(wallet.public_data.bounties_paid for wallet in self.merchant_wallets.values())
        active_merchants = len(self.merchant_wallets)
        active_agents = len(self.agent_wallets)
        total_users = len(self.user_wallets)
        total_transactions = sum(len(transactions) for transactions in self.transactions.values())
        
        return {
            "total_bounties_paid": total_bounties,
            "active_merchants": active_merchants,
            "active_agents": active_agents,
            "total_users": total_users,
            "total_transactions": total_transactions,
            "last_updated": datetime.utcnow().isoformat()
        }


# Global wallet manager instance
wallet_manager = WalletManager()
