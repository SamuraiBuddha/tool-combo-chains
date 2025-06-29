#!/usr/bin/env python3
"""
Debug script to capture raw stdout from hybrid memory MCP server
This will help identify what's causing the JSON parse error
"""
import subprocess
import sys
import os

# Set up environment
env = os.environ.copy()

# Run the MCP server and capture raw output
process = subprocess.Popen(
    [sys.executable, '-m', 'tool_combo_chains.mcp_hybrid_memory'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    env=env,
    text=False  # Get raw bytes
)

print("Capturing first 100 bytes of stdout...")
try:
    # Read first 100 bytes
    raw_output = process.stdout.read(100)
    print(f"\nRaw bytes: {raw_output}")
    print(f"As hex: {raw_output.hex()}")
    
    # Try to decode as text
    try:
        text = raw_output.decode('utf-8')
        print(f"As text: {repr(text)}")
        print(f"First 10 chars: {repr(text[:10])}")
        
        # Check what's at position 4
        if len(text) > 4:
            print(f"\nCharacter at position 4 (0-indexed): {repr(text[4])}")
            print(f"Characters 0-9: {repr(text[0:10])}")
    except:
        print("Could not decode as UTF-8")
        
finally:
    process.terminate()
    process.wait()

print("\nChecking stderr for any output...")
stderr = process.stderr.read(1000)
if stderr:
    print(f"Stderr: {stderr.decode('utf-8', errors='replace')}")
