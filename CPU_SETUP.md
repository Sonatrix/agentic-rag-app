# CPU-Only PyTorch Setup Guide

This guide helps you set up the RAG application with CPU-only PyTorch, which is lighter and faster to install.

## 🎯 Benefits of CPU-Only PyTorch

- **Smaller Download**: ~200MB instead of ~2GB (GPU version)
- **Faster Installation**: No CUDA dependencies
- **Lower Memory Usage**: More efficient for embedding tasks
- **Universal Compatibility**: Works on any machine
- **Perfect for RAG**: Embeddings don't need GPU acceleration

## 🚀 Quick Installation

### Option 1: Automated Script (Recommended)

**For Windows PowerShell:**
```powershell
# Run the automated installation script
.\install_cpu_torch.ps1
```

**For Python:**
```bash
# Run the Python installation script
python install_cpu_torch.py
```

### Option 2: Manual Installation

```bash
# Install CPU-only PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install other dependencies
pip install sentence-transformers langchain-huggingface
```

### Option 3: Using UV (if you're using UV package manager)

```bash
# Install all dependencies with CPU-only PyTorch
uv add torch --index https://download.pytorch.org/whl/cpu
uv add sentence-transformers langchain-huggingface
```

## 🔧 Configuration

### Embedding Model Options

You can configure which Hugging Face model to use by setting the `EMBEDDING_MODEL` environment variable:

```bash
# Default (fast and lightweight)
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Better quality (slower)
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2

# Multilingual support
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

# High performance
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
```

### Environment Variables

Create a `.env` file with:

```env
# Optional: Specify embedding model (defaults to all-MiniLM-L6-v2)
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Keep your Google API key for the LLM
GOOGLE_API_KEY=your_google_api_key_here
```

## 🧪 Verification

After installation, verify everything works:

```python
# Test PyTorch CPU installation
import torch
print(f"PyTorch version: {torch.__version__}")
print(f"CPU available: {torch.cpu.is_available()}")
print(f"CUDA available: {torch.cuda.is_available()}")  # Should be False

# Test Hugging Face embeddings
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'}
)

# Test embedding generation
test_embedding = embeddings.embed_query("Hello, world!")
print(f"Embedding dimension: {len(test_embedding)}")
print("✅ Hugging Face embeddings working!")
```

## 📊 Performance Comparison

| Aspect | CPU-Only PyTorch | GPU PyTorch |
|--------|------------------|-------------|
| Download Size | ~200MB | ~2GB |
| Memory Usage | Lower | Higher |
| Installation Time | 2-5 minutes | 10-20 minutes |
| Embedding Speed | Good | Excellent |
| Setup Complexity | Simple | Complex |
| Hardware Requirements | Any CPU | NVIDIA GPU |

## 🔍 Model Recommendations

### For Speed (Default)
- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Size**: 80MB
- **Dimensions**: 384
- **Best for**: Fast prototyping, small documents

### For Quality
- **Model**: `sentence-transformers/all-mpnet-base-v2`
- **Size**: 420MB
- **Dimensions**: 768
- **Best for**: Production use, better accuracy

### For Multilingual
- **Model**: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- **Size**: 420MB
- **Dimensions**: 384
- **Best for**: Non-English documents

### For Performance
- **Model**: `BAAI/bge-small-en-v1.5`
- **Size**: 130MB
- **Dimensions**: 384
- **Best for**: High performance retrieval

## 🚀 Running the Application

After installation, run your RAG application as usual:

```bash
# Start the application
chainlit run app.py

# Or with UV
uv run chainlit run app.py
```

## 🛠️ Troubleshooting

### Common Issues

1. **"No module named 'torch'"**
   ```bash
   pip install torch --index-url https://download.pytorch.org/whl/cpu
   ```

2. **"CUDA not available" warnings**
   - This is normal and expected for CPU-only installation
   - No action needed

3. **Slow embedding generation**
   - Try a smaller model like `all-MiniLM-L6-v2`
   - Reduce batch size in configuration

4. **Memory issues**
   - Use a smaller embedding model
   - Reduce chunk size in document processing

### Performance Tips

1. **Choose the right model**: Balance between speed and quality
2. **Optimize chunk size**: Smaller chunks = faster processing
3. **Use batch processing**: Process multiple documents together
4. **Monitor memory**: CPU models are more memory-efficient

## 📚 Additional Resources

- [PyTorch CPU Installation](https://pytorch.org/get-started/locally/)
- [Sentence Transformers Models](https://www.sbert.net/docs/pretrained_models.html)
- [Hugging Face Model Hub](https://huggingface.co/models?library=sentence-transformers)

## 🎉 You're Ready!

Your RAG application is now configured to use CPU-only PyTorch with Hugging Face embeddings. This setup is:

- ✅ Lightweight and fast to install
- ✅ Compatible with any hardware
- ✅ Perfect for document embedding tasks
- ✅ Easy to deploy and maintain

Happy embedding! 🚀
