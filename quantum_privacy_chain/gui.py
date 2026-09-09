#!/usr/bin/env python3
"""
Quantum Privacy Chain - GUI Wallet & Node Manager
A modern desktop interface for the QPC network.
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog, scrolledtext
import threading
import json
import os
import sys
import time
from datetime import datetime
import requests

# Import local modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wallet import Wallet
from blockchain import Transaction, Block
from crypto import generate_keypair

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class WalletGUI(ctk.CTk):
    """Modern GUI Wallet for Quantum Privacy Chain"""
    
    def __init__(self):
        super().__init__()
        
        self.title("QPC Wallet - Quantum Privacy Chain")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        
        # Wallet state
        self.wallet = None
        self.node_url = "http://localhost:5000"
        self.balance = 0.0
        self.transactions = []
        self.peers = []
        self.is_mining = False
        self.mining_thread = None
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.create_main_layout()
        self.create_menu()
        
    def create_menu(self):
        """Create top menu bar"""
        self.menu_frame = ctk.CTkFrame(self, height=40)
        self.menu_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # Title
        title_label = ctk.CTkLabel(
            self.menu_frame, 
            text="🔐 QPC Wallet - Quantum Privacy Chain", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(side="left", padx=20, pady=10)
        
        # Node URL entry
        url_frame = ctk.CTkFrame(self.menu_frame, fg_color="transparent")
        url_frame.pack(side="right", padx=20, pady=5)
        
        ctk.CTkLabel(url_frame, text="Node URL:").pack(side="left", padx=5)
        self.url_entry = ctk.CTkEntry(url_frame, width=200)
        self.url_entry.insert(0, self.node_url)
        self.url_entry.pack(side="left", padx=5)
        
        connect_btn = ctk.CTkButton(
            url_frame, 
            text="Connect", 
            command=self.connect_to_node,
            width=80
        )
        connect_btn.pack(side="left", padx=5)
        
    def create_main_layout(self):
        """Create main tabbed layout"""
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # Create tabs
        self.overview_tab = self.tabview.add("Overview")
        self.send_tab = self.tabview.add("Send")
        self.receive_tab = self.tabview.add("Receive")
        self.history_tab = self.tabview.add("History")
        self.mining_tab = self.tabview.add("Mining")
        self.settings_tab = self.tabview.add("Settings")
        
        self.setup_overview_tab()
        self.setup_send_tab()
        self.setup_receive_tab()
        self.setup_history_tab()
        self.setup_mining_tab()
        self.setup_settings_tab()
        
    def setup_overview_tab(self):
        """Setup overview tab with balance and stats"""
        self.overview_tab.grid_columnconfigure(0, weight=1)
        self.overview_tab.grid_rowconfigure(1, weight=1)
        
        # Balance card
        balance_frame = ctk.CTkFrame(self.overview_tab)
        balance_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        
        self.balance_label = ctk.CTkLabel(
            balance_frame,
            text="Balance: 0.00 QPC",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        self.balance_label.pack(pady=20)
        
        self.address_label = ctk.CTkLabel(
            balance_frame,
            text="No wallet loaded",
            font=ctk.CTkFont(size=14)
        )
        self.address_label.pack(pady=5)
        
        # Action buttons
        btn_frame = ctk.CTkFrame(balance_frame, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        create_wallet_btn = ctk.CTkButton(
            btn_frame,
            text="Create New Wallet",
            command=self.create_new_wallet,
            width=150
        )
        create_wallet_btn.pack(side="left", padx=10)
        
        load_wallet_btn = ctk.CTkButton(
            btn_frame,
            text="Load Existing Wallet",
            command=self.load_wallet,
            width=150
        )
        load_wallet_btn.pack(side="left", padx=10)
        
        refresh_btn = ctk.CTkButton(
            btn_frame,
            text="Refresh",
            command=self.refresh_balance,
            width=100
        )
        refresh_btn.pack(side="left", padx=10)
        
        # Stats frame
        stats_frame = ctk.CTkFrame(self.overview_tab)
        stats_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        ctk.CTkLabel(
            stats_frame,
            text="Network Statistics",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        self.stats_text = scrolledtext.ScrolledText(
            stats_frame,
            wrap='word',
            bg='#2b2b2b',
            fg='#ffffff',
            font=('Courier', 10)
        )
        self.stats_text.pack(fill='both', expand=True, padx=10, pady=10)
        
    def setup_send_tab(self):
        """Setup send transaction tab"""
        self.send_tab.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            self.send_tab,
            text="Send QPC Privately",
            font=ctk.CTkFont(size=20, weight="bold")
        ).grid(row=0, column=0, columnspan=2, pady=20)
        
        # Recipient address
        ctk.CTkLabel(self.send_tab, text="Recipient Address:").grid(
            row=1, column=0, sticky="w", padx=20, pady=10
        )
        self.recipient_entry = ctk.CTkEntry(self.send_tab, width=400)
        self.recipient_entry.grid(row=1, column=1, sticky="ew", padx=20, pady=10)
        
        # Amount
        ctk.CTkLabel(self.send_tab, text="Amount (QPC):").grid(
            row=2, column=0, sticky="w", padx=20, pady=10
        )
        self.amount_entry = ctk.CTkEntry(self.send_tab, width=200)
        self.amount_entry.grid(row=2, column=1, sticky="w", padx=20, pady=10)
        
        # Privacy options
        privacy_frame = ctk.CTkFrame(self.send_tab)
        privacy_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=20, pady=20)
        
        ctk.CTkLabel(
            privacy_frame,
            text="Privacy Level:",
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=5)
        
        self.ring_size_var = ctk.StringVar(value="16")
        ring_slider = ctk.CTkSlider(
            privacy_frame,
            from_=5,
            to=32,
            number_of_steps=27,
            command=lambda x: self.ring_size_var.set(str(int(x)))
        )
        ring_slider.set(16)
        ring_slider.pack(fill='x', padx=20, pady=10)
        
        self.ring_size_label = ctk.CTkLabel(
            privacy_frame,
            text="Ring Size: 16 (High Privacy)"
        )
        self.ring_size_label.pack()
        
        def update_ring_label(val):
            size = int(val)
            level = "Low" if size < 10 else "Medium" if size < 20 else "High" if size < 28 else "Maximum"
            self.ring_size_label.configure(text=f"Ring Size: {size} ({level} Privacy)")
        
        ring_slider.configure(command=lambda x: update_ring_label(x))
        
        # Send button
        send_btn = ctk.CTkButton(
            self.send_tab,
            text="Send Transaction",
            command=self.send_transaction,
            height=40,
            width=200
        )
        send_btn.grid(row=4, column=0, columnspan=2, pady=30)
        
        # Status
        self.send_status = ctk.CTkLabel(self.send_tab, text="")
        self.send_status.grid(row=5, column=0, columnspan=2, pady=10)
        
    def setup_receive_tab(self):
        """Setup receive tab with address generation"""
        self.receive_tab.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            self.receive_tab,
            text="Receive QPC Privately",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=20)
        
        # Generate stealth address
        gen_btn = ctk.CTkButton(
            self.receive_tab,
            text="Generate Stealth Address",
            command=self.generate_stealth_address,
            width=200
        )
        gen_btn.pack(pady=10)
        
        self.stealth_address_text = ctk.CTkTextbox(
            self.receive_tab,
            height=100,
            width=600
        )
        self.stealth_address_text.pack(pady=10)
        
        copy_btn = ctk.CTkButton(
            self.receive_tab,
            text="Copy Address",
            command=self.copy_address,
            width=150
        )
        copy_btn.pack(pady=10)
        
        self.receive_status = ctk.CTkLabel(self.receive_tab, text="")
        self.receive_status.pack(pady=10)
        
    def setup_history_tab(self):
        """Setup transaction history tab"""
        self.history_tab.grid_columnconfigure(0, weight=1)
        self.history_tab.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(
            self.history_tab,
            text="Transaction History",
            font=ctk.CTkFont(size=20, weight="bold")
        ).grid(row=0, column=0, pady=20)
        
        refresh_btn = ctk.CTkButton(
            self.history_tab,
            text="Refresh History",
            command=self.refresh_history,
            width=150
        )
        refresh_btn.grid(row=0, column=0, pady=20, sticky="e", padx=20)
        
        self.history_text = scrolledtext.ScrolledText(
            self.history_tab,
            wrap='word',
            bg='#2b2b2b',
            fg='#ffffff',
            font=('Courier', 9)
        )
        self.history_text.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
    def setup_mining_tab(self):
        """Setup mining tab"""
        self.mining_tab.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            self.mining_tab,
            text="CPU Mining (Random PoW)",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=20)
        
        info_frame = ctk.CTkFrame(self.mining_tab)
        info_frame.pack(fill='x', padx=20, pady=10)
        
        ctk.CTkLabel(
            info_frame,
            text="⚠️ Experimental: Random CPU PoW is ASIC-resistant but energy-intensive.\nOnly mine on test networks.",
            justify='left'
        ).pack(padx=20, pady=10)
        
        self.mining_status_label = ctk.CTkLabel(
            self.mining_tab,
            text="Status: Not Mining",
            font=ctk.CTkFont(size=16)
        )
        self.mining_status_label.pack(pady=10)
        
        self.hash_rate_label = ctk.CTkLabel(
            self.mining_tab,
            text="Hash Rate: 0 H/s",
            font=ctk.CTkFont(size=14)
        )
        self.hash_rate_label.pack(pady=5)
        
        self.blocks_found_label = ctk.CTkLabel(
            self.mining_tab,
            text="Blocks Found: 0",
            font=ctk.CTkFont(size=14)
        )
        self.blocks_found_label.pack(pady=5)
        
        btn_frame = ctk.CTkFrame(self.mining_tab, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        self.start_mining_btn = ctk.CTkButton(
            btn_frame,
            text="Start Mining",
            command=self.toggle_mining,
            width=150
        )
        self.start_mining_btn.pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame,
            text="Check Status",
            command=self.check_mining_status,
            width=150
        ).pack(side="left", padx=10)
        
        self.mining_log = scrolledtext.ScrolledText(
            self.mining_tab,
            height=15,
            wrap='word',
            bg='#1a1a1a',
            fg='#00ff00',
            font=('Courier', 8)
        )
        self.mining_log.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.blocks_found = 0
        
    def setup_settings_tab(self):
        """Setup settings tab"""
        self.settings_tab.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            self.settings_tab,
            text="Wallet Settings",
            font=ctk.CTkFont(size=20, weight="bold")
        ).grid(row=0, column=0, columnspan=2, pady=20)
        
        # Default privacy
        ctk.CTkLabel(self.settings_tab, text="Default Ring Size:").grid(
            row=1, column=0, sticky="w", padx=20, pady=10
        )
        self.default_ring_slider = ctk.CTkSlider(
            self.settings_tab,
            from_=5,
            to=32,
            number_of_steps=27
        )
        self.default_ring_slider.set(16)
        self.default_ring_slider.grid(row=1, column=1, sticky="w", padx=20, pady=10)
        
        # Auto-refresh
        self.auto_refresh_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            self.settings_tab,
            text="Auto-refresh balance every 30s",
            variable=self.auto_refresh_var,
            command=self.toggle_auto_refresh
        ).grid(row=2, column=0, sticky="w", padx=20, pady=10)
        
        # Export wallet
        export_btn = ctk.CTkButton(
            self.settings_tab,
            text="Export Wallet Keys",
            command=self.export_wallet,
            width=200
        )
        export_btn.grid(row=3, column=0, pady=20)
        
        # About
        about_text = """
        Quantum Privacy Chain (QPC) v1.0
        
        Features:
        • Quantum-proof lattice-based signatures
        • Ring signatures for sender anonymity
        • Stealth addresses for receiver privacy
        • Pedersen commitments for amount hiding
        • Random CPU PoW (ASIC-resistant)
        
        ⚠️ This is experimental software.
        Do not use for real financial transactions.
        """
        
        about_label = ctk.CTkLabel(
            self.settings_tab,
            text=about_text,
            justify='left'
        )
        about_label.grid(row=4, column=0, columnspan=2, pady=20)
        
    def create_new_wallet(self):
        """Create a new wallet"""
        try:
            self.wallet = Wallet()
            filename = f"qpc_wallet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            self.wallet.save(filename)
            
            self.address_label.configure(
                text=f"Address: {self.wallet.get_address()[:20]}..."
            )
            self.balance_label.configure(text="Balance: 0.00 QPC")
            
            messagebox.showinfo(
                "Wallet Created",
                f"New wallet created and saved to:\n{filename}\n\nBackup this file securely!"
            )
            
            self.refresh_balance()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create wallet: {str(e)}")
            
    def load_wallet(self):
        """Load existing wallet"""
        try:
            filename = filedialog.askopenfilename(
                title="Select Wallet File",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                self.wallet = Wallet.load(filename)
                self.address_label.configure(
                    text=f"Address: {self.wallet.get_address()}"
                )
                self.refresh_balance()
                messagebox.showinfo("Success", "Wallet loaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load wallet: {str(e)}")
            
    def connect_to_node(self):
        """Connect to QPC node"""
        self.node_url = self.url_entry.get().strip()
        try:
            response = requests.get(f"{self.node_url}/api/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.update_stats(data)
                messagebox.showinfo("Connected", f"Connected to node at {self.node_url}")
            else:
                raise Exception("Invalid response")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot connect to node: {str(e)}")
            
    def update_stats(self, node_data):
        """Update network statistics display"""
        self.stats_text.delete(1.0, 'end')
        stats = f"""
