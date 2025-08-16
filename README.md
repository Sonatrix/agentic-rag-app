# 🤖 Agentic RAG Assistant

**Advanced Document Q&A with Chat History**

An intelligent document analysis application built with Python, LangGraph, Chainlit, ChromaDB, and Google Gemini. Features automatic conversation saving, smart chat titles, and seamless session management.

## ✨ Features

- **🧠 Intelligent Document Analysis** - Upload PDFs and ask questions about their content
- **💬 Chat History** - Automatic conversation saving with smart titles
- **🔄 Session Management** - Resume previous conversations seamlessly
- **📊 Real-time Progress** - Visual feedback during document processing
- **🎨 Modern UI** - Clean, responsive interface with custom styling
- **🛠️ Advanced Tools** - Built-in chat management utilities

## 🚀 Setup

1.  **Install dependencies:**
    ```bash
    pip install uv
    uv venv
    uv pip install -e .
    ```

2.  **Set up your environment:**
    Create a `.env` file in the root of the project and add your Google API key:
    ```
    GOOGLE_API_KEY=your_google_api_key
    ```

3.  **Run the application:**
    ```bash
    uv run chainlit run app.py
    ```

## 📚 Chat Management

Use the included chat management tool for advanced history operations:

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

## 🏗️ Architecture

- **LangGraph**: Orchestrates the RAG workflow with state management
- **Chainlit**: Provides the interactive web interface
- **ChromaDB**: Vector database for document storage and retrieval
- **HuggingFace Embeddings**: Sentence transformers for text embedding
- **Google Gemini**: Large language model for response generation

## 📁 Project Structure

```
agentic-rag-app/
├── src/
│   ├── agent.py          # LangGraph RAG agent
│   └── vector_store.py   # ChromaDB interface
├── app.py                # Chainlit application
├── ingest.py             # Document ingestion utility
├── chat_manager.py       # Chat history management tool
├── chat_history/         # Saved conversations (auto-created)
├── public/               # Custom CSS and assets
└── .chainlit/            # Chainlit configuration
```
uv run chainlit run app.py -w
```