# 🖥️ Quantum Privacy Chain - GUI Features

## Wallet GUI (`python gui.py --mode wallet`)

### Overview Tab
- **Balance Display**: Large, clear balance indicator in QPC tokens
- **Wallet Address**: Shows your quantum-proof public address
- **Create New Wallet**: Generate a new wallet with quantum-proof keys
- **Load Existing Wallet**: Import previously saved wallet files
- **Refresh Button**: Update balance from connected node
- **Network Statistics Panel**:
  - Node version and status
  - Current chain height
  - Pending transactions count
  - Connected peers
  - Network difficulty
  - Last block timestamp

### Send Tab
- **Recipient Address Field**: Enter stealth address or regular address
- **Amount Input**: Specify amount to send (with validation)
- **Privacy Level Slider**: 
  - Adjust ring size from 5 to 32
  - Real-time privacy level indicator (Low/Medium/High/Maximum)
  - Default: 16 (Higher than Monero's 11)
- **Send Transaction Button**: Create and broadcast private transaction
- **Status Messages**: Real-time feedback on transaction status
- **Transaction Hash Display**: View hash of sent transaction

### Receive Tab
- **Generate Stealth Address**: Create one-time stealth addresses
- **Address Display Box**: Shows generated stealth address
- **Copy to Clipboard**: One-click copy functionality
- **Privacy Benefits**: Each payment uses unique address

### History Tab
- **Transaction List**: Scrollable list of recent transactions
- **Transaction Details**:
  - Timestamp
  - Transaction hash (truncated)
  - Amount in QPC
  - Transaction type
  - Confirmation status
- **Refresh Button**: Update from node
- **Auto-refresh Option**: Configurable interval

### Mining Tab
- **Start/Stop Mining Toggle**: Begin or halt CPU mining
- **Mining Status Indicator**: Shows current mining state
- **Hash Rate Display**: Real-time hashes per second
- **Blocks Found Counter**: Track successful block discoveries
- **Mining Log**: Live console output showing:
  - Mining attempts
  - Block discoveries with rewards
  - Errors and warnings
- **Check Status Button**: Query network mining statistics
- **Warning Notice**: Educational info about experimental PoW

### Settings Tab
- **Default Ring Size Slider**: Set preferred privacy level
- **Auto-refresh Toggle**: Enable/disable automatic balance updates
- **Export Wallet Keys**: Backup wallet to secure file
- **About Section**:
  - Version information
  - Feature list
  - Security warnings
  - Experimental nature notice

## Node Manager GUI (`python gui.py --mode node`)

### Configuration Panel
- **Port Selection**: Choose listening port (default: 5000)
- **Genesis Node Checkbox**: Start as network genesis node
- **Peer Addresses**: Input seed nodes for connection

### Control Panel
- **Start Node Button**: Launch the P2P node
- **Stop Node Button**: Gracefully shutdown node
- **Status Indicator**: Current node state (Running/Stopped)

### Log Output
- **Real-time Logs**: Live node activity feed
- **Color-coded Output**: Green text on dark background
- **Scrollable Console**: Full history access
- **Error Highlighting**: Easy error identification

## Technical Features

### Security
- Local wallet encryption (file-based)
- No cloud storage of private keys
- Secure key generation using cryptographic RNG
- Quantum-proof lattice-based signatures

### Privacy
- Adjustable ring signatures (5-32 members)
- Stealth address generation
- Pedersen commitments for amount hiding
- No address reuse by default

### Usability
- Modern dark theme interface
- Responsive layout
- Intuitive tabbed navigation
- Clear status messages and error handling
- Tooltips and help text

### Integration
- REST API communication with nodes
- JSON-RPC style requests
- Automatic reconnection on failure
- Timeout handling

## System Requirements

### Minimum
- Python 3.8+
- 2GB RAM
- Display server (X11/Wayland) for GUI
- Network connectivity for node operation

### Dependencies
```bash
pip install customtkinter requests flask numpy scipy
apt-get install python3-tk tk
```

## Usage Examples

### Basic Wallet Operation
1. Launch: `python gui.py --mode wallet`
2. Click "Create New Wallet"
3. Save wallet file securely
4. Note your address
5. Use "Receive" tab to generate stealth addresses
6. Use "Send" tab to make private transactions

### Mining Setup
1. Load or create a wallet
2. Navigate to "Mining" tab
3. Click "Start Mining"
4. Monitor hash rate and blocks found
5. Rewards automatically credited to loaded wallet

### Node Management
1. Launch: `python gui.py --mode node`
2. Configure port (e.g., 5000)
3. Check "Genesis Node" for first node
4. Click "Start Node"
5. Monitor logs for activity
6. Share node URL with other users

## Troubleshooting

### GUI Won't Start
- Ensure tkinter is installed: `apt-get install python3-tk`
- Check display server is running
- Verify customtkinter installation

### Cannot Connect to Node
- Verify node is running
- Check firewall settings
- Confirm correct port and URL

### Mining Not Working
- Ensure wallet is loaded
- Verify node connection
- Check node has pending transactions

## Future Enhancements

- [ ] QR code generation for addresses
- [ ] Multi-wallet support
- [ ] Advanced transaction options
- [ ] Network topology visualization
- [ ] Enhanced mining statistics
- [ ] Hardware wallet integration
- [ ] Mobile companion app
- [ ] Trading pair integration

---

**⚠️ WARNING**: This is experimental software for research purposes only. Do not use for real financial transactions.
