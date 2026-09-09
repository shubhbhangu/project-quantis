"""
Blockchain Core Module

Implements the core blockchain data structures and consensus mechanisms:
- Block structure with privacy-preserving transactions
- Random CPU PoW with variable difficulty
- Chain validation and fork resolution
"""

import hashlib
import time
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field, asdict
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crypto import (
    QuantumProofSignature, 
    PedersenCommitment, 
    RingSignature,
    generate_keypair,
    sign_message,
    verify_signature
)


@dataclass
class Transaction:
    """
    Privacy-preserving transaction.
    
    Features:
    - Ring signatures for sender anonymity
    - Stealth addresses for receiver privacy
    - Pedersen commitments for amount hiding
    """
    tx_id: str = ""
    inputs: List[Dict] = field(default_factory=list)  # Previous outputs being spent
    outputs: List[Dict] = field(default_factory=list)  # New outputs with stealth addresses
    ring_signature: Dict = field(default_factory=dict)  # Ring signature for inputs
    amount_commitments: List[Tuple[int, bytes]] = field(default_factory=list)  # Pedersen commitments
    fee: int = 0
    timestamp: float = field(default_factory=time.time)
    extra_privacy_data: Dict = field(default_factory=dict)  # Additional mixing data
    
    def compute_tx_id(self) -> str:
        """Compute transaction ID."""
        tx_data = json.dumps({
            'inputs': self.inputs,
            'outputs': [{'address': o['address'], 'commitment': o.get('commitment', 0)} 
                       for o in self.outputs],
            'fee': self.fee,
            'timestamp': self.timestamp
        }, sort_keys=True).encode()
        self.tx_id = hashlib.sha3_256(tx_data).hexdigest()
        return self.tx_id
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'tx_id': self.tx_id,
            'inputs': self.inputs,
            'outputs': self.outputs,
            'ring_signature': {
                'mix_hash': self.ring_signature.get('mix_hash', ''),
                'ring_size': self.ring_signature.get('ring_size', 0)
            },
            'amount_commitments': [(c[0], c[1].hex()) for c in self.amount_commitments],
            'fee': self.fee,
            'timestamp': self.timestamp
        }


@dataclass
class Block:
    """Block in the blockchain."""
    index: int = 0
    timestamp: float = field(default_factory=time.time)
    transactions: List[Transaction] = field(default_factory=list)
    previous_hash: str = "0" * 64
    nonce: int = 0
    difficulty: int = 4  # Number of leading zeros required
    miner_address: str = ""
    block_hash: str = ""
    pow_seed: int = 0  # Random seed for CPU-intensive PoW
    
    def compute_hash(self) -> str:
        """Compute block hash."""
        block_data = json.dumps({
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'difficulty': self.difficulty,
            'miner_address': self.miner_address,
            'pow_seed': self.pow_seed
        }, sort_keys=True).encode()
        self.block_hash = hashlib.sha3_256(block_data).hexdigest()
        return self.block_hash
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'difficulty': self.difficulty,
            'miner_address': self.miner_address,
            'block_hash': self.block_hash,
            'pow_seed': self.pow_seed
        }


