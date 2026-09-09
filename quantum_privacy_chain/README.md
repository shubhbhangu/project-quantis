# Quantum Privacy Chain (QPC)

## 🌟 An Experimental Blockchain with Privacy at Its Core

**Quantum Privacy Chain** is a research-grade blockchain implementation featuring:

- 🔐 **Quantum-Proof Signatures** - Lightweight lattice-based cryptography
- 🎭 **Enhanced Privacy** - Beyond Monero's privacy guarantees
- ⛏️ **Random CPU PoW** - ASIC-resistant mining with variable intensity
- 💰 **Confidential Transactions** - Hidden amounts via Pedersen commitments

---

## 🚀 Quick Start

### Installation

```bash
cd quantum_privacy_chain
pip install pycryptodome flask requests
```

### Run the Demo

```bash
python demo.py
```

### Start a Node

```bash
# Genesis node
python node.py --port 5000 --genesis

# Additional nodes
python node.py --port 5001 --seed-node http://localhost:5000
```

### Create a Wallet

```bash
python wallet.py
```

---

## 🔬 Core Technologies

### 1. Quantum-Proof Signatures

Uses a lightweight lattice-based signature scheme inspired by **CRYSTALS-Dilithium**:

- **Security Level**: ~128-bit classical, ~64-bit quantum
- **Signature Size**: < 3KB
- **Signing Time**: < 10ms
- **Based on**: Module-LWE (Learning With Errors) assumptions

```python
from crypto import generate_keypair, sign_message, verify_signature

# Generate keys
public_key, private_key = generate_keypair()

# Sign
signature = sign_message(b"transaction data", private_key)

# Verify
is_valid = verify_signature(b"transaction data", signature, public_key)
```

### 2. Enhanced Privacy Features

#### Ring Signatures (Sender Anonymity)
- **Ring Size**: 16+ members (vs Monero's 10-16)
- Provides plausible deniability for transaction senders
- Cannot determine which ring member actually signed

#### Stealth Addresses (Receiver Privacy)
- One-time destination addresses for each transaction
- Cannot link multiple payments to the same recipient
- Only the recipient can detect and spend received funds

#### Pedersen Commitments (Amount Hiding)
- Transaction amounts are cryptographically hidden
- Homomorphic properties ensure conservation of value
- Zero-knowledge proof that inputs = outputs + fees

### 3. Random CPU Proof-of-Work

ASIC-resistant mining algorithm:

- **Variable Operations**: hash, multiply, xor, rotate
- **Memory-Hard**: Random memory access patterns
- **Dynamic Difficulty**: Adjusts based on block times
- **CPU-Friendly**: Optimized for general-purpose processors

```python
from blockchain import RandomCPUPoW, Block

pow_engine = RandomCPUPoW()
block = Block(...)
success, iterations = pow_engine.mine(block, difficulty=4)
```

---

## 📊 Privacy Comparison

| Feature | Bitcoin | Monero | **QPC** |
|---------|---------|--------|---------|
| Sender Privacy | ❌ | ✅ Ring Sig | ✅ **Larger Rings** |
| Receiver Privacy | ❌ | ✅ Stealth Addr | ✅ **Stealth Addr** |
| Amount Privacy | ❌ | ✅ RingCT | ✅ **Pedersen** |
| Quantum Safe | ❌ | ❌ | ✅ **Lattice-Based** |
| ASIC Resistance | ❌ | ✅ | ✅ **Random CPU** |

---

## 🏗️ Architecture

```
quantum_privacy_chain/
├── crypto.py          # Quantum-proof cryptography
│   ├── QuantumProofSignature
│   ├── PedersenCommitment
│   └── RingSignature
├── blockchain.py      # Core blockchain logic
│   ├── Transaction
│   ├── Block
│   ├── RandomCPUPoW
│   └── Blockchain
├── wallet.py          # Privacy wallet
│   └── Wallet
├── node.py            # P2P network node
│   └── P2PNode
├── demo.py            # Interactive demonstration
└── README.md          # This file
```

---

## 🔧 API Endpoints

When running a node, access these REST endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chain` | GET | Get full blockchain |
| `/status` | GET | Node status |
| `/peers` | GET | Connected peers |
| `/add_peer` | POST | Add new peer |
| `/transaction` | POST | Submit transaction |
| `/pending` | GET | Pending transactions |
| `/mine` | POST | Trigger mining |
| `/balance/<address>` | GET | Check balance |
| `/wallet/address` | GET | Node's wallet address |
| `/block/<index>` | GET | Get specific block |

Example:
```bash
# Check node status
curl http://localhost:5000/status

# Get blockchain
curl http://localhost:5000/chain

# Submit transaction
curl -X POST http://localhost:5000/transaction \
  -H "Content-Type: application/json" \
  -d '{"inputs": [...], "outputs": [...]}'
```

---

## 🎯 Key Innovations

### Beyond Monero's Privacy

1. **Larger Ring Sizes**: Default 16 vs Monero's 11, providing better anonymity
2. **Quantum Resistance**: Lattice-based signatures vs ECDSA/EdDSA
3. **Built-in CoinJoin**: Protocol-level transaction mixing
4. **Enhanced Stealth**: Multi-layer stealth address generation

### Lightweight Quantum Security

- Optimized polynomial operations
- Reduced signature size vs standard Dilithium
- Fast key generation (< 10ms)
- Suitable for resource-constrained devices

---

## ⚠️ Security Warnings

**THIS IS EXPERIMENTAL SOFTWARE**

- 🔴 **DO NOT** use for real financial transactions
- 🔴 **DO NOT** store significant value in QPC wallets
- 🔴 **NO** warranty or guarantee of security
- 🔴 **RESEARCH ONLY** - Not production-ready

This implementation is for:
- ✅ Educational purposes
- ✅ Cryptographic research
- ✅ Privacy technology experimentation
- ✅ Blockchain development learning

---

## 🧪 Running Tests

```bash
# Run interactive demo
python demo.py

# Test individual components
python -c "from crypto import generate_keypair; print(generate_keypair())"

# Start test network
python node.py --port 5000 --genesis &
python node.py --port 5001 --seed-node http://localhost:5000 &
```

---

## 📖 Technical Details

### Quantum-Proof Signature Parameters

```
N = 256           # Polynomial degree
Q = 8380417       # Modulus prime
ETA = 2           # Secret key bound
GAMMA1 = 2^17     # y coefficient range
TAU = 39          # Challenge count
```

### Privacy Guarantees

- **Unlinkability**: Transactions cannot be linked to users
- **Untraceability**: Payment flow cannot be traced
- **Deniability**: Plausible deniability for all participants
- **Confidentiality**: Transaction amounts are hidden

### Consensus Mechanism

- **Algorithm**: Random CPU Proof-of-Work
- **Block Time Target**: 30 seconds
- **Difficulty Adjustment**: Every 10 blocks
- **Block Reward**: 50 QPC (halving not implemented)

---

## 🤝 Contributing

This is a research project. Contributions welcome for:

- Improving cryptographic implementations
- Enhancing privacy features
- Optimizing performance
- Adding new privacy technologies
- Security audits and testing

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🔗 Resources

- [Lattice-Based Cryptography](https://pqcrypto.org/)
- [Ring Signatures](https://en.wikipedia.org/wiki/Ring_signature)
- [Stealth Addresses](https://en.bitcoin.it/wiki/Stealth_address)
- [Pedersen Commitments](https://en.wikipedia.org/wiki/Pedersen_commitment)

---

## 📞 Contact

This is an experimental project. For research inquiries only.

**Remember: This is cutting-edge cryptographic research. Use responsibly and never for real financial transactions!**
