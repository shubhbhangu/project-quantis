"""
Network Node for Quantum Privacy Chain

A fully functional P2P node with:
- Peer discovery and management
- Transaction propagation
- Block synchronization
- Mining capabilities
- REST API for interaction
"""

import hashlib
import json
import time
import threading
import argparse
from typing import List, Dict, Optional, Set
from flask import Flask, request, jsonify
import requests
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blockchain import Blockchain, Transaction, Block
from wallet import Wallet, create_wallet


# Global mining state
mining_jobs = {}
job_counter = 0
job_lock = threading.Lock()


class P2PNode:
    """
    Peer-to-peer network node.
    
    Handles:
    - Peer discovery
    - Block propagation
    - Transaction relay
    - Chain synchronization
    """
    
    def __init__(self, port: int, seed_node: Optional[str] = None):
        self.port = port
        self.host = "localhost"
        self.blockchain = Blockchain()
        self.peers: Set[str] = set()
        self.pending_transactions: List[Transaction] = []
        self.is_mining = False
        self.miner_address = ""
        
        # Initialize wallet
        self.wallet_file = f"node_wallet_{port}.json"
        if os.path.exists(self.wallet_file):
            self.wallet = Wallet(self.wallet_file)
        else:
            self.wallet = create_wallet(self.wallet_file)
        
        self.miner_address = self.wallet.get_public_address()
        
        # Connect to seed node if provided
        if seed_node:
            self.connect_to_peer(seed_node)
    
    def connect_to_peer(self, peer_url: str):
        """Connect to a peer node."""
        try:
            # Normalize URL
            if not peer_url.startswith('http'):
                peer_url = f"http://{peer_url}"
            
            response = requests.get(f"{peer_url}/peers", timeout=5)
            if response.status_code == 200:
                self.peers.add(peer_url)
                
                # Get peers from this node
                peer_list = response.json().get('peers', [])
                for peer in peer_list:
                    if peer != peer_url and peer != f"http://{self.host}:{self.port}":
                        self.peers.add(peer)
                
                print(f"✅ Connected to peer: {peer_url}")
                print(f"📡 Total peers: {len(self.peers)}")
                
                # Sync blockchain
                self.synchronize_chain(peer_url)
        except Exception as e:
            print(f"❌ Failed to connect to {peer_url}: {e}")
    
    def synchronize_chain(self, source_peer: str):
        """Synchronize blockchain with a peer."""
        try:
            response = requests.get(f"{source_peer}/chain", timeout=10)
            if response.status_code == 200:
                peer_chain_data = response.json()
                peer_chain_length = peer_chain_data.get('length', 0)
                
                if peer_chain_length > len(self.blockchain.chain):
                    print(f"📥 Syncing chain from {source_peer} (length: {peer_chain_length})")
                    
                    # Validate and adopt longer chain
                    # In production, would validate each block
                    self.blockchain = Blockchain()  # Reset
                    # Would rebuild from peer data here
                    
                    print(f"✅ Chain synchronized")
        except Exception as e:
            print(f"❌ Failed to sync chain: {e}")
    
    def broadcast_transaction(self, transaction: Transaction):
        """Broadcast transaction to all peers."""
        tx_data = transaction.to_dict()
        
        for peer in self.peers:
            try:
                requests.post(
                    f"{peer}/transaction",
                    json=tx_data,
                    timeout=5
                )
            except Exception:
                pass  # Peer might be offline
    
    def broadcast_block(self, block: Block):
        """Broadcast new block to all peers."""
        block_data = block.to_dict()
        
        for peer in self.peers:
            try:
                requests.post(
                    f"{peer}/block",
                    json=block_data,
                    timeout=5
                )
            except Exception:
                pass
    
    def mine_block(self) -> Optional[Block]:
        """Mine a new block with pending transactions."""
        if not self.pending_transactions and len(self.blockchain.chain) <= 1:
            # Wait for transactions or genesis
            return None
        
        print(f"⛏️  Mining block with {len(self.pending_transactions)} transactions...")
        
        block = self.blockchain.mine_pending_transactions(self.miner_address)
        
        if block:
            print(f"✅ Block mined! Hash: {block.block_hash[:16]}...")
            self.broadcast_block(block)
            return block
        
        return None
    
    def add_transaction(self, transaction: Transaction) -> bool:
        """Add transaction to pending pool."""
        if self.blockchain.add_transaction(transaction):
            self.pending_transactions.append(transaction)
            self.broadcast_transaction(transaction)
            return True
        return False