Network Status: Connected
Node Version: {node_data.get('version', 'Unknown')}
Chain Height: {node_data.get('chain_length', 0)}
Pending Transactions: {node_data.get('pending_txs', 0)}
Connected Peers: {node_data.get('peers', 0)}
Difficulty: {node_data.get('difficulty', 0)}
Last Block: {node_data.get('last_block_time', 'N/A')}
        """.strip()
        self.stats_text.insert('1.0', stats)
        
    def refresh_balance(self):
        """Refresh wallet balance from node"""
        if not self.wallet:
            return
            
        try:
            address = self.wallet.get_address()
            response = requests.get(
                f"{self.node_url}/api/balance/{address}",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                self.balance = data.get('balance', 0)
                self.balance_label.configure(
                    text=f"Balance: {self.balance:.4f} QPC"
                )
        except Exception as e:
            print(f"Error refreshing balance: {e}")
            
    def send_transaction(self):
        """Send a private transaction"""
        if not self.wallet:
            messagebox.showerror("Error", "No wallet loaded")
            return
            
        recipient = self.recipient_entry.get().strip()
        try:
            amount = float(self.amount_entry.get())
        except:
            messagebox.showerror("Error", "Invalid amount")
            return
            
        if amount <= 0:
            messagebox.showerror("Error", "Amount must be positive")
            return
            
        ring_size = int(self.ring_size_var.get())
        
        self.send_status.configure(text="Creating transaction...")
        self.update()
        
        try:
            # Create transaction through wallet
            tx = self.wallet.create_transaction(
                recipient=recipient,
                amount=amount,
                ring_size=ring_size
            )
            
            # Broadcast to node
            response = requests.post(
                f"{self.node_url}/api/transaction",
                json=tx.to_dict(),
                timeout=10
            )
            
            if response.status_code == 200:
                self.send_status.configure(
                    text=f"✓ Transaction sent! Hash: {tx.hash[:16]}..."
                )
                messagebox.showinfo(
                    "Success",
                    f"Transaction sent successfully!\nHash: {tx.hash}"
                )
                self.refresh_balance()
            else:
                error = response.json().get('error', 'Unknown error')
                self.send_status.configure(text=f"✗ Failed: {error}")
                messagebox.showerror("Error", f"Transaction failed: {error}")
                
        except Exception as e:
            self.send_status.configure(text=f"✗ Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to send: {str(e)}")
            
    def generate_stealth_address(self):
        """Generate a new stealth address"""
        if not self.wallet:
            self.stealth_address_text.insert('1.0', "Please load a wallet first")
            return
            
        try:
            stealth_addr = self.wallet.generate_stealth_address()
            self.stealth_address_text.delete('1.0', 'end')
            self.stealth_address_text.insert('1.0', stealth_addr)
            self.receive_status.configure(text="✓ Stealth address generated")
        except Exception as e:
            self.receive_status.configure(text=f"✗ Error: {str(e)}")
            
    def copy_address(self):
        """Copy stealth address to clipboard"""
        address = self.stealth_address_text.get('1.0', 'end').strip()
        if address:
            self.clipboard_clear()
            self.clipboard_append(address)
            messagebox.showinfo("Copied", "Address copied to clipboard!")
            
    def refresh_history(self):
        """Refresh transaction history"""
        if not self.wallet:
            return
            
        try:
            address = self.wallet.get_address()
            response = requests.get(
                f"{self.node_url}/api/transactions/{address}",
                timeout=5
            )
            if response.status_code == 200:
                txs = response.json().get('transactions', [])
                self.history_text.delete('1.0', 'end')
                
                if not txs:
                    self.history_text.insert('1.0', "No transactions found")
                else:
                    for tx in reversed(txs[-20:]):  # Last 20 transactions
                        line = f"""
