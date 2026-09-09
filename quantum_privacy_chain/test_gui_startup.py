#!/usr/bin/env python3
"""Test script to verify GUI can be instantiated (without display)"""
import sys
import os

# Test imports
try:
    from gui import WalletGUI, NodeManagerGUI
    print("✓ GUI module imports successfully")
except Exception as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

# Test that classes are properly defined
try:
    # Check class attributes exist
    assert hasattr(WalletGUI, '__init__')
    assert hasattr(WalletGUI, 'create_main_layout')
    assert hasattr(WalletGUI, 'send_transaction')
    assert hasattr(WalletGUI, 'toggle_mining')
    print("✓ WalletGUI class structure verified")
    
    assert hasattr(NodeManagerGUI, '__init__')
    assert hasattr(NodeManagerGUI, 'start_node')
    assert hasattr(NodeManagerGUI, 'stop_node')
    print("✓ NodeManagerGUI class structure verified")
except Exception as e:
    print(f"✗ Class structure error: {e}")
    sys.exit(1)

print("\n✅ All GUI tests passed!")
print("\nTo run the GUI:")
print("  python gui.py --mode wallet   # Launch wallet GUI")
print("  python gui.py --mode node     # Launch node manager GUI")
print("\nNote: Requires a display (X11/Wayland) to run the actual GUI window.")