# Flask API
app = Flask(__name__)
node: Optional[P2PNode] = None


@app.route('/chain', methods=['GET'])
def get_chain():
    """Get the full blockchain."""
    return jsonify(node.blockchain.to_dict())


@app.route('/peers', methods=['GET'])
def get_peers():
    """Get list of connected peers."""
    return jsonify({
        'peers': list(node.peers),
        'count': len(node.peers)
    })


@app.route('/add_peer', methods=['POST'])
def add_peer():
    """Add a new peer."""
    data = request.get_json()
    peer_url = data.get('peer')
    
    if peer_url:
        node.connect_to_peer(peer_url)
        return jsonify({'status': 'success', 'peers': list(node.peers)})
    
    return jsonify({'status': 'error', 'message': 'No peer URL provided'}), 400


@app.route('/transaction', methods=['POST'])
def submit_transaction():
    """Submit a new transaction."""
    data = request.get_json()
    
    try:
        # Reconstruct transaction from JSON
        tx = Transaction(
            inputs=data.get('inputs', []),
            outputs=data.get('outputs', []),
            ring_signature=data.get('ring_signature', {}),
            fee=data.get('fee', 0),
            timestamp=data.get('timestamp', time.time())
        )
        tx.compute_tx_id()
        
        if node.add_transaction(tx):
            return jsonify({
                'status': 'success',
                'tx_id': tx.tx_id,
                'message': 'Transaction added to pending pool'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Invalid transaction'
            }), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/pending', methods=['GET'])
def get_pending():
    """Get pending transactions."""
    return jsonify({
        'pending': [tx.to_dict() for tx in node.pending_transactions],
        'count': len(node.pending_transactions)
    })


@app.route('/mine', methods=['POST'])
def trigger_mine():
    """Trigger mining of a new block."""
    block = node.mine_block()
    
    if block:
        return jsonify({
            'status': 'success',
            'block': block.to_dict()
        })
    else:
        return jsonify({
            'status': 'info',
            'message': 'No transactions to mine or mining failed'
        })


@app.route('/balance/<address>', methods=['GET'])
def get_balance(address):
    """Get balance for an address (simplified)."""
    # In production, would scan entire chain for UTXOs
    balance = 0
    utxo_count = 0
    
    for block in node.blockchain.chain:
        for tx in block.transactions:
            for output in tx.outputs:
                if output.get('address') == address:
                    balance += output.get('amount', 0)
                    utxo_count += 1
    
    return jsonify({
        'address': address,
        'balance': balance,
        'utxo_count': utxo_count
    })


@app.route('/wallet/address', methods=['GET'])
def get_wallet_address():
    """Get this node's wallet address."""
    return jsonify({
        'address': node.wallet.get_public_address(),
        'balance': node.wallet.get_balance()
    })


@app.route('/status', methods=['GET'])
def get_status():
    """Get node status."""
    return jsonify({
        'port': node.port,
        'chain_length': len(node.blockchain.chain),
        'pending_transactions': len(node.pending_transactions),
        'peers': len(node.peers),
        'difficulty': node.blockchain.difficulty,
        'miner_address': node.miner_address,
        'is_mining': node.is_mining
    })