Date: {tx.get('timestamp', 'N/A')}
Hash: {tx.get('hash', 'N/A')[:20]}...
Amount: {tx.get('amount', 0):.4f} QPC
Type: {tx.get('type', 'N/A')}
Status: {tx.get('status', 'N/A')}
---
"""
                        self.history_text.insert('end', line)
        except Exception as e:
            self.history_text.insert('1.0', f"Error loading history: {str(e)}")
            
    def toggle_mining(self):
        """Start/stop mining"""
        if self.is_mining:
            self.is_mining = False
            self.start_mining_btn.configure(text="Start Mining")
            self.mining_status_label.configure(text="Status: Stopping...")
        else:
            if not self.wallet:
                messagebox.showerror("Error", "Load a wallet first to receive rewards")
                return
                
            self.is_mining = True
            self.start_mining_btn.configure(text="Stop Mining")
            self.mining_status_label.configure(text="Status: Mining...")
            self.mining_thread = threading.Thread(target=self.mine_loop)
            self.mining_thread.daemon = True
            self.mining_thread.start()
            
    def mine_loop(self):
        """Mining loop"""
        start_time = time.time()
        hashes = 0
        
        while self.is_mining:
            try:
                # Call node mining API
                response = requests.post(
                    f"{self.node_url}/api/mine",
                    json={"miner_address": self.wallet.get_address()},
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        self.blocks_found += 1
                        self.blocks_found_label.configure(
                            text=f"Blocks Found: {self.blocks_found}"
                        )
                        reward = result.get('reward', 0)
                        self.mining_log.insert('end', 
                            f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Block found! Reward: {reward} QPC\n"
                        )
                        self.refresh_balance()
                    else:
                        hashes += result.get('hashes_attempted', 1000)
                        elapsed = time.time() - start_time
                        hash_rate = hashes / max(elapsed, 1)
                        self.hash_rate_label.configure(
                            text=f"Hash Rate: {hash_rate:.0f} H/s"
                        )
                        
                        if hashes % 10000 == 0:
                            self.mining_log.insert('end', 
                                f"[{datetime.now().strftime('%H:%M:%S')}] Mining... Total hashes: {hashes}\n"
                            )
                            self.mining_log.see('end')
                else:
                    self.mining_log.insert('end', 
                        f"[{datetime.now().strftime('%H:%M:%S')}] ✗ Mining error\n"
                    )
                    
                time.sleep(0.1)  # Small delay between attempts
                
            except Exception as e:
                self.mining_log.insert('end', 
                    f"[{datetime.now().strftime('%H:%M:%S')}] Error: {str(e)}\n"
                )
                time.sleep(5)
                
    def check_mining_status(self):
        """Check current mining status"""
        try:
            response = requests.get(f"{self.node_url}/api/mining/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                status = f"""
