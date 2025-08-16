import os
from typing import TypedDict, Annotated
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END, add_messages, START
from .vector_store import VectorStore

# Load environment variables
load_dotenv()

# Get the Google API key
if "GOOGLE_API_KEY" not in os.environ:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")


class AgentState(TypedDict):
    """
    Represents the state of the agent.
    """
    messages: Annotated[list[BaseMessage], add_messages]
    context: list[str]


class RAGAgent:
    """
    A RAG agent that uses LangGraph to orchestrate the workflow.
    """

    def __init__(self, progress_callback=None):
        """
        Initializes the RAGAgent.
        
        Args:
            progress_callback: Optional callback for tracking initialization progress
        """
        if progress_callback:
            progress_callback(5, "agent_init", "🤖 Initializing RAG Agent...")
        
        self.vector_store = VectorStore(progress_callback=progress_callback)
        
        if progress_callback:
            progress_callback(80, "llm_init", "🧠 Initializing language model...")
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash", 
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2
        )
        
        if progress_callback:
            progress_callback(90, "graph_build", "🔗 Building workflow graph...")
        
        self.graph = self._build_graph()
        
        if progress_callback:
            progress_callback(100, "agent_ready", "✅ RAG Agent ready!")

    def _build_graph(self) -> StateGraph:
        """
        Builds the LangGraph for the agent.
        """
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("retrieve", self._retrieve)
        workflow.add_node("generate", self._generate)
        workflow.add_node("rewrite", self._rewrite)

        # Add edges
        workflow.add_edge(START, "retrieve")
        workflow.add_conditional_edges(
            "retrieve",
            self._decide_to_generate,
            {
                "generate": "generate",
                "rewrite": "rewrite",
            },
        )
        workflow.add_edge("rewrite", "retrieve")
        workflow.add_edge("generate", END)

        return workflow.compile()

    def _retrieve(self, state: AgentState) -> AgentState:
        """
        Retrieves relevant documents from the vector store.
        """
        print("---RETRIEVING DOCUMENTS---")
        last_message = state["messages"][-1]
        retrieved_docs = self.vector_store.search(last_message.content)
        return {"context": retrieved_docs}

    def _generate(self, state: AgentState) -> AgentState:
        """
        Generates a response using the retrieved context and conversation history.
        """
        print("---GENERATING RESPONSE---")
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful assistant. Use the following context to answer the user's question.
            If you don't know the answer, just say that you don't know.

            Context:
            {context}"""),
            ("human", "{question}")
        ])
        chain = prompt | self.llm | StrOutputParser()
        response = chain.invoke(
            {"context": "\n".join(state["context"]), "question": state["messages"][-1].content}
        )
        return {"messages": [AIMessage(content=response)]}

    def _rewrite(self, state: AgentState) -> AgentState:
        """
        Rewrites the user's query to be more specific and informative for retrieval.
        """
        print("---REWRITING QUERY---")
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Rewrite the following user query to be more specific and informative for a RAG retrieval system.
            For example, if the user asks "what is the capital of France?", you could rewrite it as "What is the capital city of the country France?".
            
            Only return the rewritten query, nothing else."""),
            ("human", "{query}")
        ])
        chain = prompt | self.llm | StrOutputParser()
        rewritten_query = chain.invoke({"query": state["messages"][-1].content})
        return {"messages": [HumanMessage(content=rewritten_query)]}

    def _decide_to_generate(self, state: AgentState) -> str:
        """
        Decides whether to generate a response or to rewrite the query.
        """
        print("---DECIDING TO GENERATE---")
        if len(state["context"]) == 0:
            print("---DECISION: REWRITE---")
            return "rewrite"
        else:
            print("---DECISION: GENERATE---")
            return "generate"

    def invoke(self, messages: list[BaseMessage]) -> list[BaseMessage]:
        """
        Invokes the agent with a list of messages.
        """
        # Limit the number of messages to prevent payload overflow
        # Keep only the last few messages to maintain context while preventing overflow
        max_messages = 10
        if len(messages) > max_messages:
            # Keep the first message (usually system) and the last few messages
            messages = messages[:1] + messages[-(max_messages-1):]
        
        try:
            result = self.graph.invoke({"messages": messages, "context": []})
            return result["messages"]
        except Exception as e:
            print(f"Error in agent invoke: {e}")
            # Return a safe fallback response
            return messages + [AIMessage(content="I apologize, but I encountered an error processing your request. Please try again.")]
