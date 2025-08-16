#!/usr/bin/env python3
"""
Installation script for CPU-only PyTorch and dependencies.
This ensures we get the CPU-only version of PyTorch which is much smaller.
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"📦 {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}:")
        print(f"   Command: {command}")
        print(f"   Error: {e.stderr}")
        return False

def install_cpu_torch():
    """Install CPU-only PyTorch packages."""
    print("🚀 Installing CPU-only PyTorch and dependencies...")
    print("=" * 50)
    
    # Commands to install CPU-only PyTorch
    commands = [
        {
            "cmd": "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu",
            "desc": "Installing CPU-only PyTorch"
        },
        {
            "cmd": "pip install sentence-transformers",
            "desc": "Installing sentence-transformers"
        },
        {
            "cmd": "pip install langchain-huggingface",
            "desc": "Installing LangChain Hugging Face integration"
        }
    ]
    
    success_count = 0
    for cmd_info in commands:
        if run_command(cmd_info["cmd"], cmd_info["desc"]):
            success_count += 1
    
    print(f"\n🎯 Installation Summary: {success_count}/{len(commands)} packages installed successfully")
    
    if success_count == len(commands):
        print("🎉 All packages installed successfully!")
        print("\n💡 Benefits of CPU-only PyTorch:")
        print("   - Smaller download size (~200MB vs ~2GB)")
        print("   - Faster installation")
        print("   - Lower memory usage")
        print("   - Suitable for embedding tasks")
        return True
    else:
        print("⚠️ Some packages failed to install. Please check the errors above.")
        return False

def verify_installation():
    """Verify that the installation works correctly."""
    print("\n🧪 Verifying installation...")
    
    try:
        import torch
        print(f"✅ PyTorch version: {torch.__version__}")
        print(f"✅ PyTorch CPU support: {torch.cpu.is_available()}")
        print(f"✅ CUDA available: {torch.cuda.is_available()} (Expected: False for CPU-only)")
        
        from sentence_transformers import SentenceTransformer
        print("✅ Sentence Transformers imported successfully")
        
        from langchain_huggingface import HuggingFaceEmbeddings
        print("✅ LangChain Hugging Face integration imported successfully")
        
        print("\n🎉 All components verified successfully!")
        print("💡 Your setup is ready for CPU-based embeddings!")
        
        return True
        
    except ImportError as e:
        print(f"❌ Verification failed: {e}")
        print("   Please run the installation again or install missing packages manually.")
        return False

if __name__ == "__main__":
    print("🤖 CPU-Only PyTorch Installation Script")
    print("=" * 50)
    
    # Check if we're in a virtual environment (recommended)
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: You're not in a virtual environment.")
        print("   It's recommended to use a virtual environment for this installation.")
        response = input("   Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("   Installation cancelled. Please create a virtual environment first.")
            sys.exit(1)
    
    # Install packages
    if install_cpu_torch():
        # Verify installation
        verify_installation()
    else:
        print("❌ Installation failed. Please check the errors and try again.")
        sys.exit(1)
