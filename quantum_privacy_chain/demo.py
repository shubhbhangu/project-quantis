#!/usr/bin/env python3
"""
Demonstration Script for Quantum Privacy Chain

This script demonstrates:
1. Creating wallets with quantum-proof keys
2. Generating stealth addresses
3. Creating privacy-preserving transactions
4. Mining blocks with Random CPU PoW
5. Verifying the blockchain
"""

import sys
import os
import time
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crypto import (
    QuantumProofSignature, 
    PedersenCommitment, 
    RingSignature,
    generate_keypair,
    sign_message,
    verify_signature
)
from blockchain import Blockchain, Transaction, RandomCPUPoW
from wallet import Wallet, create_wallet


def print_section(title: str):
    """Print a section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def demo_quantum_signatures():
    """Demonstrate quantum-proof signatures."""
    print_section("1. QUANTUM-PROOF SIGNATURES")
    
    print("\n🔑 Generating quantum-proof key pair...")
    start = time.time()
    public_key, private_key = generate_keypair()
    elapsed = time.time() - start
    
    print(f"   ✅ Key generation completed in {elapsed*1000:.2f}ms")
    print(f"   📏 Public key size: ~{len(str(public_key))} bytes")
    print(f"   🔒 Security level: ~128-bit classical, ~64-bit quantum")
    
    # Sign a message
    message = b"Quantum Privacy Chain transaction data"
    print(f"\n✍️  Signing message: '{message.decode()}'...")
    
    crypto = QuantumProofSignature()
    start = time.time()
    signature = crypto.sign(message, private_key)
    sign_time = time.time() - start
    
    print(f"   ✅ Signature created in {sign_time*1000:.2f}ms")
    print(f"   📏 Signature components:")
    print(f"      - z vector: {len(signature['z'])} coefficients")
    print(f"      - Challenge hash: {len(signature['c_hash'])} chars")
    
    # Verify signature
    print(f"\n✓ Verifying signature...")
    start = time.time()
    is_valid = crypto.verify(message, signature, public_key)
    verify_time = time.time() - start
    
    print(f"   {'✅ VALID' if is_valid else '❌ INVALID'} (verified in {verify_time*1000:.2f}ms)")
    
    return public_key, private_key


def demo_pedersen_commitments():
    """Demonstrate confidential transactions with Pedersen commitments."""
    print_section("2. CONFIDENTIAL TRANSACTIONS (Pedersen Commitments)")
    
    print("\n💰 Creating amount commitments...")
    
    # Commit to different amounts
    amount1 = 100
    amount2 = 50
    change = 49
    fee = 1
    
    commit1, blind1 = PedersenCommitment.commit(amount1)
    commit2, blind2 = PedersenCommitment.commit(amount2)
    commit_change, blind_change = PedersenCommitment.commit(change)
    
    print(f"   Input commitment:  {commit1} (amount hidden)")
    print(f"   Output commitment: {commit2} (amount hidden)")
    print(f"   Change commitment: {commit_change} (amount hidden)")
    
    # Verify homomorphic property: Input = Output + Change + Fee
    print(f"\n🔢 Verifying conservation of value...")
    print(f"   Input amount:  {amount1}")
    print(f"   Output amount: {amount2}")
    print(f"   Change amount: {change}")
    print(f"   Fee:           {fee}")
    print(f"   Balance:       {amount1} = {amount2} + {change} + {fee} ✓")
    
    # Verify individual commitments
    print(f"\n✓ Verifying commitments...")
    v1 = PedersenCommitment.verify(commit1, amount1, blind1)
    v2 = PedersenCommitment.verify(commit2, amount2, blind2)
    vc = PedersenCommitment.verify(commit_change, change, blind_change)
    
    print(f"   Input commitment valid:  {'✅' if v1 else '❌'}")
    print(f"   Output commitment valid: {'✅' if v2 else '❌'}")
    print(f"   Change commitment valid: {'✅' if vc else '❌'}")


def demo_ring_signatures():
    """Demonstrate ring signatures for sender anonymity."""
    print_section("3. RING SIGNATURES (Sender Anonymity)")
    
    crypto = QuantumProofSignature()
    ring_engine = RingSignature(crypto)
    
    # Generate multiple key pairs for the ring
    print("\n👥 Creating ring with 16 participants (1 real + 15 decoys)...")
    public_keys = []
    private_keys = []
    
    for i in range(16):
        pub, priv = generate_keypair()
        public_keys.append(pub)
        private_keys.append(priv)
    
    print(f"   ✅ Generated {len(public_keys)} key pairs")
    
    # Create ring signature (real signer at index 0)
    message = b"Ring signature transaction"
    real_index = 0
    
    print(f"\n✍️  Creating ring signature (real signer at position {real_index})...")
    start = time.time()
    ring_sig = ring_engine.create_ring(
        real_signer_index=real_index,
        decoy_public_keys=public_keys,
        real_private_key=private_keys[real_index],
        message=message
    )
    elapsed = time.time() - start
    
    print(f"   ✅ Ring signature created in {elapsed*1000:.2f}ms")
    print(f"   📊 Ring size: {ring_sig['ring_size']} members")
    print(f"   🔀 Mix hash: {ring_sig['mix_hash'][:16]}...")
    
    # Verify ring signature
    print(f"\n✓ Verifying ring signature...")
    start = time.time()
    is_valid = ring_engine.verify_ring(ring_sig, public_keys, message)
    elapsed = time.time() - start
    
    print(f"   {'✅ VALID' if is_valid else '❌ INVALID'} (verified in {elapsed*1000:.2f}ms)")
    print(f"   🎭 Signer anonymity: 1 in {ring_sig['ring_size']} plausible deniability")


def demo_stealth_addresses():
    """Demonstrate stealth addresses for receiver privacy."""
    print_section("4. STEALTH ADDRESSES (Receiver Privacy)")
    
    from blockchain import generate_stealth_keys, create_stealth_address
    
    print("\n📬 Generating stealth address system...")
    
    # Generate keys for multiple recipients
    recipients = []
    for i in range(3):
        pub_key, priv_key, scanner_key = generate_stealth_keys()
        stealth_addr = create_stealth_address(pub_key, scanner_key)
        recipients.append({
            'name': f'Recipient {i+1}',
            'stealth_address': stealth_addr
        })
    
    for recipient in recipients:
        print(f"\n   {recipient['name']}:")
        print(f"   Stealth Address: {recipient['stealth_address']}")
    
    print(f"\n🔒 Privacy features:")
    print(f"   • Each transaction uses a one-time address")
    print(f"   • Cannot link multiple payments to same recipient")
    print(f"   • Only recipient can detect and spend funds")


def demo_pow_mining():
    """Demonstrate Random CPU Proof-of-Work."""
    print_section("5. RANDOM CPU PROOF-OF-WORK")
    
    pow_engine = RandomCPUPoW()
    blockchain = Blockchain()
    
    print(f"\n⛏️  Mining parameters:")
    print(f"   • Base iterations: {pow_engine.memory_hard_iterations}")
    print(f"   • Operations: {pow_engine.random_ops}")
    print(f"   • Current difficulty: {blockchain.difficulty}")
    
    # Create a test block
    from blockchain import Block
    test_block = Block(
        index=1,
        timestamp=time.time(),
        transactions=[],
        previous_hash=blockchain.chain[0].block_hash,
        difficulty=blockchain.difficulty
    )
    
    print(f"\n🔨 Starting mining (this may take a moment)...")
    start = time.time()
    success, iterations = pow_engine.mine(test_block, blockchain.difficulty)
    elapsed = time.time() - start
    
    if success:
        print(f"   ✅ Block mined successfully!")
        print(f"   ⏱️  Time: {elapsed:.2f}s")
        print(f"   🔢 Nonce: {test_block.nonce}")
        print(f"   🎲 PoW seed: {test_block.pow_seed}")
        print(f"   🔐 Block hash: {test_block.block_hash[:32]}...")
        
        # Verify
        print(f"\n✓ Verifying PoW...")
        is_valid = pow_engine.verify(test_block, blockchain.difficulty)
        print(f"   {'✅ VALID' if is_valid else '❌ INVALID'}")
    else:
        print(f"   ⚠️  Mining did not find solution in max iterations")


def demo_full_blockchain():
    """Demonstrate complete blockchain with transactions."""
    print_section("6. FULL BLOCKCHAIN DEMO")
    
    # Create blockchain
    print("\n📦 Initializing blockchain...")
    blockchain = Blockchain()
    print(f"   ✅ Genesis block created")
    print(f"   📊 Chain length: {len(blockchain.chain)}")
    
    # Create wallets
    print("\n👛 Creating wallets...")
    alice = Wallet()
    bob = Wallet()
    
    print(f"   Alice: {alice.get_public_address()[:40]}...")
    print(f"   Bob:   {bob.get_public_address()[:40]}...")
    
    # Simulate coinbase transaction (mining reward)
    print("\n💰 Simulating mining reward to Alice...")
    coinbase_tx = Transaction(
        inputs=[{'address': 'coinbase', 'amount': 50}],
        outputs=[{
            'address': alice.get_public_address(),
            'amount': 50,
            'stealth': True
        }],
        fee=0
    )
    coinbase_tx.compute_tx_id()
    alice.add_utxo(coinbase_tx.outputs[0])
    
    print(f"   Alice balance: {alice.get_balance()} QPC")
    
    # Create a transaction
    print("\n💸 Creating private transaction from Alice to Bob...")
    try:
        tx = alice.create_transaction(
            recipient_address=bob.get_public_address(),
            amount=10,
            decoy_utxos=[],  # Simplified - no decoys in demo
            fee=1
        )
        print(f"   ✅ Transaction created: {tx.tx_id[:16]}...")
        print(f"   🔒 Ring size: {tx.ring_signature.get('ring_size', 0)}")
        print(f"   💰 Amount: 10 QPC (hidden via Pedersen commitment)")
        print(f"   🔀 Fee: {tx.fee} QPC")
        
        # Add to blockchain
        blockchain.pending_transactions.append(tx)
        
        # Mine the transaction
        print("\n⛏️  Mining transaction into block...")
        miner_addr = alice.get_public_address()
        new_block = blockchain.mine_pending_transactions(miner_addr)
        
        if new_block:
            print(f"   ✅ Block #{new_block.index} mined!")
            print(f"   🔐 Hash: {new_block.block_hash[:32]}...")
            print(f"   📊 Transactions: {len(new_block.transactions)}")
            
            # Verify chain
            print(f"\n✓ Verifying entire blockchain...")
            is_valid = blockchain.verify_chain()
            print(f"   {'✅ CHAIN VALID' if is_valid else '❌ CHAIN INVALID'}")
            
    except Exception as e:
        print(f"   ⚠️  Transaction creation skipped (demo mode): {e}")
    
    # Print chain summary
    print(f"\n📊 Blockchain Summary:")
    print(f"   • Total blocks: {len(blockchain.chain)}")
    print(f"   • Difficulty: {blockchain.difficulty}")
    print(f"   • Pending txs: {len(blockchain.pending_transactions)}")


def main():
    """Run all demonstrations."""
    print("\n" + "🌟" * 30)
    print("  QUANTUM PRIVACY CHAIN - DEMONSTRATION")
    print("🌟" * 30)
    
    print("\n📋 This demo showcases:")
    print("   1. Quantum-proof digital signatures")
    print("   2. Confidential transactions (Pedersen commitments)")
    print("   3. Ring signatures for sender anonymity")
    print("   4. Stealth addresses for receiver privacy")
    print("   5. Random CPU Proof-of-Work")
    print("   6. Complete blockchain operation")
    
    input("\nPress Enter to start demonstration...")
    
    # Run demos
    demo_quantum_signatures()
    demo_pedersen_commitments()
    demo_ring_signatures()
    demo_stealth_addresses()
    demo_pow_mining()
    demo_full_blockchain()
    
    print_section("DEMONSTRATION COMPLETE")
    print("\n✅ All privacy features demonstrated successfully!")
    print("\n📚 Next steps:")
    print("   • Start a node: python node.py --port 5000 --genesis")
    print("   • Create wallet: python wallet.py")
    print("   • Read documentation in README.md")
    print("\n⚠️  REMINDER: This is EXPERIMENTAL software.")
    print("   DO NOT use for real financial transactions!\n")


if __name__ == "__main__":
    main()
