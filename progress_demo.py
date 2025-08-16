"""
Demo script to showcase the progress bar functionality.
This shows what users will see during PDF ingestion.
"""

import asyncio
import time

async def demo_progress_bar():
    """Demonstrate the progress bar that users will see."""
    
    print("🚀 PDF Ingestion Progress Bar Demo")
    print("=" * 50)
    
    steps = [
        ("Loading PDF document", 10, "📖 Reading the PDF file and extracting content..."),
        ("Splitting into chunks", 25, "✂️ Breaking document into manageable pieces..."),
        ("Processing chunks", 45, "📝 Analyzing and preparing text chunks..."),
        ("Generating embeddings", 75, "🧠 Creating AI embeddings for semantic search..."),
        ("Storing in database", 90, "💾 Saving to vector database..."),
        ("Finalizing", 100, "✅ Process completed successfully!")
    ]
    
    for step_name, percentage, description in steps:
        # Create progress bar visual (20 segments)
        filled = int(percentage // 5)
        empty = 20 - filled
        progress_bar = "🟩" * filled + "⬜" * empty
        
        step_indicator = "🔄" if percentage < 100 else "✅"
        
        # Clear screen and show progress
        print("\033[2J\033[H")  # Clear screen
        print(f"""
📄 **Processing: sample_document.pdf**

{progress_bar} **{percentage}%**

{step_indicator} **{step_name}**
{description}

Progress Details:
- Current Step: {step_name}
- Progress: {percentage}%
- Status: {description}
        """.strip())
        
        # Simulate processing time
        if percentage < 100:
            await asyncio.sleep(1.5)
    
    print("\n🎉 Processing complete! Your document is now ready for questions.")

if __name__ == "__main__":
    asyncio.run(demo_progress_bar())
