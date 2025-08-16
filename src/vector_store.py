import chromadb
from langchain_huggingface import HuggingFaceEmbeddings
import os
import sys
from tqdm import tqdm
import time


# Constants
CHROMA_DB_PATH = "chroma_db"
CHROMA_COLLECTION_NAME = "rag_collection"
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def create_embeddings_with_progress(model_name: str = None, progress_callback=None):
    """
    Create HuggingFace embeddings with download progress tracking.
    
    Args:
        model_name: Name of the embedding model
        progress_callback: Callback function to report progress
    """
    if model_name is None:
        model_name = os.getenv("EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)
    
    # Check if model is already cached
    from transformers import AutoModel
    import torch
    
    try:
        # Try to load model to see if it's cached
        model_cache_dir = os.path.expanduser("~/.cache/huggingface/transformers")
        model_cached = False
        
        if os.path.exists(model_cache_dir):
            # Simple check - if any files exist for this model
            cached_files = [f for f in os.listdir(model_cache_dir) if model_name.replace("/", "--") in f]
            model_cached = len(cached_files) > 0
        
        if progress_callback and not model_cached:
            progress_callback(0, "download", "🔄 Downloading embedding model...")
            progress_callback(25, "download", f"📥 Fetching {model_name}...")
        
        # Create embeddings with progress simulation
        embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={
                'device': 'cpu',  # Use CPU for consistency
                'trust_remote_code': False,
            },
            encode_kwargs={
                'normalize_embeddings': True,  # Must match ingest.py settings
                'batch_size': 32,
            }
        )
        
        if progress_callback and not model_cached:
            progress_callback(75, "download", "🔧 Initializing model...")
            time.sleep(0.5)  # Small delay for visual feedback
            progress_callback(100, "download", "✅ Embedding model ready!")
        elif progress_callback:
            progress_callback(100, "cached", "📂 Using cached embedding model")
        
        return embeddings
        
    except Exception as e:
        if progress_callback:
            progress_callback(0, "error", f"❌ Failed to load model: {str(e)}")
        raise


class VectorStore:
    """
    A class to interact with a ChromaDB vector store using Hugging Face embeddings.
    """

    def __init__(self, progress_callback=None):
        """
        Initializes the VectorStore with Hugging Face embeddings.
        
        Args:
            progress_callback: Optional callback for tracking embedding model download
        """
        self.client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        self.collection = self.client.get_or_create_collection(name=CHROMA_COLLECTION_NAME)
        
        # Initialize Hugging Face embeddings with progress tracking
        model_name = os.getenv("EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)
        self.embeddings = create_embeddings_with_progress(model_name, progress_callback)

    def search(self, query: str, n_results: int = 5) -> list[str]:
        """
        Searches the vector store for the most similar documents to a given query.

        Args:
            query: The query to search for.
            n_results: The number of results to return.

        Returns:
            A list of the most similar documents.
        """
        query_embedding = self.embeddings.embed_query(query)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
        )
        return results["documents"][0] if results["documents"] else []
