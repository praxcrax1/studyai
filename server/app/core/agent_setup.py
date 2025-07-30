from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import Tool
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AgentAction, AgentFinish
from app.core.tools import rag_retriever, upload_pdf_tool, url_upload_tool
from app.core.config import settings
import logging
from typing import Any, Dict, List, Optional
import json

# Configure logging to show more details
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ThinkingProcessCallback(BaseCallbackHandler):
    """Custom callback to capture and display the agent's thinking process."""
    
    def __init__(self):
        self.step_count = 0
        
    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        """Called when the agent takes an action."""
        self.step_count += 1
        print(f"\n🤔 THINKING STEP {self.step_count}:")
        print(f"💭 Agent Decision: Using tool '{action.tool}'")
        print(f"📝 Reasoning: {action.log}")
        print(f"🔧 Tool Input: {action.tool_input}")
        print("-" * 60)
        
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> Any:
        """Called when a tool starts running."""
        tool_name = serialized.get("name", "Unknown Tool")
        print(f"🛠️  EXECUTING TOOL: {tool_name}")
        print(f"📥 Input: {input_str}")
        
    def on_tool_end(self, output: str, **kwargs: Any) -> Any:
        """Called when a tool finishes running."""
        print(f"📤 Tool Output: {output[:200]}{'...' if len(output) > 200 else ''}")
        print("-" * 60)
        
    def on_tool_error(self, error: Exception, **kwargs: Any) -> Any:
        """Called when a tool encounters an error."""
        print(f"❌ TOOL ERROR: {str(error)}")
        print("-" * 60)
        
    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> Any:
        """Called when the agent finishes."""
        print(f"\n✅ FINAL DECISION:")
        print(f"🎯 Agent's final response: {finish.return_values}")
        print(f"📋 Reasoning: {finish.log}")
        print("=" * 60)
        
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> Any:
        """Called when LLM starts generating."""
        print(f"\n🧠 LLM THINKING...")
        if kwargs.get('verbose', False):
            print(f"🎯 Prompt: {prompts[0][:300]}{'...' if len(prompts[0]) > 300 else ''}")
            
    def on_llm_end(self, response, **kwargs: Any) -> Any:
        """Called when LLM finishes generating."""
        print(f"💡 LLM Response Generated")

def create_verbose_tools(user_id: str):
    """Create tools with verbose output for debugging."""
    
    def verbose_rag_retriever(query: str) -> str:
        """Retrieve relevant information with verbose output."""
        print(f"🔍 Searching knowledge base for: '{query}'")
        try:
            result = rag_retriever.invoke({"query": query, "user_id": user_id})
            print(f"📚 Retrieved {len(str(result))} characters of information")
            return str(result) if result else "No relevant information found."
        except Exception as e:
            error_msg = f"Error retrieving information: {str(e)}"
            print(f"❌ RAG Error: {error_msg}")
            return error_msg
    
    def verbose_pdf_uploader(file_path: str) -> str:
        """Upload PDF with verbose output."""
        print(f"📄 Processing PDF: {file_path}")
        try:
            result = upload_pdf_tool.invoke({"file_path": file_path, "user_id": user_id})
            print(f"✅ PDF processed successfully")
            return str(result) if result else "PDF upload completed successfully."
        except Exception as e:
            error_msg = f"Error uploading PDF: {str(e)}"
            print(f"❌ PDF Error: {error_msg}")
            return error_msg
    
    def verbose_url_processor(url: str) -> str:
        """Process URL with verbose output."""
        print(f"🌐 Processing URL: {url}")
        try:
            result = url_upload_tool.invoke({"url": url, "user_id": user_id})
            print(f"✅ URL processed successfully")
            return str(result) if result else "URL processing completed successfully."
        except Exception as e:
            error_msg = f"Error processing URL: {str(e)}"
            print(f"❌ URL Error: {error_msg}")
            return error_msg

    return [
        Tool(
            name="KnowledgeRetriever",
            func=verbose_rag_retriever,
            description="Retrieve relevant information from user documents. Use this when users ask about their uploaded content or need information from their knowledge base."
        ),
        Tool(
            name="PDFUploader",
            func=verbose_pdf_uploader,
            description="Upload and process PDF documents from a file path. Use this when users want to add new PDF documents to their knowledge base."
        ),
        Tool(
            name="URLProcessor",
            func=verbose_url_processor,
            description="Process and extract content from web URLs. Use this when users provide URLs they want to analyze or add to their knowledge base."
        )
    ]

