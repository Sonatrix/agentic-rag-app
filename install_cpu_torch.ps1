# PowerShell script to install CPU-only PyTorch
# This script ensures you get the CPU-only version of PyTorch

Write-Host "🤖 CPU-Only PyTorch Installation Script (PowerShell)" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python first." -ForegroundColor Red
    exit 1
}

# Check if pip is available
try {
    $pipVersion = pip --version 2>&1
    Write-Host "✅ pip found: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ pip not found. Please install pip first." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📦 Installing CPU-only PyTorch packages..." -ForegroundColor Yellow
Write-Host "   This will download ~200MB instead of ~2GB (GPU version)" -ForegroundColor Gray

# Install CPU-only PyTorch
Write-Host "🔄 Installing PyTorch CPU..." -ForegroundColor Blue
try {
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
    Write-Host "✅ PyTorch CPU installed successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install PyTorch CPU" -ForegroundColor Red
    exit 1
}

# Install sentence-transformers
Write-Host "🔄 Installing sentence-transformers..." -ForegroundColor Blue
try {
    pip install sentence-transformers
    Write-Host "✅ sentence-transformers installed successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install sentence-transformers" -ForegroundColor Red
    exit 1
}

# Install langchain-huggingface
Write-Host "🔄 Installing langchain-huggingface..." -ForegroundColor Blue
try {
    pip install langchain-huggingface
    Write-Host "✅ langchain-huggingface installed successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install langchain-huggingface" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🧪 Verifying installation..." -ForegroundColor Yellow

# Verify PyTorch
try {
    $verification = python -c "
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CPU support: {torch.cpu.is_available()}')
print(f'CUDA available: {torch.cuda.is_available()}')

from sentence_transformers import SentenceTransformer
print('sentence-transformers: OK')

from langchain_huggingface import HuggingFaceEmbeddings
print('langchain-huggingface: OK')
"
    Write-Host $verification -ForegroundColor Green
    
    Write-Host ""
    Write-Host "🎉 Installation completed successfully!" -ForegroundColor Green
    Write-Host "💡 Benefits of CPU-only PyTorch:" -ForegroundColor Cyan
    Write-Host "   - Smaller download size (~200MB vs ~2GB)" -ForegroundColor Gray
    Write-Host "   - Faster installation" -ForegroundColor Gray
    Write-Host "   - Lower memory usage" -ForegroundColor Gray
    Write-Host "   - Perfect for embedding tasks" -ForegroundColor Gray
    
} catch {
    Write-Host "❌ Verification failed. Some packages may not be installed correctly." -ForegroundColor Red
    Write-Host "Please check the installation manually." -ForegroundColor Red
}

Write-Host ""
Write-Host "🚀 You can now run your RAG application with CPU-based embeddings!" -ForegroundColor Green
