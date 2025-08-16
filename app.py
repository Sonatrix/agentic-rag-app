import chainlit as cl
from langchain_core.messages import HumanMessage, AIMessage
from src.agent import RAGAgent
from src.vector_store import VectorStore
from ingest import DocumentIngestor
import os
import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

DATA_DIR = "data"
CHAT_HISTORY_DIR = "chat_history"

# Ensure chat history directory exists
if not os.path.exists(CHAT_HISTORY_DIR):
    os.makedirs(CHAT_HISTORY_DIR)

def generate_chat_title(first_message: str) -> str:
    """Generate a chat title from the first user message."""
    # Take first 50 characters and clean up
    title = first_message.strip()[:50]
    if len(first_message) > 50:
        title += "..."
    
    # Remove newlines and extra spaces
    title = " ".join(title.split())
    
    # If empty or too short, use timestamp
    if len(title.strip()) < 3:
        title = f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    return title

def save_chat_history(chat_id: str, messages: List[Dict], title: str):
    """Save chat history to file."""
    try:
        chat_data = {
            "id": chat_id,
            "title": title,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "messages": messages
        }
        
        file_path = os.path.join(CHAT_HISTORY_DIR, f"{chat_id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(chat_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving chat history: {e}")

def load_chat_history(chat_id: str) -> Optional[Dict]:
    """Load chat history from file."""
    try:
        file_path = os.path.join(CHAT_HISTORY_DIR, f"{chat_id}.json")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading chat history: {e}")
    return None

