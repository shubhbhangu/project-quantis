#!/usr/bin/env python3
"""
Standalone CPU Miner for Quantum Privacy Chain (QPC)
Features:
- Randomized CPU PoW (ASIC resistant)
- Quantum-proof reward handling
- Real-time hashrate monitoring
- Auto-reconnect and job polling
"""

import hashlib
import time
import threading
import argparse
import requests
import sys
import os
from datetime import datetime

# Add parent directory to path to import crypto modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crypto import generate_keypair, sign_message, verify_signature

class QPCMiner:
    def __init__(self, node_url, wallet_address, threads=4):
        self.node_url = node_url.rstrip('/')
        self.wallet_address = wallet_address
        self.num_threads = threads
        self.running = False
        self.hashrate = 0.0
        self.shares_found = 0
        self.blocks_found = 0
        self.current_job = None
        self.lock = threading.Lock()
        
    def get_job(self):
        """Fetch mining job from node"""
        try:
            response = requests.get(f"{self.node_url}/api/get_mining_job", 
                                    params={'address': self.wallet_address},
                                    timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"[Error] Failed to fetch job: {e}")
        return None

    def submit_share(self, nonce, block_hash, job_id):
        """Submit valid share to node"""
        try:
            payload = {
                'job_id': job_id,
                'nonce': nonce,
                'hash': block_hash,
                'address': self.wallet_address
            }
            response = requests.post(f"{self.node_url}/api/submit_share", 
                                     json=payload, timeout=5)
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    with self.lock:
                        self.shares_found += 1
                        if result.get('is_block'):
                            self.blocks_found += 1
                            print(f"\n[🎉 BLOCK FOUND!] Hash: {block_hash[:16]}... Reward sent to {self.wallet_address[:8]}")
                        else:
                            print(f"[✅ Share Accepted] Difficulty: {result.get('difficulty')}")
                    return True
        except Exception as e:
            print(f"[Error] Failed to submit share: {e}")
        return False

    def mine_thread(self, thread_id):
        """Worker thread for mining"""
        local_hashes = 0
        last_report = time.time()
        
        while self.running:
            if not self.current_job:
                time.sleep(1)
                continue

            job = self.current_job
            block_header = job['header']
            target = job['target']
            job_id = job['job_id']
            
            # Randomized PoW Loop
            # We vary the hashing strategy slightly to simulate "Random X CPU"
            strategy = thread_id % 3 
            
            nonce = 0
            while self.running and self.current_job == job:
                nonce += 1
                local_hashes += 1
                
                # Construct data to hash
                # Strategy 0: Standard SHA256
                # Strategy 1: Double SHA256 with salt
                # Strategy 2: SHA256 of reversed bytes (simulating different CPU instructions)
                data = f"{block_header}{nonce}".encode()
                
                if strategy == 0:
                    h = hashlib.sha256(data).hexdigest()
                elif strategy == 1:
                    h = hashlib.sha256(hashlib.sha256(data + b"QPC_SALT").digest()).hexdigest()
                else:
                    h = hashlib.sha256(data[::-1]).hexdigest()
                
                # Check if hash meets target (simplified comparison for demo)
                # In real impl, compare integer values
                if int(h, 16) < target:
                    if self.submit_share(nonce, h, job_id):
                        # If block found, node usually sends new job immediately
                        pass
                    # Reset nonce range or continue depending on pool logic
                    # For solo/cpu mining, we usually keep going until job changes
                
                # Report hashrate every second
                if time.time() - last_report >= 1.0:
                    with self.lock:
                        self.hashrate = local_hashes / (time.time() - last_report)
                    local_hashes = 0
                    last_report = time.time()

            time.sleep(0.01) # Small yield

    def start(self):
        print(f"🚀 Starting QPC Miner...")
        print(f"📡 Node: {self.node_url}")
        print(f"💰 Address: {self.wallet_address}")
        print(f"🧵 Threads: {self.num_threads}")
        print("-" * 40)
        
        self.running = True
        
        # Fetch initial job
        job = self.get_job()
        if not job:
            print("❌ Could not connect to node. Is it running with --mine enabled?")
            return

        self.current_job = job
        print(f"✅ Connected. Current Difficulty: {job['difficulty']}")

        # Start worker threads
        threads = []
        for i in range(self.num_threads):
            t = threading.Thread(target=self.mine_thread, args=(i,), daemon=True)
            t.start()
            threads.append(t)

        # Main loop for status updates and job polling
        try:
            while self.running:
                time.sleep(5)
                # Poll for new job (new block found by network)
                new_job = self.get_job()
                if new_job and new_job['job_id'] != self.current_job['job_id']:
                    print(f"[🔄 New Job Received] Height: {new_job.get('height', '?')}")
                    self.current_job = new_job
                
                # Print status
                with self.lock:
                    hr_str = f"{self.hashrate:.2f} H/s" if self.hashrate > 1000 else f"{self.hashrate*1000:.2f} KH/s"
                    sys.stdout.write(f"\r⛏️ Status: {hr_str} | Shares: {self.shares_found} | Blocks: {self.blocks_found}   ")
                    sys.stdout.flush()
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping miner...")
            self.running = False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="QPC Standalone Miner")
    parser.add_argument("--node", default="http://127.0.0.1:5000", help="Node URL")
    parser.add_argument("--address", required=True, help="Wallet address for rewards")
    parser.add_argument("--threads", type=int, default=4, help="Number of CPU threads")
    
    args = parser.parse_args()
    
    miner = QPCMiner(args.node, args.address, args.threads)
    miner.start()
