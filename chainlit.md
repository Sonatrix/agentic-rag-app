# Agentic RAG with Chat History

Welcome to this agentic RAG application with intelligent conversation management!

## 🚀 **Getting Started:**

1. **Upload a PDF file** - Drag & drop or click to upload
2. **Wait for processing** - Watch the real-time progress bar
3. **Ask questions** - Chat about your document content
4. **Continue conversations** - Your chat history is automatically saved

## 💬 **Chat Features:**

- **Auto-saved conversations** - Every chat gets a smart title and is preserved
- **Session resume** - Continue previous conversations seamlessly  
- **Recent chats sidebar** - Quick access to your conversation history
- **Smart titles** - Conversations are automatically named based on your first message

## 📚 **Document Processing:**

- **Real-time progress** - See exactly what's happening during PDF processing
- **Error handling** - Clear feedback if something goes wrong
- **Multiple documents** - Upload and query multiple PDFs

## 🔧 **Chat Management:**

Use the included `chat_manager.py` tool for advanced history management:

```bash
# List all conversations
python chat_manager.py list --details

# Search your chat history  
python chat_manager.py search "machine learning"

# Export a conversation
python chat_manager.py export <chat_id> --format txt

# Clean up old chats
python chat_manager.py cleanup --days 30 --confirm
```

## 💡 **Tips:**

- **First message matters** - It becomes your chat title, so make it descriptive
- **Resume anytime** - Your conversations persist across browser sessions
- **Ask follow-ups** - The agent remembers the context within each conversation
- **Upload multiple files** - Each document adds to the shared knowledge base

---

*Happy chatting! 🤖📖*