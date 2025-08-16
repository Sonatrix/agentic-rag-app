"""
Script to clear ChromaDB collection when switching embedding models.
Use this when you change embedding models and get dimension mismatch errors.
"""

import chromadb
import os
import shutil
from pathlib import Path

# Constants (same as in ingest.py)
CHROMA_DB_PATH = "chroma_db"
CHROMA_COLLECTION_NAME = "rag_collection"

def clear_chroma_collection():
    """Clear the existing ChromaDB collection to allow new embedding dimensions."""
    
    print("🧹 ChromaDB Collection Reset Tool")
    print("=" * 50)
    
    if not os.path.exists(CHROMA_DB_PATH):
        print(f"✅ No existing ChromaDB found at {CHROMA_DB_PATH}")
        print("   You can proceed with ingestion directly.")
        return True
    
    print(f"📂 Found existing ChromaDB at: {CHROMA_DB_PATH}")
    print(f"🗃️  Collection name: {CHROMA_COLLECTION_NAME}")
    
    # Ask for confirmation
    print("\n⚠️  WARNING: This will delete all existing document embeddings!")
    print("   You'll need to re-ingest all your PDF documents.")
    
    response = input("\n❓ Do you want to proceed? (y/N): ").strip().lower()
    
    if response != 'y':
        print("❌ Operation cancelled. Collection remains unchanged.")
        return False
    
    try:
        # Method 1: Try to delete the collection via ChromaDB API
        print("\n🔄 Attempting to delete collection via ChromaDB API...")
        try:
            client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
            client.delete_collection(name=CHROMA_COLLECTION_NAME)
            print(f"✅ Successfully deleted collection '{CHROMA_COLLECTION_NAME}'")
        except Exception as e:
            print(f"⚠️  API deletion failed: {e}")
            print("   Falling back to directory removal...")
            
            # Method 2: Remove the entire ChromaDB directory
            if os.path.exists(CHROMA_DB_PATH):
                shutil.rmtree(CHROMA_DB_PATH)
                print(f"✅ Successfully removed ChromaDB directory: {CHROMA_DB_PATH}")
        
        print("\n🎉 ChromaDB collection cleared successfully!")
        print("💡 Next steps:")
        print("   1. Run your ingestion script: python ingest.py")
        print("   2. Or upload PDFs through the Chainlit interface")
        print("   3. New embeddings will use the correct dimensions")
        
        return True
        
    except Exception as e:
        print(f"❌ Error clearing ChromaDB: {e}")
        print("\n🛠️  Manual cleanup steps:")
        print(f"   1. Stop your application")
        print(f"   2. Delete the folder: {CHROMA_DB_PATH}")
        print(f"   3. Restart your application")
        return False

def show_collection_info():
    """Show information about the current collection."""
    
    if not os.path.exists(CHROMA_DB_PATH):
        print("📂 No ChromaDB found.")
        return
    
    try:
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        collections = client.list_collections()
        
        print("📊 ChromaDB Information:")
        print(f"   Path: {CHROMA_DB_PATH}")
        print(f"   Collections: {len(collections)}")
        
        for collection in collections:
            print(f"   - {collection.name}: {collection.count()} documents")
            
    except Exception as e:
        print(f"❌ Error reading ChromaDB info: {e}")

if __name__ == "__main__":
    print("🔧 ChromaDB Management Tool")
    print("=" * 30)
    
    # Show current state
    show_collection_info()
    print()
    
    # Clear collection
    clear_chroma_collection()
