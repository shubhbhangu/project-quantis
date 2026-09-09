# 🚀 Quick Start Guide - Quantum Privacy Chain

## GUI Wallet & Node Manager

### Launch the Wallet GUI
```bash
python gui.py --mode wallet
```

**Features:**
- 🔐 **Overview Tab**: View balance, create/load wallets, network stats
- 💸 **Send Tab**: Send private transactions with adjustable ring size (5-32)
- 📥 **Receive Tab**: Generate stealth addresses for receiving funds
- 📜 **History Tab**: Transaction history with details
- ⛏️ **Mining Tab**: CPU mining with real-time hash rate and block counter
- ⚙️ **Settings Tab**: Configure privacy defaults, export wallet keys

### Launch the Node Manager GUI
```bash
python gui.py --mode node
```

**Features:**
- Configure port and genesis node settings
- Start/stop node with one click
- Real-time log output
- Peer management

## Command Line Usage

### Start a Genesis Node
```bash
python node.py --port 5000 --genesis
```

### Connect Additional Nodes
```bash
python node.py --port 5001 --seed-node http://localhost:5000
```

### Run Demo
```bash
python demo.py
```

### Deploy Multi-Node Network
```bash
./deploy.sh 3  # Deploys 3 nodes
```

## API Endpoints

Once a node is running, access the REST API:

- `GET /api/status` - Node status
- `GET /api/balance/<address>` - Check balance
- `POST /api/transaction` - Broadcast transaction
- `POST /api/mine` - Mine a block
- `GET /api/peers` - List connected peers

## Requirements

```bash
pip install customtkinter requests flask numpy scipy
apt-get install python3-tk tk  # For GUI
```

## ⚠️ Important Notes

- This is **experimental research software**
- Do **NOT** use for real financial transactions
- Quantum-proof cryptography is simplified for demonstration
- Random CPU PoW is energy-intensive - use on test networks only