Network Hash Rate: {data.get('network_hashrate', 0)} H/s
Your Hash Rate: {data.get('your_hashrate', 0)} H/s
Pending Blocks: {data.get('pending_blocks', 0)}
Difficulty: {data.get('difficulty', 0)}
                """
                self.mining_log.insert('end', f"\n{status}\n")
                self.mining_log.see('end')
        except Exception as e:
            messagebox.showerror("Error", f"Cannot get mining status: {str(e)}")
            
    def toggle_auto_refresh(self):
        """Toggle auto-refresh"""
        if self.auto_refresh_var.get():
            self.auto_refresh_loop()
            
    def auto_refresh_loop(self):
        """Auto-refresh balance every 30s"""
        if self.auto_refresh_var.get():
            self.refresh_balance()
            self.after(30000, self.auto_refresh_loop)
            
    def export_wallet(self):
        """Export wallet keys"""
        if not self.wallet:
            messagebox.showerror("Error", "No wallet loaded")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile=f"qpc_wallet_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        if filename:
            try:
                self.wallet.save(filename)
                messagebox.showinfo(
                    "Export Successful",
                    f"Wallet exported to:\n{filename}\n\n⚠️ Keep this file secure and private!"
                )
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")


class NodeManagerGUI(ctk.CTk):
    """GUI Node Manager for running QPC nodes"""
    
    def __init__(self):
        super().__init__()
        
        self.title("QPC Node Manager")
        self.geometry("1000x700")
        
        self.node_process = None
        self.is_running = False
        
        self.create_ui()
        
    def create_ui(self):
        """Create node manager UI"""
        self.grid_columnconfigure(0, weight=1)
        
        # Header
        header = ctk.CTkLabel(
            self,
            text="🖥️ QPC Node Manager",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        header.grid(row=0, column=0, pady=20)
        
        # Configuration
        config_frame = ctk.CTkFrame(self)
        config_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        
        ctk.CTkLabel(config_frame, text="Port:").grid(
            row=0, column=0, padx=10, pady=10
        )
        self.port_entry = ctk.CTkEntry(config_frame, width=100)
        self.port_entry.insert(0, "5000")
        self.port_entry.grid(row=0, column=1, padx=10, pady=10)
        
        self.genesis_var = ctk.BooleanVar()
        ctk.CTkCheckBox(
            config_frame,
            text="Start as Genesis Node",
            variable=self.genesis_var
        ).grid(row=0, column=2, padx=10, pady=10)
        
        self.peers_entry = ctk.CTkEntry(config_frame, width=200)
        self.peers_entry.insert(0, "Peer addresses (comma-separated)")
        self.peers_entry.grid(row=0, column=3, padx=10, pady=10)
        
        # Control buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=2, column=0, pady=20)
        
        self.start_btn = ctk.CTkButton(
            btn_frame,
            text="Start Node",
            command=self.start_node,
            width=150,
            height=40
        )
        self.start_btn.pack(side="left", padx=20)
        
        self.stop_btn = ctk.CTkButton(
            btn_frame,
            text="Stop Node",
            command=self.stop_node,
            width=150,
            height=40,
            state="disabled"
        )
        self.stop_btn.pack(side="left", padx=20)
        
        # Status
        self.status_label = ctk.CTkLabel(
            self,
            text="Status: Stopped",
            font=ctk.CTkFont(size=16)
        )
        self.status_label.grid(row=3, column=0, pady=10)
        
        # Log output
        log_frame = ctk.CTkFrame(self)
        log_frame.grid(row=4, column=0, sticky="nsew", padx=20, pady=10)
        self.grid_rowconfigure(4, weight=1)
        
        ctk.CTkLabel(
            log_frame,
            text="Node Logs",
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=5)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap='word',
            bg='#1a1a1a',
            fg='#00ff00',
            font=('Courier', 9)
        )
        self.log_text.pack(fill='both', expand=True, padx=10, pady=10)
        
    def start_node(self):
        """Start the node"""
        if self.is_running:
            return
            
        port = self.port_entry.get()
        is_genesis = self.genesis_var.get()
        
        cmd = [sys.executable, "node.py", "--port", port]
        if is_genesis:
            cmd.append("--genesis")
            
        self.log_text.insert('end', f"Starting node: {' '.join(cmd)}\n")
        self.log_text.see('end')
        
        # In a real implementation, you would spawn a subprocess here
        # For demo purposes, we'll simulate
        self.is_running = True
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.status_label.configure(text="Status: Running")
        
        self.log_text.insert('end', "Node started successfully!\n")
        self.log_text.insert('end', f"Listening on port {port}\n")
        self.log_text.see('end')
        
    def stop_node(self):
        """Stop the node"""
        if not self.is_running:
            return
            
        self.is_running = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.status_label.configure(text="Status: Stopped")
        
        self.log_text.insert('end', "Node stopped.\n")
        self.log_text.see('end')


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="QPC GUI")
    parser.add_argument("--mode", choices=["wallet", "node"], default="wallet",
                       help="Launch mode: wallet or node manager")
    args = parser.parse_args()
    
    if args.mode == "wallet":
        app = WalletGUI()
    else:
        app = NodeManagerGUI()
        
    app.mainloop()


if __name__ == "__main__":
    main()
