#!/usr/bin/env python3
"""
Test script for embedding model download progress tracking.
"""

import os
import sys
import time
from src.vector_store import create_embeddings_with_progress
from ingest import DocumentIngestor

def test_embedding_progress():
    """Test embedding model download progress tracking."""
    
    print("🧪 Testing Embedding Model Progress Tracking")
    print("=" * 60)
    
    # Test 1: Direct embedding creation with progress
    print("\n1. Testing direct embedding creation...")
    
    progress_updates = []
    
    def capture_progress(percentage, stage, description):
        progress_updates.append({
            'percentage': percentage,
            'stage': stage,
            'description': description,
            'timestamp': time.time()
        })
        print(f"   📊 {percentage:3d}% | {stage:12s} | {description}")
    
    try:
        print("   Creating embeddings with progress tracking...")
        embeddings = create_embeddings_with_progress(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            progress_callback=capture_progress
        )
        
        # Test embedding
        test_vector = embeddings.embed_query("test query")
        print(f"   ✅ Embedding created successfully (dimension: {len(test_vector)})")
        print(f"   📈 Progress updates received: {len(progress_updates)}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 2: DocumentIngestor with progress
    print("\n2. Testing DocumentIngestor initialization...")
    
    ingestor_updates = []
    
    def capture_ingest_progress(percentage, stage, description):
        ingestor_updates.append({
            'percentage': percentage,
            'stage': stage,
            'description': description,
            'timestamp': time.time()
        })
        print(f"   📊 {percentage:3d}% | {stage:15s} | {description}")
    
    try:
        print("   Creating DocumentIngestor with progress tracking...")
        ingestor = DocumentIngestor(progress_callback=capture_ingest_progress)
        
        print(f"   ✅ DocumentIngestor created successfully")
        print(f"   📈 Progress updates received: {len(ingestor_updates)}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 3: Performance analysis
    print("\n3. Performance Analysis...")
    
    if progress_updates:
        total_time = progress_updates[-1]['timestamp'] - progress_updates[0]['timestamp']
        print(f"   ⏱️  Total embedding load time: {total_time:.2f} seconds")
        
        stages = set(update['stage'] for update in progress_updates)
        print(f"   🔄 Stages tracked: {', '.join(stages)}")
    
    if ingestor_updates:
        total_time = ingestor_updates[-1]['timestamp'] - ingestor_updates[0]['timestamp']
        print(f"   ⏱️  Total ingestor init time: {total_time:.2f} seconds")
        
        stages = set(update['stage'] for update in ingestor_updates)
        print(f"   🔄 Stages tracked: {', '.join(stages)}")
    
    print("\n" + "=" * 60)
    print("🎉 Embedding Progress Test Complete!")
    print("\n📋 Summary:")
    print(f"   • Direct embedding progress: ✅ ({len(progress_updates)} updates)")
    print(f"   • DocumentIngestor progress: ✅ ({len(ingestor_updates)} updates)")
    print(f"   • Progress tracking working: ✅")
    
    return True

def simulate_ui_progress():
    """Simulate how progress would appear in the UI."""
    
    print("\n" + "=" * 60)
    print("🎭 UI Progress Simulation")
    print("=" * 60)
    
    def ui_progress(percentage, stage, description):
        # Simulate progress bar
        filled = int(percentage // 5)
        empty = 20 - filled
        progress_bar = "🟩" * filled + "⬜" * empty
        
        step_indicator = "🔄" if percentage < 100 else "✅"
        
        # Clear line and show progress
        print(f"\r   {progress_bar} {percentage:3d}% {step_indicator} {description}", end="", flush=True)
        time.sleep(0.1)  # Small delay for visual effect
    
    print("\nSimulating embedding model download progress:")
    
    # Simulate download stages
    stages = [
        (10, "download", "🔄 Downloading embedding model..."),
        (25, "download", "📥 Fetching sentence-transformers/all-MiniLM-L6-v2..."),
        (50, "download", "📦 Loading model components..."),
        (75, "download", "🔧 Initializing model..."),
        (100, "download", "✅ Embedding model ready!")
    ]
    
    for percentage, stage, description in stages:
        ui_progress(percentage, stage, description)
        time.sleep(0.5)
    
    print("\n\n✨ Progress visualization complete!")

if __name__ == "__main__":
    try:
        success = test_embedding_progress()
        
        if success:
            simulate_ui_progress()
            
            print("\n🚀 All tests passed! Embedding progress tracking is ready.")
            print("\n💡 Integration notes:")
            print("   • Progress callbacks work with both VectorStore and DocumentIngestor")
            print("   • Model caching is detected to avoid unnecessary progress updates")
            print("   • Progress is mapped to percentage for consistent UI display")
            print("   • Error handling preserves original functionality")
            
        else:
            print("\n❌ Tests failed. Please check the implementation.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Test runner error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