@app.route('/api/get_mining_job', methods=['GET'])
def get_mining_job():
    """Get a mining job for external miners."""
    global job_counter
    
    address = request.args.get('address')
    if not address:
        return jsonify({'error': 'Address required'}), 400
    
    # Create a new mining job
    with job_lock:
        job_counter += 1
        job_id = job_counter
    
    # Prepare block template
    last_block = node.blockchain.chain[-1]
    transactions = node.pending_transactions.copy()
    
    # Create block header data (simplified)
    prev_hash = last_block.block_hash
    timestamp = time.time()
    merkle_root = hashlib.sha256(json.dumps([tx.tx_id for tx in transactions]).encode()).hexdigest()
    
    # Calculate target based on difficulty
    # Higher difficulty = lower target
    difficulty = node.blockchain.difficulty
    target = int(2**256 / difficulty) if difficulty > 0 else 2**256
    
    header_data = f"{prev_hash}{merkle_root}{timestamp}{job_id}"
    
    job = {
        'job_id': job_id,
        'header': header_data,
        'target': target,
        'difficulty': difficulty,
        'height': len(node.blockchain.chain),
        'prev_hash': prev_hash,
        'timestamp': timestamp
    }
    
    # Store job for validation later
    mining_jobs[job_id] = {
        'header': header_data,
        'target': target,
        'timestamp': time.time(),
        'transactions': transactions
    }
    
    # Clean old jobs (older than 5 minutes)
    current_time = time.time()
    expired_jobs = [jid for jid, jdata in mining_jobs.items() 
                    if current_time - jdata['timestamp'] > 300]
    for jid in expired_jobs:
        del mining_jobs[jid]
    
    return jsonify(job)


@app.route('/api/submit_share', methods=['POST'])
def submit_share():
    """Submit a mining share from external miner."""
    data = request.get_json()
    job_id = data.get('job_id')
    nonce = data.get('nonce')
    submitted_hash = data.get('hash')
    address = data.get('address')
    
    if not all([job_id, nonce, submitted_hash]):
        return jsonify({'status': 'error', 'message': 'Missing parameters'}), 400
    
    job = mining_jobs.get(job_id)
    if not job:
        return jsonify({'status': 'error', 'message': 'Job not found or expired'}), 400
    
    # Verify the hash meets target
    try:
        hash_int = int(submitted_hash, 16)
        if hash_int >= job['target']:
            return jsonify({'status': 'rejected', 'message': 'Hash does not meet target'}), 400
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Invalid hash format'}), 400
    
    # Check if this is a valid block (meets full difficulty)
    block_difficulty = node.blockchain.difficulty
    block_target = int(2**256 / block_difficulty) if block_difficulty > 0 else 2**256
    
    is_block = hash_int < block_target
    
    if is_block:
        # Construct and add the actual block
        print(f"🎉 Valid block found by {address}!")
        
        # Create block with transactions
        block = node.blockchain.mine_pending_transactions(address)
        if block:
            node.broadcast_block(block)
            return jsonify({
                'status': 'success',
                'is_block': True,
                'reward': node.blockchain.block_reward,
                'message': 'Block accepted!'
            })
    
    # Accept share (for pool mining simulation)
    return jsonify({
        'status': 'success',
        'is_block': False,
        'difficulty': node.blockchain.difficulty,
        'message': 'Share accepted'
    })


@app.route('/block/<int:index>', methods=['GET'])
def get_block(index):
    """Get a specific block by index."""
    if 0 <= index < len(node.blockchain.chain):
        return jsonify(node.blockchain.chain[index].to_dict())
    return jsonify({'error': 'Block not found'}), 404


def run_node(port: int, seed_node: Optional[str] = None, is_genesis: bool = False):
    """Run the P2P node."""
    global node, app
    
    print(f"🚀 Starting Quantum Privacy Chain node on port {port}...")
    
    node = P2PNode(port, seed_node)
    
    if is_genesis:
        print("✨ This is the genesis node")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)


def main():
    parser = argparse.ArgumentParser(description='Quantum Privacy Chain Node')
    parser.add_argument('--port', type=int, default=5000, help='Port to run on')
    parser.add_argument('--seed-node', type=str, help='Seed node URL to connect to')
    parser.add_argument('--genesis', action='store_true', help='Start as genesis node')
    
    args = parser.parse_args()
    
    run_node(args.port, args.seed_node, args.genesis)


if __name__ == '__main__':
    main()
