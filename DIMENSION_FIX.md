# Embedding Dimension Compatibility Guide

## 🎯 Quick Fix for "Collection expecting embedding with dimension of 768, got 384" Error

This error happens when you switch embedding models with different dimensions. Here are your options:

## Option 1: Clear Existing Data (Recommended for Development) 🧹

```bash
# Run the cleanup script
python clear_chroma.py

# Then re-ingest your documents
python ingest.py
```

**Pros:** Clean start, use any model you want  
**Cons:** Need to re-ingest all documents  

## Option 2: Switch to Compatible Model (Preserves Data) 🔄

Your existing collection uses **768 dimensions**. Use a compatible model:

```bash
# Set environment variable
set EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2

# Or in .env file
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
```

**Pros:** Keeps existing data  
**Cons:** Larger model (slower, more memory)

## Option 3: Use Auto-Detection (Smart Choice) 🤖

The updated `ingest.py` now automatically detects existing dimensions and chooses a compatible model.

Just run:
```bash
python ingest.py
```

It will automatically use a 768D model to match your existing collection.

## 📊 Model Dimension Reference

| Model | Dimensions | Size | Speed | Quality |
|-------|------------|------|-------|---------|
| `all-MiniLM-L6-v2` | 384 | 80MB | Fast | Good |
| `all-mpnet-base-v2` | 768 | 420MB | Medium | Better |
| `paraphrase-multilingual-MiniLM-L12-v2` | 384 | 420MB | Medium | Good |
| `BAAI/bge-small-en-v1.5` | 384 | 130MB | Fast | Very Good |

## 🔧 Manual Model Selection

Set the `EMBEDDING_MODEL` environment variable:

### For 768D (matches your current collection):
```bash
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
```

### For 384D (requires clearing collection first):
```bash
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

## 🚀 Recommended Workflow

1. **For Development:** Clear collection and use lightweight model
   ```bash
   python clear_chroma.py
   set EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
   python ingest.py
   ```

2. **For Production:** Use auto-detection (maintains existing data)
   ```bash
   python ingest.py  # Will auto-detect and use compatible model
   ```

3. **For Best Quality:** Clear and use high-quality model
   ```bash
   python clear_chroma.py
   set EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
   python ingest.py
   ```

## 🛠️ Troubleshooting

**Still getting dimension errors?**
1. Ensure both `ingest.py` and `vector_store.py` use the same model
2. Clear the ChromaDB collection completely
3. Check for typos in the model name
4. Verify the model exists on Hugging Face

**Want to change models later?**
1. Always clear the collection first: `python clear_chroma.py`
2. Set new model: `set EMBEDDING_MODEL=your-new-model`
3. Re-ingest documents: `python ingest.py`
