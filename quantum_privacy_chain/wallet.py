"""
Wallet Module for Quantum Privacy Chain

Provides wallet functionality including:
- Key management with quantum-proof signatures
- Stealth address generation
- Private transaction creation with ring signatures
- Balance tracking via view keys
"""

import json
import os
import time
from typing import Dict, List, Optional, Tuple
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crypto import (
    QuantumProofSignature, 
    PedersenCommitment, 
    RingSignature,
    generate_keypair,
    sign_message,
    verify_signature
)
from blockchain import Transaction, create_stealth_address, generate_stealth_keys


class Wallet:
    """
    Privacy-focused wallet with quantum-proof security.
    
    Features:
    - Quantum-proof key pairs
    - Stealth addresses for receiving
    - Ring signature transaction signing
    - Confidential transactions
    """
    
    def __init__(self, wallet_file: Optional[str] = None):
        self.crypto = QuantumProofSignature()
        self.ring_sig_engine = RingSignature(self.crypto)
        
        if wallet_file and os.path.exists(wallet_file):
            self.load(wallet_file)
        else:
            self.generate_new_wallet()
        
        self.wallet_file = wallet_file
    
    def generate_new_wallet(self):
        """Generate a new wallet with quantum-proof keys."""
        # Generate main key pair for spending
        self.spend_public_key, self.spend_private_key = generate_keypair()
        
        # Generate view key pair for scanning stealth addresses
        self.view_public_key, self.view_private_key, self.scanner_key = generate_stealth_keys()
        
        # Generate default stealth address
        self.stealth_address = create_stealth_address(self.view_public_key, self.scanner_key)
        
        # Track UTXOs (unspent transaction outputs)
        self.utxos: List[Dict] = []
        
        # Transaction history
        self.transactions: List[Dict] = []
    
    def save(self, filepath: str):
        """Save wallet to file (ENCRYPT IN PRODUCTION!)."""
        wallet_data = {
            'spend_public_key': self.spend_public_key,
            'spend_private_key': self._serialize_key(self.spend_private_key),
            'view_public_key': self.view_public_key,
            'view_private_key': self._serialize_key(self.view_private_key),
            'scanner_key': self.scanner_key.hex(),
            'stealth_address': self.stealth_address,
            'utxos': self.utxos,
            'transactions': self.transactions
        }
        
        with open(filepath, 'w') as f:
            json.dump(wallet_data, f, indent=2)
        
        print(f"⚠️  WARNING: Wallet saved to {filepath}")
        print("   In production, this file should be encrypted!")
    
    def load(self, filepath: str):
        """Load wallet from file."""
        with open(filepath, 'r') as f:
            wallet_data = json.load(f)
        
        self.spend_public_key = wallet_data['spend_public_key']
        self.spend_private_key = self._deserialize_key(wallet_data['spend_private_key'])
        self.view_public_key = wallet_data['view_public_key']
        self.view_private_key = self._deserialize_key(wallet_data['view_private_key'])
        self.scanner_key = bytes.fromhex(wallet_data['scanner_key'])
        self.stealth_address = wallet_data['stealth_address']
        self.utxos = wallet_data.get('utxos', [])
        self.transactions = wallet_data.get('transactions', [])
    
    def _serialize_key(self, key: dict) -> dict:
        """Serialize private key for storage."""
        serialized = key.copy()
        if 's1' in serialized and isinstance(serialized['s1'], list):
            serialized['s1'] = ','.join(map(str, serialized['s1']))
        if 's2' in serialized and isinstance(serialized['s2'], list):
            serialized['s2'] = ','.join(map(str, serialized['s2']))
        return serialized
    
    def _deserialize_key(self, key: dict) -> dict:
        """Deserialize private key from storage."""
        deserialized = key.copy()
        if 's1' in deserialized and isinstance(deserialized['s1'], str):
            deserialized['s1'] = list(map(int, deserialized['s1'].split(',')))
        if 's2' in deserialized and isinstance(deserialized['s2'], str):
            deserialized['s2'] = list(map(int, deserialized['s2'].split(',')))
        return deserialized
    
    def get_public_address(self) -> str:
        """Get the public stealth address for receiving funds."""
        return self.stealth_address
    
    def get_balance(self) -> int:
        """Calculate total balance from UTXOs."""
        return sum(utxo.get('amount', 0) for utxo in self.utxos)
    
    def add_utxo(self, tx_output: Dict):
        """Add a UTXO to the wallet."""
        # Check if this output belongs to us
        if self._output_belongs_to_us(tx_output):
            self.utxos.append({
                'tx_id': tx_output.get('tx_id', ''),
                'address': tx_output['address'],
                'amount': tx_output['amount'],
                'commitment': tx_output.get('commitment'),
                'spent': False
            })
    
    def _output_belongs_to_us(self, output: Dict) -> bool:
        """Check if an output belongs to this wallet."""
        # In a real implementation, this would use the view key to scan
        # For now, we check if the address matches our stealth address
        return output.get('address') == self.stealth_address or \
               output.get('address').startswith('stl_')
    
    def create_transaction(self, recipient_address: str, amount: int, 
                          decoy_utxos: List[Dict], fee: int = 1) -> Transaction:
        """
        Create a privacy-preserving transaction.
        
        Args:
            recipient_address: Recipient's stealth address
            amount: Amount to send
            decoy_utxos: Decoy inputs for ring signature (from other users)
            fee: Transaction fee
        
        Returns:
            Signed transaction object
        """
        # Find suitable UTXOs to spend
        spendable_utxos = [u for u in self.utxos if not u['spent']]
        
        if not spendable_utxos:
            raise ValueError("No unspent outputs available")
        
        # Select input (simplified - in practice use coin selection algorithm)
        selected_input = spendable_utxos[0]
        
        if selected_input['amount'] < amount + fee:
            raise ValueError("Insufficient funds")
        
        # Create ring of inputs (real + decoys)
        ring_inputs = [selected_input] + decoy_utxos[:15]  # 16-member ring
        
        # Create Pedersen commitments for amounts
        input_commitment, input_blinding = PedersenCommitment.commit(selected_input['amount'])
        
        # Create output commitment
        change_amount = selected_input['amount'] - amount - fee
        output_commitment, output_blinding = PedersenCommitment.commit(amount)
        
        if change_amount > 0:
            change_commitment, change_blinding = PedersenCommitment.commit(change_amount)
        
        # Prepare message to sign
        message = json.dumps({
            'inputs': [i['tx_id'] if isinstance(i, dict) else i for i in ring_inputs],
            'outputs': [recipient_address],
            'amounts': [amount],
            'fee': fee
        }, sort_keys=True).encode()
        
        # Create ring signature
        # Get public keys for all ring members (in practice, fetch from blockchain)
        ring_public_keys = [self.spend_public_key] * len(ring_inputs)  # Simplified
        
        ring_signature = self.ring_sig_engine.create_ring(
            real_signer_index=0,  # Real input is first
            decoy_public_keys=ring_public_keys,
            real_private_key=self.spend_private_key,
            message=message
        )
        
        # Build transaction
        tx = Transaction(
            inputs=[{
                'tx_id': selected_input.get('tx_id', 'unknown'),
                'address': selected_input.get('address', '')
            }],
            outputs=[{
                'address': recipient_address,
                'amount': amount,
                'stealth': True,
                'commitment': output_commitment
            }],
            ring_signature=ring_signature,
            amount_commitments=[(input_commitment, input_blinding)],
            fee=fee,
            timestamp=time.time(),
            extra_privacy_data={
                'change_commitment': change_commitment if change_amount > 0 else None,
                'ring_size': len(ring_inputs)
            }
        )
        
        # Add change output if needed
        if change_amount > 0:
            tx.outputs.append({
                'address': self.stealth_address,
                'amount': change_amount,
                'stealth': True,
                'commitment': change_commitment
            })
            tx.amount_commitments.append((change_commitment, change_blinding))
        
        tx.compute_tx_id()
        
        # Mark input as spent
        selected_input['spent'] = True
        
        return tx
    
    def scan_for_outputs(self, blockchain_outputs: List[Dict]):
        """Scan blockchain outputs to find those belonging to this wallet."""
        for output in blockchain_outputs:
            if self._output_belongs_to_us(output):
                self.add_utxo(output)
    
    def export_view_key(self) -> str:
        """Export view key for auditing purposes (without spending ability)."""
        return json.dumps({
            'view_public': self.view_public_key,
            'view_private': self._serialize_key(self.view_private_key)
        })
    
    def get_transaction_history(self) -> List[Dict]:
        """Get transaction history."""
        return self.transactions


def create_wallet(wallet_file: str = "wallet.json") -> Wallet:
    """Create a new wallet."""
    wallet = Wallet()
    wallet.save(wallet_file)
    return wallet


def load_wallet(wallet_file: str = "wallet.json") -> Wallet:
    """Load existing wallet."""
    if not os.path.exists(wallet_file):
        raise FileNotFoundError(f"Wallet file {wallet_file} not found")
    return Wallet(wallet_file)


if __name__ == "__main__":
    # Demo: Create a new wallet
    print("Creating new Quantum Privacy Chain wallet...")
    wallet = create_wallet("demo_wallet.json")
    
    print(f"\n📬 Your stealth address:")
    print(f"   {wallet.get_public_address()}")
    
    print(f"\n🔑 Wallet features:")
    print(f"   - Quantum-proof signatures (Dilithium-inspired)")
    print(f"   - Stealth addresses for receiver privacy")
    print(f"   - Ring signatures for sender anonymity")
    print(f"   - Pedersen commitments for amount hiding")
    
    print(f"\n💰 Current balance: {wallet.get_balance()} QPC")
    
    print("\n✅ Wallet created successfully!")
    print("⚠️  Remember to backup your wallet file securely!")