def create_agent_with_thinking(user_id: str, chat_history: list = None):
    """Create an agent that shows its complete thinking process."""
    
    if chat_history is None:
        chat_history = []
    
    print(f"🚀 Creating agent for user: {user_id}")
    print(f"📚 Loading {len(chat_history)} previous messages")
    
    # Create verbose tools
    tools = create_verbose_tools(user_id)
    
    # Initialize LLM with fallback
    print("🧠 Initializing Language Model...")
    llm = None
    
    # Try primary model first
    try:
        llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.3,
            max_retries=2,
        )
        # Test connection
        test_response = llm.invoke("Hello")
        print(f"✅ Primary model initialized: {settings.GEMINI_MODEL}")
        
    except Exception as e:
        print(f"⚠️  Primary model failed: {e}")
        try:
            # Fallback - you should specify actual fallback model
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",  # Specify fallback model
                google_api_key=settings.GEMINI_API_KEY,
                temperature=0.3,
                max_retries=2,
            )
            test_response = llm.invoke("Hello")
            print("✅ Fallback model initialized: gemini-1.5-flash")
            
        except Exception as e2:
            print(f"❌ All models failed: {e2}")
            raise Exception("Unable to initialize any Gemini model")

    # Enhanced prompt for better thinking visibility
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful AI assistant with access to various tools for document processing and information retrieval.

IMPORTANT: When making decisions, think step by step and explain your reasoning clearly.

Your available tools:
1. KnowledgeRetriever - Search through user's uploaded documents
2. PDFUploader - Process new PDF files
3. URLProcessor - Extract content from web URLs

Guidelines:
- Always explain WHY you're choosing a specific tool
- If you need to use multiple tools, explain the sequence
- Be transparent about your decision-making process
- Provide helpful responses even if tools fail
- When unsure, ask clarifying questions

Remember: Your reasoning and tool choices are visible to help users understand your process."""),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}")
    ])

    # Create agent
    try:
        agent = create_tool_calling_agent(llm, tools, prompt)
        print("✅ Agent created successfully")
    except Exception as e:
        print(f"❌ Failed to create agent: {e}")
        raise Exception(f"Agent creation failed: {e}")

    # Setup memory
    memory = ConversationBufferWindowMemory(
        k=5,
        memory_key="chat_history",
        return_messages=True
    )

    # Load existing history with verbose output
    if chat_history:
        print("📖 Loading conversation history...")
        loaded_count = 0
        for msg in chat_history:
            try:
                if isinstance(msg, dict) and "human" in msg and "ai" in msg:
                    memory.save_context({"input": msg["human"]}, {"output": msg["ai"]})
                    loaded_count += 1
            except Exception as e:
                print(f"⚠️  Skipped malformed message: {e}")
        print(f"✅ Loaded {loaded_count} conversation exchanges")

    # Create callback for thinking process
    thinking_callback = ThinkingProcessCallback()

    # Create agent executor with maximum verbosity
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,  # LangChain's built-in verbosity
        handle_parsing_errors=True,
        max_iterations=15,
        early_stopping_method="generate",
        return_intermediate_steps=True,  # This captures the thinking steps
        callbacks=[thinking_callback]  # Our custom thinking process callback
    )
    
    print("🎉 Agent ready! All thinking processes will be displayed.")
    return agent_executor

def run_agent_with_thinking(agent_executor, user_input: str):
    """Run the agent and display comprehensive thinking process."""
    
    print(f"\n{'='*80}")
    print(f"🎯 USER INPUT: {user_input}")
    print(f"{'='*80}")
    
    try:
        # Run the agent
        result = agent_executor.invoke({"input": user_input})
        
        print(f"\n🏁 FINAL RESULT:")
        print(f"📝 Output: {result['output']}")
        
        # Display intermediate steps if available
        if 'intermediate_steps' in result and result['intermediate_steps']:
            print(f"\n📊 INTERMEDIATE STEPS SUMMARY:")
            for i, (action, observation) in enumerate(result['intermediate_steps'], 1):
                print(f"Step {i}:")
                print(f"  Action: {action.tool} - {action.tool_input}")
                print(f"  Result: {observation[:100]}{'...' if len(observation) > 100 else ''}")
        
        return result
        
    except Exception as e:
        print(f"❌ EXECUTION ERROR: {str(e)}")
        return {"output": f"Error: {str(e)}", "error": True}

# Example usage function
def demo_thinking_process():
    """Demonstrate the thinking process with example queries."""
    
    try:
        # Create agent
        agent = create_agent_with_thinking("demo_user", [])
        
        # Example queries that will show different thinking patterns
        test_queries = [
            "What information do you have about machine learning?",
            "Can you upload a PDF from /path/to/document.pdf?",
            "Process this URL: https://example.com/article"
        ]
        
        for query in test_queries:
            print(f"\n{'🧪 DEMO QUERY':-^80}")
            result = run_agent_with_thinking(agent, query)
            print(f"{'END DEMO':-^80}\n")
            
    except Exception as e:
        print(f"Demo failed: {e}")

if __name__ == "__main__":
    # Uncomment to run demo
    # demo_thinking_process()
    pass