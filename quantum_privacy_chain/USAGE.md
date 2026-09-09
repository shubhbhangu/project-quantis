# Quantum Privacy Chain (QPC) - Complete Usage Guide

## 🚀 Quick Start

### 1. Start a Node
```bash
cd /workspace/quantum_privacy_chain

# Start genesis node on port 5000
python node.py --port 5000 --genesis
```

### 2. Launch GUI Wallet
```bash
# In a new terminal
python gui.py --mode wallet
```

### 3. Launch Node Manager with Mining
```bash
# In a new terminal  
python gui.py --mode node
# Click "Start Node", then "Start Mining"
```

### 4. Use Standalone Miner
```bash
# Get your wallet address first from GUI or:
curl http://localhost:5000/wallet/address

# Start mining (replace ADDRESS with your wallet address)
python miner.py --address YOUR_WALLET_ADDRESS --threads 4
```

## 📋 All Components

| Component | File | Description |
|-----------|------|-------------|
| **Blockchain Core** | `blockchain.py` | Chain logic, transactions, PoW |
| **Cryptography** | `crypto.py` | Quantum-proof signatures, ring signatures, commitments |
| **Wallet** | `wallet.py` | Key management, stealth addresses, transaction creation |
| **Node** | `node.py` | P2P networking, REST API, mining endpoints |
| **Miner** | `miner.py` | Standalone CPU miner with multi-threading |
| **GUI** | `gui.py` | Modern desktop interface for wallet & node |
| **Demo** | `demo.py` | Interactive command-line demonstration |
| **Deploy** | `deploy.sh` | Multi-node network deployment script |

## 🔐 Privacy Features

- **Ring Signatures**: Size 16-32 (configurable in GUI)
- **Stealth Addresses**: Automatic receiver privacy
- **Pedersen Commitments**: Hidden transaction amounts
- **Quantum-Proof**: Lattice-based signatures (Dilithium-inspired)
- **Random CPU PoW**: ASIC-resistant mining

## 🖥️ GUI Features

### Wallet Tab
- Balance overview
- Send private transactions
- Receive with stealth addresses
- Transaction history
- Built-in miner control
- Adjustable privacy settings

### Node Manager Tab
- Start/stop node
- Genesis node configuration
- Peer management
- Live logs
- Integrated mining controls

## ⛏️ Mining

### Via GUI
1. Open Node Manager (`python gui.py --mode node`)
2. Click "Start Node"
3. Click "Start Mining"
4. Enter thread count (default: 4)

### Via Command Line
```bash
python miner.py --node http://localhost:5000 --address QPC_YOUR_ADDRESS --threads 8
```

### Via Node API
```bash
# Get mining job
curl "http://localhost:5000/api/get_mining_job?address=YOUR_ADDRESS"

# Submit share
curl -X POST http://localhost:5000/api/submit_share \
  -H "Content-Type: application/json" \
  -d '{"job_id":1,"nonce":12345,"hash":"abc...","address":"YOUR_ADDRESS"}'
```

## 🌐 Network Deployment

Deploy a 3-node network:
```bash
./deploy.sh 3
```

This starts:
- Node 1: Port 5000 (genesis)
- Node 2: Port 5001 (connected to genesis)
- Node 3: Port 5002 (connected to genesis)

## 🧪 Testing

Run the interactive demo:
```bash
python demo.py
```

Test individual components:
```bash
# Test crypto
python -c "from crypto import *; print('Crypto OK')"

# Test blockchain
python -c "from blockchain import Blockchain; b=Blockchain(); print('Blockchain OK')"

# Test wallet
python -c "from wallet import create_wallet; w=create_wallet('test.json'); print('Wallet OK')"
```

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chain` | GET | Get full blockchain |
| `/status` | GET | Node status |
| `/peers` | GET | Connected peers |
| `/transaction` | POST | Submit transaction |
| `/pending` | GET | Pending transactions |
| `/mine` | POST | Trigger internal mining |
| `/api/get_mining_job` | GET | Get external mining job |
| `/api/submit_share` | POST | Submit mining share |
| `/wallet/address` | GET | Node wallet address |
| `/balance/<address>` | GET | Check balance |

## ⚠️ Important Notes

- **Experimental Software**: Not for real financial transactions
- **Privacy Settings**: Higher ring sizes = more privacy but slower transactions
- **Mining**: CPU-only by design (ASIC resistance)
- **Network**: Local testing recommended before P2P deployment

## 🎯 Next Steps

1. **Explore the Demo**: Run `python demo.py` to see all features
2. **Launch GUI**: Try the wallet and node manager
3. **Test Mining**: Start a node and run the miner
4. **Deploy Network**: Use deploy.sh for multi-node testing
5. **Review Code**: Examine crypto.py for quantum-proof implementation

Enjoy exploring the Quantum Privacy Chain! 🔐⛏️🚀