def get_recent_chats(limit: int = 10) -> List[Dict]:
    """Get list of recent chats."""
    try:
        chat_files = []
        for filename in os.listdir(CHAT_HISTORY_DIR):
            if filename.endswith('.json'):
                file_path = os.path.join(CHAT_HISTORY_DIR, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    chat_data = json.load(f)
                    chat_files.append({
                        "id": chat_data.get("id", filename[:-5]),
                        "title": chat_data.get("title", "Untitled Chat"),
                        "updated_at": chat_data.get("updated_at", ""),
                        "message_count": len(chat_data.get("messages", []))
                    })
        
        # Sort by updated_at descending
        chat_files.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return chat_files[:limit]
    
    except Exception as e:
        print(f"Error getting recent chats: {e}")
        return []

async def initialize_agent_with_progress() -> RAGAgent:
    """Initialize the RAG agent with progress tracking."""
    progress_msg = cl.Message(
        content="🚀 Initializing AI Assistant...",
        elements=[
            cl.Text(
                name="init_info",
                content="Setting up the RAG agent...",
                display="side"
            )
        ]
    )
    await progress_msg.send()
    
    last_update_time = 0
    
    def init_progress(percentage: int, stage: str, description: str):
        nonlocal last_update_time
        current_time = time.time()
        
        # Rate limit updates
        if current_time - last_update_time < 0.3 and percentage != 100:
            return
        
        last_update_time = current_time
        
        # Create progress bar
        filled = int(percentage // 5)
        empty = 20 - filled
        progress_bar = "🟩" * filled + "⬜" * empty
        
        step_indicator = "🔄" if percentage < 100 else "✅"
        
        # Store progress update to be sent later
        progress_msg.content = f"""
🤖 **Initializing AI Assistant**

{progress_bar} **{percentage}%**

{step_indicator} **{description}**
        """.strip()
        
        if progress_msg.elements:
            progress_msg.elements[0].content = f"""
**Stage:** {stage}
**Progress:** {percentage}%
**Status:** {description}
            """.strip()
    
    try:
        # Initialize agent with progress tracking
        agent = RAGAgent(progress_callback=init_progress)
        
        # Send final progress update
        await progress_msg.update()
        
        # Small delay to show completion
        await cl.sleep(0.5)
        
        # Hide the progress message after completion
        await progress_msg.remove()
        
        return agent
        
    except Exception as e:
        progress_msg.content = f"""
❌ **Initialization Failed**

{str(e)}

Please check your configuration and try again.
        """.strip()
        await progress_msg.update()
        raise

@cl.on_chat_start
async def on_chat_start():
    """
    Initializes the agent and chat session when the chat starts.
    """
    # Set application title and settings
    settings = cl.ChatSettings([
        cl.input_widget.Select(
            id="app_info",
            label="🤖 Agentic RAG Assistant",
            values=["Advanced Document Q&A with Chat History"],
            initial_index=0,
            description="Intelligent document analysis with conversation memory"
        )
    ])
    await settings.send()
    
    # Initialize agent with progress tracking
    agent = await initialize_agent_with_progress()
    cl.user_session.set("agent", agent)
    
    # Initialize chat session variables
    cl.user_session.set("chat_id", cl.user_session.get("id"))
    cl.user_session.set("chat_title", None)
    cl.user_session.set("message_history", [])
    cl.user_session.set("is_first_message", True)
    
    # Create welcome message with app title
    welcome_header = """
# 🤖 **Agentic RAG Assistant**
### *Advanced Document Q&A with Chat History*

---
"""
    
    # Show recent chats in sidebar
    recent_chats = get_recent_chats()
    if recent_chats:
        chat_list = "\n📚 **Recent Conversations:**\n\n"
        for chat in recent_chats[:5]:
            title = chat["title"][:35] + "..." if len(chat["title"]) > 35 else chat["title"]
            chat_list += f"• *{title}* ({chat['message_count']} messages)\n"
        
        welcome_content = welcome_header + f"""
🚀 **Ready to help you analyze documents!**

📄 **Upload a PDF** to get started, or continue a previous conversation.

{chat_list}

💡 *Tip: Your conversations are automatically saved with smart titles!*
"""
    else:
        welcome_content = welcome_header + f"""
🚀 **Ready to help you analyze documents!**

📄 **Upload a PDF** to get started and ask questions about its content.

💡 *Tip: Your conversations will be automatically saved with smart titles!*
"""
    
    await cl.Message(
        content=welcome_content,
        author="🤖 Assistant"
    ).send()

@cl.on_chat_resume
async def on_chat_resume(thread: Any):
    """
    Handles resuming a previous chat session.
    """
    # Set application title and settings
    settings = cl.ChatSettings([
        cl.input_widget.Select(
            id="app_info",
            label="🤖 Agentic RAG Assistant",
            values=["Advanced Document Q&A with Chat History"],
            initial_index=0,
            description="Intelligent document analysis with conversation memory"
        )
    ])
    await settings.send()
    
    # Initialize agent with progress tracking
    agent = await initialize_agent_with_progress()
    cl.user_session.set("agent", agent)
    
    # Load chat history
    chat_data = load_chat_history(thread.id)
    if chat_data:
        cl.user_session.set("chat_id", thread.id)
        cl.user_session.set("chat_title", chat_data.get("title", "Resumed Chat"))
        cl.user_session.set("message_history", chat_data.get("messages", []))
        cl.user_session.set("is_first_message", False)
        
        # Restore conversation context for the agent
        messages = []
        for msg in chat_data.get("messages", []):
            if msg["type"] == "human":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["type"] == "ai":
                messages.append(AIMessage(content=msg["content"]))
        
        # Initialize agent with previous context
        if messages:
            agent._memory = messages
        
        resume_header = """
# 🤖 **Agentic RAG Assistant**
### *Advanced Document Q&A with Chat History*

---
"""
        
        await cl.Message(
            content=f"""{resume_header}
💬 **Resumed Conversation:** *{chat_data.get('title', 'Untitled Chat')}*

🔄 **Context restored** - Continue where you left off!

📊 **Previous messages:** {len(chat_data.get('messages', []))} messages loaded
""",
            author="🤖 Assistant"
        ).send()
    else:
        # Fallback to new chat
        await on_chat_start()


async def process_pdf(file_path: str):
    """
    Processes a PDF file by saving it and ingesting it directly with progress bar.
    """
    file_name = os.path.basename(file_path)
    
    try:
        # Create data directory if it doesn't exist
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

        # Save the file to the data directory
        target_path = os.path.join(DATA_DIR, file_name)
        
        # Copy the uploaded file to the data directory
        with open(file_path, "rb") as source:
            with open(target_path, "wb") as target:
                target.write(source.read())

        # Create progress message with initial state
        progress_msg = cl.Message(
            content="🚀 Starting PDF processing...",
            elements=[
                cl.Text(
                    name="progress_info",
                    content="Preparing to process your document...",
                    display="side"
                )
            ]
        )
        await progress_msg.send()

        # Define progress callback with detailed progress bar and rate limiting
        last_update_time = 0
        pending_updates = []
        
        async def update_progress(step_name: str, percentage: int, description: str):
            nonlocal last_update_time
            current_time = time.time()
            
            # Rate limit updates to prevent payload overflow (max 1 update per 200ms)
            if current_time - last_update_time < 0.2 and percentage != 100 and percentage != -1:
                return
            
            last_update_time = current_time
            
            if percentage == -1:  # Error case
                progress_msg.content = f"""
❌ **Processing Failed**

{description}

Please check the file and try again.
                """.strip()
                await progress_msg.update()
                return
            
            # Create animated progress bar
            filled = int(percentage // 5)  # 20 segments for 100%
            empty = 20 - filled
            progress_bar = "🟩" * filled + "⬜" * empty
            
            # Add step indicator
            step_indicator = "🔄" if percentage < 100 else "✅"
            
            progress_msg.content = f"""
📄 **Processing: `{file_name}`**

{progress_bar} **{percentage}%**

{step_indicator} **{step_name}**
{description}
            """.strip()
            
            # Update the side info as well
            if progress_msg.elements:
                progress_msg.elements[0].content = f"""
**Current Step:** {step_name}
**Progress:** {percentage}%
**File:** {file_name}
**Status:** {description}
                """.strip()
            
            await progress_msg.update()

        # Create synchronous progress wrapper for DocumentIngestor
        def sync_progress_wrapper(percentage: int, stage: str, description: str):
            # Store the update to be processed later
            pending_updates.append((stage, percentage, description))

        # Initialize ingestor and process the file
        ingestor = DocumentIngestor(progress_callback=sync_progress_wrapper)
        
        # Process any pending updates from initialization
        for stage, percentage, description in pending_updates:
            await update_progress(stage, percentage, description)
        pending_updates.clear()
        
        success = await ingestor.ingest_pdf(target_path, update_progress)
        
        if success:
            # Update the vector store in the agent (refresh it)
            agent = cl.user_session.get("agent")
            if agent:
                # Create a simple progress callback for vector store refresh
                def refresh_progress(percentage: int, stage: str, description: str):
                    if percentage == 100:
                        # We can't await here, so we'll just update the progress synchronously
                        # This will be processed in the next update cycle
                        pending_updates.append(("vector_refresh", 95, "🔄 Refreshing knowledge base..."))
                
                agent.vector_store = VectorStore(progress_callback=refresh_progress)
                
                # Process any pending updates from vector store refresh
                for stage, percentage, description in pending_updates:
                    await update_progress(stage, percentage, description)
                pending_updates.clear()
            
            # Final success message
            final_msg = cl.Message(
                content=f"""
✅ **Success!** 

📄 **`{file_name}`** has been successfully processed and added to the knowledge base.

🤖 You can now ask questions about the document content!
                """.strip()
            )
            await final_msg.send()
        else:
            # Error message was already sent via progress callback
            pass
            
    except Exception as e:
        await cl.Message(
            content=f"""
❌ **Unexpected Error**

Failed to process `{file_name}`: {str(e)}

Please check the file format and try again.
            """.strip()
        ).send()


@cl.on_message
async def on_message(message: cl.Message):
    """
    Handles incoming messages from the user with chat history support.
    """
    # Check for file uploads
    if message.elements:
        for element in message.elements:
            if element.mime and "pdf" in element.mime:
                await process_pdf(element.path)
                return

    agent = cl.user_session.get("agent")
    if not agent:
        await cl.Message(content="Agent not initialized. Please refresh the page.").send()
        return

    # Get session variables
    chat_id = cl.user_session.get("chat_id")
    chat_title = cl.user_session.get("chat_title")
    message_history = cl.user_session.get("message_history", [])
    is_first_message = cl.user_session.get("is_first_message", True)

    # Generate chat title from first message
    if is_first_message and not chat_title:
        chat_title = generate_chat_title(message.content)
        cl.user_session.set("chat_title", chat_title)
        cl.user_session.set("is_first_message", False)

    # Add user message to history
    user_message = {
        "type": "human",
        "content": message.content,
        "timestamp": datetime.now().isoformat()
    }
    message_history.append(user_message)

    # Create a streaming message
    msg = cl.Message(content="🤔 Thinking...")
    await msg.send()

    try:
        # Use invoke instead of astream to avoid payload issues
        result = agent.graph.invoke({"messages": [HumanMessage(content=message.content)]})
        
        if "messages" in result and len(result["messages"]) > 0:
            # Get the last AI message (response)
            last_message = result["messages"][-1]
            if hasattr(last_message, 'content') and last_message.content:
                # Update with the final response
                ai_response = last_message.content
                msg.content = ai_response
                await msg.update()
                
                # Add AI response to history
                ai_message = {
                    "type": "ai",
                    "content": ai_response,
                    "timestamp": datetime.now().isoformat()
                }
                message_history.append(ai_message)
                
            else:
                error_response = "I apologize, but I couldn't generate a response. Please try again."
                msg.content = error_response
                await msg.update()
                
                # Add error response to history
                ai_message = {
                    "type": "ai",
                    "content": error_response,
                    "timestamp": datetime.now().isoformat()
                }
                message_history.append(ai_message)
        else:
            error_response = "No response generated. Please try rephrasing your question."
            msg.content = error_response
            await msg.update()
            
            # Add error response to history
            ai_message = {
                "type": "ai",
                "content": error_response,
                "timestamp": datetime.now().isoformat()
            }
            message_history.append(ai_message)
                    
    except Exception as e:
        error_msg = f"Error processing your request: {str(e)}"
        msg.content = error_msg
        await msg.update()
        
        # Add error to history
        ai_message = {
            "type": "ai",
            "content": error_msg,
            "timestamp": datetime.now().isoformat()
        }
        message_history.append(ai_message)
    
    finally:
        # Update session with new message history
        cl.user_session.set("message_history", message_history)
        
        # Save chat history to file
        if chat_id and chat_title:
            save_chat_history(chat_id, message_history, chat_title)

@cl.on_settings_update
async def setup_agent(settings):
    """
    Handle settings updates (if any chat preferences are added).
    """
    print("Settings updated:", settings)

@cl.on_stop
async def on_stop():
    """
    Handle chat session stop - ensure history is saved.
    """
    chat_id = cl.user_session.get("chat_id")
    chat_title = cl.user_session.get("chat_title")
    message_history = cl.user_session.get("message_history", [])
    
    if chat_id and chat_title and message_history:
        save_chat_history(chat_id, message_history, chat_title)
        print(f"Chat history saved for: {chat_title}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)