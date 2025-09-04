#!/usr/bin/env python3
"""
Installation script for Synapse Engine ComfyUI Custom Node
This script handles the Node.js dependencies installation automatically.
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, cwd=None, check=True):
    """Run a command and handle errors appropriately"""
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, cwd=cwd, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        if check:
            raise
        return e

def install_synapse_engine():
    """Install the Synapse Engine dependencies"""
    print("Installing Synapse Engine for ComfyUI...")
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.absolute()
    print(f"Installing in: {script_dir}")
    
    # Check if Node.js is available
    try:
        result = run_command(['node', '--version'])
        print(f"Node.js version: {result.stdout.strip()}")
    except subprocess.CalledProcessError:
        print("ERROR: Node.js is not installed or not in PATH.")
        print("Please install Node.js (https://nodejs.org/) and try again.")
        sys.exit(1)
    
    # Check if npm is available
    try:
        result = run_command(['npm', '--version'])
        print(f"npm version: {result.stdout.strip()}")
    except subprocess.CalledProcessError:
        print("ERROR: npm is not installed or not in PATH.")
        print("Please install npm and try again.")
        sys.exit(1)
    
    # Install Node.js dependencies
    print("Installing Node.js dependencies...")
    run_command(['npm', 'install'], cwd=script_dir)
    
    # Build the TypeScript project
    print("Building TypeScript project...")
    run_command(['npm', 'run', 'build'], cwd=script_dir)
    
    # Test the installation
    print("Testing installation...")
    test_result = run_command(['node', 'dist/index.js', '--count', '1'], cwd=script_dir, check=False)
    
    if test_result.returncode == 0:
        print("✅ Synapse Engine installation completed successfully!")
        print("The node should now be available in ComfyUI under 'text/synapse'")
    else:
        print("⚠️  Installation completed but test failed.")
        print("This might be normal if config files need adjustment.")
        print("Check the ComfyUI console for any error messages.")

if __name__ == "__main__":
    install_synapse_engine()