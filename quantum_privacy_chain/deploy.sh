#!/bin/bash
# Quantum Privacy Chain - Network Deployment Script
# This script deploys a multi-node QPC network for testing

set -e

echo "🚀 Quantum Privacy Chain - Network Deployment"
echo "=============================================="

# Configuration
NUM_NODES=${1:-3}  # Default to 3 nodes
BASE_PORT=5000

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check dependencies
echo -e "${BLUE}Checking dependencies...${NC}"
python3 -c "import flask, requests, Crypto" 2>/dev/null || {
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install pycryptodome flask requests --quiet
}

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}Shutting down nodes...${NC}"
    pkill -f "python.*node.py" 2>/dev/null || true
    sleep 2
    echo -e "${GREEN}✅ All nodes stopped${NC}"
}

# Set trap for cleanup
trap cleanup EXIT INT TERM

# Start genesis node
echo -e "\n${BLUE}Starting genesis node on port $BASE_PORT...${NC}"
cd /workspace/quantum_privacy_chain
python node.py --port $BASE_PORT --genesis &
GENESIS_PID=$!
sleep 3

# Check if genesis node started
if ! kill -0 $GENESIS_PID 2>/dev/null; then
    echo -e "${RED}❌ Failed to start genesis node${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Genesis node started (PID: $GENESIS_PID)${NC}"

# Start additional nodes
for i in $(seq 2 $NUM_NODES); do
    PORT=$((BASE_PORT + i - 1))
    echo -e "${BLUE}Starting node $i on port $PORT...${NC}"
    python node.py --port $PORT --seed-node http://localhost:$BASE_PORT &
    sleep 2
    
    echo -e "${GREEN}✅ Node $i started (PID: $!)${NC}"
done

# Wait for network to stabilize
echo -e "\n${YELLOW}Waiting for network to stabilize...${NC}"
sleep 5

# Show network status
echo -e "\n${GREEN}============================================${NC}"
echo -e "${GREEN}  📊 QUANTUM PRIVACY CHAIN NETWORK STATUS${NC}"
echo -e "${GREEN}============================================${NC}\n"

for i in $(seq 1 $NUM_NODES); do
    PORT=$((BASE_PORT + i - 1))
    echo -e "${BLUE}Node $i (Port $PORT):${NC}"
    
    # Try to get status
    STATUS=$(curl -s http://localhost:$PORT/status 2>/dev/null || echo "Not ready")
    if [ "$STATUS" != "Not ready" ]; then
        CHAIN_LENGTH=$(echo $STATUS | python3 -c "import sys,json; print(json.load(sys.stdin).get('chain_length', 'N/A'))" 2>/dev/null || echo "N/A")
        PEERS=$(echo $STATUS | python3 -c "import sys,json; print(json.load(sys.stdin).get('peers', 'N/A'))" 2>/dev/null || echo "N/A")
        DIFFICULTY=$(echo $STATUS | python3 -c "import sys,json; print(json.load(sys.stdin).get('difficulty', 'N/A'))" 2>/dev/null || echo "N/A")
        
        echo "   Chain Length: $CHAIN_LENGTH"
        echo "   Peers: $PEERS"
        echo "   Difficulty: $DIFFICULTY"
        echo "   API: http://localhost:$PORT"
    else
        echo "   Status: Starting..."
    fi
    echo ""
done

echo -e "${YELLOW}============================================${NC}"
echo -e "${YELLOW}  📡 AVAILABLE ENDPOINTS${NC}"
echo -e "${YELLOW}============================================${NC}"
echo ""
echo "  Get blockchain:     curl http://localhost:$BASE_PORT/chain"
echo "  Get status:         curl http://localhost:$BASE_PORT/status"
echo "  Get peers:          curl http://localhost:$BASE_PORT/peers"
echo "  Mine block:         curl -X POST http://localhost:$BASE_PORT/mine"
echo "  Wallet address:     curl http://localhost:$BASE_PORT/wallet/address"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all nodes${NC}"
echo ""

# Keep running
wait
