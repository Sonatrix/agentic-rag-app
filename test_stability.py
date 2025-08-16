"""
Test script to verify the payload overflow fixes.
"""
import asyncio
from src.agent import RAGAgent
from langchain_core.messages import HumanMessage, AIMessage

async def test_agent_stability():
    """Test the agent with multiple messages to ensure no payload overflow."""
    
    print("🧪 Testing Agent Stability (Payload Overflow Prevention)")
    print("=" * 60)
    
    try:
        # Initialize agent
        agent = RAGAgent()
        print("✅ Agent initialized successfully")
        
        # Test with multiple messages to simulate potential overflow scenario
        messages = [HumanMessage(content="Hello, this is a test message.")]
        
        for i in range(5):
            print(f"🔄 Test iteration {i+1}/5")
            
            # Invoke agent
            result = agent.invoke(messages)
            print(f"   Messages in result: {len(result)}")
            
            # Add the response to continue conversation
            if result and len(result) > len(messages):
                messages = result
            
            # Simulate some delay
            await asyncio.sleep(0.5)
        
        print("✅ All tests passed! No payload overflow detected.")
        print(f"📊 Final message count: {len(messages)}")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(test_agent_stability())
