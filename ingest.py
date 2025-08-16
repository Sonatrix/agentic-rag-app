import os
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
import chromadb
from tqdm import tqdm
from typing import Optional, Tuple
import chainlit as cl
import time
import asyncio

# Load environment variables
load_dotenv()

# Constants
DATA_DIR = "data"
CHROMA_DB_PATH = "chroma_db"
CHROMA_COLLECTION_NAME = "rag_collection"

# Hugging Face model configuration
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # Fast and lightweight
# Alternative models you can use:
# "sentence-transformers/all-mpnet-base-v2"  # Better quality, slower
# "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"  # Multilingual support
# "BAAI/bge-small-en-v1.5"  # High performance


class DocumentIngestor:
    """
    A class to handle document ingestion into ChromaDB with Hugging Face embeddings.
    """
    
    def __init__(self, progress_callback=None):
        """
        Initialize the document ingestor.
        
        Args:
            progress_callback: Optional callback function for progress updates
        """
        self.embeddings = None
        self.client = None
        self.collection = None
        self.progress_callback = progress_callback
        self._initialize_components()
    
    def _detect_existing_dimensions(self) -> Optional[int]:
        """Detect the embedding dimensions of existing collection."""
        try:
            if self.collection.count() > 0:
                # Get a sample document to check dimensions
                sample = self.collection.get(limit=1, include=['embeddings'])
                if sample['embeddings'] and len(sample['embeddings']) > 0:
                    return len(sample['embeddings'][0])
            return None
        except Exception:
            return None
    
    def _get_compatible_model(self, target_dimensions: Optional[int] = None) -> str:
        """Get a compatible embedding model based on existing collection dimensions."""
        
        # Check environment variable first
        env_model = os.getenv("EMBEDDING_MODEL")
        if env_model:
            return env_model
        
        # If we have target dimensions, pick compatible model
        if target_dimensions == 768:
            return "sentence-transformers/all-mpnet-base-v2"  # 768 dims
        elif target_dimensions == 384:
            return "sentence-transformers/all-MiniLM-L6-v2"  # 384 dims
        else:
            # Default for new collections
            return DEFAULT_EMBEDDING_MODEL
    
    def _initialize_components(self):
        """Initialize ChromaDB and embeddings with dimension compatibility check."""
        try:
            # Initialize ChromaDB first to check existing dimensions
            self.client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
            self.collection = self.client.get_or_create_collection(name=CHROMA_COLLECTION_NAME)
            
            # Check existing dimensions
            existing_dims = self._detect_existing_dimensions()
            if existing_dims:
                print(f"📏 Detected existing embeddings with {existing_dims} dimensions")
            
            # Get compatible model
            model_name = self._get_compatible_model(existing_dims)
            
            # Use progress callback if available
            if hasattr(self, 'progress_callback') and self.progress_callback:
                self.progress_callback(10, "model_setup", f"📦 Loading embedding model: {model_name}")
                if existing_dims:
                    self.progress_callback(20, "model_setup", f"🔗 Matching existing {existing_dims}D embeddings")
                else:
                    self.progress_callback(20, "model_setup", "⏳ First run - downloading model...")
            else:
                print(f"📦 Loading embedding model: {model_name}")
                if existing_dims:
                    print(f"🔗 Selected to match existing {existing_dims}D embeddings")
                else:
                    print("⏳ This may take a moment on first run...")
            
            # Load embeddings with progress tracking
            from src.vector_store import create_embeddings_with_progress
            
            def embedding_progress(progress, stage, description):
                if hasattr(self, 'progress_callback') and self.progress_callback:
                    # Map embedding progress to overall progress (30-60%)
                    overall_progress = 30 + (progress * 0.3)
                    self.progress_callback(int(overall_progress), f"embedding_{stage}", description)
            
            self.embeddings = create_embeddings_with_progress(model_name, embedding_progress)
            
            # Verify dimensions match
            if hasattr(self, 'progress_callback') and self.progress_callback:
                self.progress_callback(65, "model_verify", "🔍 Verifying model compatibility...")
            
            test_embedding = self.embeddings.embed_query("test")
            new_dims = len(test_embedding)
            
            if existing_dims and existing_dims != new_dims:
                error_msg = f"""
❌ Dimension mismatch detected!
   Existing collection: {existing_dims} dimensions
   New model: {new_dims} dimensions
   
💡 Solutions:
   1. Run: python clear_chroma.py (clears existing data)
   2. Set EMBEDDING_MODEL environment variable to a {existing_dims}D model
   3. Use a different collection name
                """
                if hasattr(self, 'progress_callback') and self.progress_callback:
                    self.progress_callback(0, "error", "❌ Dimension mismatch detected!")
                raise Exception(error_msg)
            
            if hasattr(self, 'progress_callback') and self.progress_callback:
                self.progress_callback(70, "model_ready", f"✅ Model ready: {model_name} ({new_dims}D)")
            else:
                print(f"✅ Successfully loaded embedding model: {model_name}")
                print(f"📐 Embedding dimensions: {new_dims}")
            print(f"✅ Connected to ChromaDB at: {CHROMA_DB_PATH}")
            
        except Exception as e:
            raise Exception(f"Error initializing components: {e}")
    
    def _get_processing_steps(self) -> list[Tuple[str, int, str]]:
        """Get the processing steps with their progress percentages and descriptions."""
        return [
            ("Loading PDF document", 10, "📖 Reading the PDF file and extracting content..."),
            ("Splitting into chunks", 25, "✂️ Breaking document into manageable pieces..."),
            ("Processing chunks", 45, "📝 Analyzing and preparing text chunks..."),
            ("Generating embeddings", 75, "🧠 Creating AI embeddings for semantic search..."),
            ("Storing in database", 90, "💾 Saving to vector database..."),
            ("Finalizing", 100, "✅ Process completed successfully!")
        ]
    
    def _create_progress_visual(self, percentage: int, width: int = 30) -> str:
        """Create a visual progress bar for terminal output."""
        filled = int(percentage * width // 100)
        empty = width - filled
        return f"[{'█' * filled}{'░' * empty}] {percentage}%"
    
    async def ingest_pdf(self, pdf_path: str, progress_callback: Optional[callable] = None) -> bool:
        """
        Ingest a single PDF file into the vector store with detailed progress tracking.
        
        Args:
            pdf_path: Path to the PDF file
            progress_callback: Optional callback function for progress updates (message, percentage, description)
            
        Returns:
            bool: True if successful, False otherwise
        """
        steps = self._get_processing_steps()
        start_time = time.time()
        
        try:
            for i, (step_name, percentage, description) in enumerate(steps):
                if progress_callback:
                    await progress_callback(step_name, percentage, description)
                
                # Add small delay only for visual feedback, but reduce it to prevent payload issues
                if i < len(steps) - 1:
                    await asyncio.sleep(0.1)  # Reduced from 0.2 to 0.1
                
                if step_name == "Loading PDF document":
                    # Load PDF
                    loader = PyPDFLoader(pdf_path)
                    documents = loader.load()
                    
                elif step_name == "Splitting into chunks":
                    # Split document into chunks
                    text_splitter = RecursiveCharacterTextSplitter(
                        chunk_size=1000, 
                        chunk_overlap=200,
                        length_function=len,
                        is_separator_regex=False,
                    )
                    chunks = text_splitter.split_documents(documents)
                    
                    if not chunks:
                        raise Exception("No content found in PDF")
                    
                elif step_name == "Processing chunks":
                    # Get text from chunks
                    chunk_texts = [chunk.page_content for chunk in chunks]
                    
                    # Update progress with chunk info (but don't send extra updates)
                    if progress_callback and len(chunks) > 0:
                        detailed_desc = f"📝 Processing {len(chunks)} text chunks from the document..."
                        # Don't send another progress update here to avoid too many packets
                    
                elif step_name == "Generating embeddings":
                    # Generate embeddings with Hugging Face (this is usually the slowest step)
                    print(f"🧠 Generating embeddings for {len(chunk_texts)} chunks...")
                    chunk_embeddings = self.embeddings.embed_documents(chunk_texts)
                    
                    # Create IDs for chunks
                    filename = os.path.basename(pdf_path)
                    chunk_ids = [f"{filename}-{i}" for i in range(len(chunks))]
                    
                elif step_name == "Storing in database":
                    # Add to ChromaDB
                    self.collection.add(
                        ids=chunk_ids,
                        embeddings=chunk_embeddings,
                        documents=chunk_texts,
                        metadatas=[chunk.metadata for chunk in chunks],
                    )
                    
                elif step_name == "Finalizing":
                    # Calculate processing time
                    processing_time = time.time() - start_time
                    filename = os.path.basename(pdf_path)
                    
                    if progress_callback:
                        final_desc = f"🎉 Successfully processed {len(chunks)} chunks from '{filename}' in {processing_time:.1f}s"
                        await progress_callback(step_name, percentage, final_desc)
                        
                    # Add a final small delay to ensure the last update is processed
                    await asyncio.sleep(0.1)
            
            return True
            
        except Exception as e:
            if progress_callback:
                error_desc = f"❌ Processing failed: {str(e)}"
                await progress_callback("Error", -1, error_desc)
            return False
    
    def ingest_all_pdfs(self) -> bool:
        """
        Ingest all PDF files in the data directory with progress tracking.
        
        Returns:
            bool: True if all files processed successfully
        """
        if not os.path.exists(DATA_DIR):
            print(f"Data directory '{DATA_DIR}' not found.")
            return False
        
        pdf_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".pdf")]
        if not pdf_files:
            print("No PDF files found in data directory.")
            return True
        
        print(f"Found {len(pdf_files)} PDF file(s) to process:")
        for i, filename in enumerate(pdf_files, 1):
            print(f"  {i}. {filename}")
        print()
        
        success_count = 0
        
        # Use tqdm for file-level progress, and custom progress for each file
        for file_idx, filename in enumerate(tqdm(pdf_files, desc="Processing PDFs", unit="file")):
            pdf_path = os.path.join(DATA_DIR, filename)
            
            print(f"\n📄 Processing: {filename}")
            print("-" * 50)
            
            try:
                # Create a simple progress callback for batch processing
                async def batch_progress_callback(step_name: str, percentage: int, description: str):
                    progress_visual = self._create_progress_visual(percentage)
                    print(f"\r{progress_visual} {step_name}", end="", flush=True)
                    if percentage == 100:
                        print()  # New line after completion
                
                # Use synchronous version for batch processing
                result = asyncio.run(self.ingest_pdf(pdf_path, batch_progress_callback))
                
                if result:
                    success_count += 1
                    print(f"✅ Successfully processed {filename}")
                else:
                    print(f"❌ Failed to process {filename}")
                    
            except Exception as e:
                print(f"❌ Error processing file {filename}: {e}")
        
        print(f"\n🎯 Summary: Processed {success_count}/{len(pdf_files)} files successfully.")
        
        if success_count == len(pdf_files):
            print("🎉 All files processed successfully!")
        elif success_count > 0:
            print(f"⚠️ {len(pdf_files) - success_count} files failed to process.")
        else:
            print("❌ No files were processed successfully.")
            
        return success_count == len(pdf_files)


def main():
    """
    Main function for command-line usage.
    """
    ingestor = DocumentIngestor()
    ingestor.ingest_all_pdfs()


if __name__ == "__main__":
    main()
