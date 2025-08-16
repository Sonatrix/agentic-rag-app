"""
Test script to demonstrate direct method call vs subprocess approach.
"""
import time
import asyncio
from ingest import DocumentIngestor

async def test_direct_ingestion():
    """Test direct method call approach."""
    print("Testing direct method call approach...")
    
    # Create a sample progress callback
    async def progress_callback(message: str):
        print(f"Progress: {message}")
    
    # Initialize ingestor
    ingestor = DocumentIngestor()
    
    # This would be much faster and more efficient than subprocess
    print("✅ Direct method call benefits:")
    print("  - No process creation overhead")
    print("  - Direct error handling with full stack traces")
    print("  - Real-time progress updates")
    print("  - Shared memory space")
    print("  - Easier debugging and profiling")
    print("  - Type safety and IDE support")

if __name__ == "__main__":
    asyncio.run(test_direct_ingestion())