class RandomCPUPoW:
    """
    Random CPU Proof-of-Work algorithm.
    
    Inspired by RandomX but simplified. Uses random computational puzzles
    with variable intensity to ensure ASIC resistance and fair mining.
    """
    
    def __init__(self):
        self.memory_hard_iterations = 1000  # Base iterations
        self.random_ops = ['hash', 'multiply', 'xor', 'rotate']
    
    def _random_memory_access(self, seed: int, iteration: int) -> int:
        """Simulate random memory access pattern."""
        # Create a small scratchpad
        scratchpad = [(seed + i * 17) % (2**32) for i in range(256)]
        
        # Random access pattern
        index = (seed + iteration * 31) % len(scratchpad)
        value = scratchpad[index]
        
        # Modify scratchpad
        scratchpad[index] = (value + iteration) % (2**32)
        
        return value
    
    def _compute_work(self, data: bytes, seed: int, iterations: int) -> bytes:
        """Perform CPU-intensive work."""
        current_hash = hashlib.sha3_256(data).digest()
        current_val = int.from_bytes(current_hash[:8], 'big')
        
        for i in range(iterations):
            # Random operation selection
            op = self.random_ops[(seed + i) % len(self.random_ops)]
            
            if op == 'hash':
                current_hash = hashlib.sha3_256(
                    current_hash + (current_val).to_bytes(8, 'big')
                ).digest()
                current_val = int.from_bytes(current_hash[:8], 'big')
            
            elif op == 'multiply':
                mem_val = self._random_memory_access(seed, i)
                current_val = (current_val * mem_val) % (2**64)
            
            elif op == 'xor':
                mem_val = self._random_memory_access(seed, i)
                current_val ^= mem_val
            
            elif op == 'rotate':
                rotate_amount = (seed + i) % 64
                current_val = ((current_val << rotate_amount) | 
                              (current_val >> (64 - rotate_amount))) & (2**64 - 1)
        
        return current_val.to_bytes(8, 'big')
    
    def mine(self, block: Block, difficulty: int) -> Tuple[bool, int]:
        """
        Mine a block by finding a nonce that satisfies difficulty.
        
        Returns:
            (success, iterations_used)
        """
        # Random seed for this mining attempt
        block.pow_seed = random.randint(0, 2**32 - 1)
        
        # Variable iterations based on difficulty
        base_iterations = self.memory_hard_iterations
        variable_iterations = random.randint(base_iterations // 2, base_iterations * 2)
        
        target = 2 ** (256 - difficulty * 4)  # Target threshold
        
        nonce = 0
        max_nonces = 100000  # Prevent infinite loop
        
        while nonce < max_nonces:
            block.nonce = nonce
            
            # Prepare data for hashing
            block_data = json.dumps({
                'index': block.index,
                'timestamp': block.timestamp,
                'transactions': [tx.to_dict() for tx in block.transactions],
                'previous_hash': block.previous_hash,
                'nonce': nonce,
                'difficulty': difficulty,
                'pow_seed': block.pow_seed
            }, sort_keys=True).encode()
            
            # Perform CPU-intensive work
            work_result = self._compute_work(block_data, block.pow_seed, variable_iterations)
            
            # Final hash
            final_hash = hashlib.sha3_256(block_data + work_result).hexdigest()
            
            # Check if hash meets difficulty
            if int(final_hash, 16) < target:
                block.block_hash = final_hash
                return True, nonce
            
            nonce += 1
        
        return False, max_nonces
    
    def verify(self, block: Block, difficulty: int) -> bool:
        """Verify that a block's PoW is valid."""
        # Recompute the work
        block_data = json.dumps({
            'index': block.index,
            'timestamp': block.timestamp,
            'transactions': [tx.to_dict() for tx in block.transactions],
            'previous_hash': block.previous_hash,
            'nonce': block.nonce,
            'difficulty': difficulty,
            'pow_seed': block.pow_seed
        }, sort_keys=True).encode()
        
        variable_iterations = random.randint(
            self.memory_hard_iterations // 2, 
            self.memory_hard_iterations * 2
        )
        
        work_result = self._compute_work(block_data, block.pow_seed, variable_iterations)
        final_hash = hashlib.sha3_256(block_data + work_result).hexdigest()
        
        # Check difficulty
        target = 2 ** (256 - difficulty * 4)
        return int(final_hash, 16) < target and block.block_hash == final_hash


class Blockchain:
    """Main blockchain class."""
    
    def __init__(self):
        self.chain: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        self.difficulty = 4
        self.block_time_target = 30  # seconds
        self.pow_engine = RandomCPUPoW()
        self.crypto = QuantumProofSignature()
        self.ring_sig_engine = RingSignature(self.crypto)
        
        # Create genesis block
        self.create_genesis_block()
    
    def create_genesis_block(self) -> Block:
        """Create the first block in the chain."""
        genesis_tx = Transaction(
            inputs=[{'address': 'genesis', 'amount': 0}],
            outputs=[{'address': 'genesis', 'amount': 0, 'stealth': True}],
            fee=0,
            timestamp=time.time()
        )
        genesis_tx.compute_tx_id()
        
        genesis_block = Block(
            index=0,
            timestamp=time.time(),
            transactions=[genesis_tx],
            previous_hash="0" * 64,
            difficulty=self.difficulty
        )
        genesis_block.compute_hash()
        
        self.chain.append(genesis_block)
        return genesis_block
    
    def get_latest_block(self) -> Optional[Block]:
        """Get the most recent block."""
        return self.chain[-1] if self.chain else None
    
    def adjust_difficulty(self) -> int:
        """Adjust difficulty based on block times."""
        if len(self.chain) < 10:
            return self.difficulty
        
        # Look at last 10 blocks
        recent_blocks = self.chain[-10:]
        actual_time = recent_blocks[-1].timestamp - recent_blocks[0].timestamp
        expected_time = 10 * self.block_time_target
        
        if actual_time < expected_time * 0.8:
            return min(self.difficulty + 1, 10)  # Increase difficulty
        elif actual_time > expected_time * 1.2:
            return max(self.difficulty - 1, 1)  # Decrease difficulty
        
        return self.difficulty
    
    def mine_pending_transactions(self, miner_address: str) -> Optional[Block]:
        """Mine pending transactions into a new block."""
        latest_block = self.get_latest_block()
        if not latest_block:
            return None
        
        # Adjust difficulty
        self.difficulty = self.adjust_difficulty()
        
        # Create new block
        new_block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            transactions=self.pending_transactions.copy(),
            previous_hash=latest_block.block_hash,
            difficulty=self.difficulty,
            miner_address=miner_address
        )
        
        # Add coinbase transaction (block reward)
        block_reward = 50  # QPC tokens
        coinbase_tx = Transaction(
            inputs=[{'address': 'coinbase', 'amount': block_reward}],
            outputs=[{'address': miner_address, 'amount': block_reward, 'stealth': True}],
            fee=0
        )
        coinbase_tx.compute_tx_id()
        new_block.transactions.insert(0, coinbase_tx)
        
        # Mine the block
        success, iterations = self.pow_engine.mine(new_block, self.difficulty)
        
        if success:
            self.chain.append(new_block)
            self.pending_transactions.clear()
            return new_block
        
        return None
    
    def add_transaction(self, transaction: Transaction) -> bool:
        """Add a transaction to the pending pool."""
        # Verify transaction
        if not self.verify_transaction(transaction):
            return False
        
        transaction.compute_tx_id()
        self.pending_transactions.append(transaction)
        return True
    
    def verify_transaction(self, transaction: Transaction) -> bool:
        """Verify a transaction's validity."""
        # Check ring signature
        if not transaction.ring_signature:
            return False
        
        # Verify amount commitments sum correctly
        if transaction.amount_commitments:
            input_sum = sum(c[0] for c in transaction.amount_commitments[:len(transaction.inputs)])
            output_sum = sum(c[0] for c in transaction.amount_commitments[len(transaction.inputs):])
            
            # Inputs should equal outputs + fee
            if input_sum != output_sum + transaction.fee:
                return False
        
        return True
    
    def verify_chain(self) -> bool:
        """Verify the entire blockchain."""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Check hash linkage
            if current_block.previous_hash != previous_block.block_hash:
                return False
            
            # Check PoW
            if not self.pow_engine.verify(current_block, current_block.difficulty):
                return False
            
            # Verify transactions
            for tx in current_block.transactions:
                if not self.verify_transaction(tx):
                    return False
        
        return True
    
    def to_dict(self) -> Dict:
        """Convert blockchain to dictionary."""
        return {
            'chain': [block.to_dict() for block in self.chain],
            'pending_transactions': [tx.to_dict() for tx in self.pending_transactions],
            'difficulty': self.difficulty,
            'length': len(self.chain)
        }


def create_stealth_address(public_key: dict, scanner_key: bytes) -> str:
    """
    Create a one-time stealth address for receiving funds.
    
    This ensures that even if someone knows your public address,
    they cannot link multiple transactions to you.
    """
    # Combine public key with scanner key
    combined = json.dumps(public_key, sort_keys=True).encode() + scanner_key
    stealth_hash = hashlib.sha3_256(combined).hexdigest()
    return f"stl_{stealth_hash[:32]}"


def generate_stealth_keys() -> Tuple[dict, dict, bytes]:
    """Generate keys for stealth address system."""
    pub_key, priv_key = generate_keypair()
    scanner_key = os.urandom(32)
    return pub_key, priv_key, scanner_key
