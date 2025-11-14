from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from agents.config import MODEL_GEMINI_2_0_FLASH, MODEL_GPT_4O, \
    MODEL_CLAUDE_SONNET, MODEL_GROQ_QWEN3_32B, MODEL_GROQ_META_LLAMA_GUARD_4_12B, \
    MODEL_GROQ_MOONSHOTAI_KIMI_K2_INSTRUCT_0905, MODEL_GROQ_COMPOUND_MINI, MODEL_GROQ
from agents.multi_agent.tools import say_hello, say_goodbye
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from agents.multi_agent.prompts import searcher_prompt


# --- Greeting Agent ---
greeting_agent = None
try:
    greeting_agent = Agent(
        model = LiteLlm(model=MODEL_GPT_4O),
        name="greeting_agent",
        instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting to the user. "
                    "Use the 'say_hello' tool to generate the greeting. "
                    "If the user provides their name, make sure to pass it to the tool. "
                    "Do not engage in any other conversation or tasks.",
        description="Handles simple greetings and hellos using the 'say_hello' tool.", # Crucial for delegation
        tools=[say_hello],
    )
    print(f"✅ Agent '{greeting_agent.name}' created using model '{greeting_agent.model.model}'.")
except Exception as e:
    print(f"❌ Could not create Greeting agent. Check API Key ({greeting_agent.model}). Error: {e}")

# --- Farewell Agent ---
farewell_agent = None
try:
    farewell_agent = Agent(
        model = LiteLlm(model=MODEL_GROQ_QWEN3_32B),
        name="farewell_agent",
        instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message. "
                    "Use the 'say_goodbye' tool when the user indicates they are leaving or ending the conversation "
                    "(e.g., using words like 'bye', 'goodbye', 'thanks bye', 'see you'). "
                    "Do not perform any other actions.",
        description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.", # Crucial for delegation
        tools=[say_goodbye],
    )
    print(f"✅ Agent '{farewell_agent.name}' created using model '{farewell_agent.model.model}'.")
except Exception as e:
    print(f"❌ Could not create Farewell agent. Check API Key ({farewell_agent.model}). Error: {e}")


# --- Searcher Agent ---
searcher_agent = None
TAVILY_API_KEY = "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"

# Create a function to initialize the MCP toolset to avoid async context issues
def tavily_search_tool():
    """Creates a new MCPToolset instance for Tavily search."""
    return MCPToolset(
        connection_params=StreamableHTTPServerParams(
            url="https://mcp.tavily.com/mcp/",
            headers={
                "Authorization": f"Bearer {TAVILY_API_KEY}",
            },
        ),
    )

searcher_agent = None
try:
    searcher_agent = Agent(
        model="gemini-2.0-flash",
        name="searcher_agent",
        instruction=searcher_prompt,
        description="Handles web searching and information retrieval using the 'tavily_search_tool'.", # Crucial for delegation
        tools=[tavily_search_tool()],
    )
    print(f"✅ Agent '{searcher_agent.name}' created using model '{searcher_agent.model.model}'.")
except Exception as e:
    print(f"❌ Could not create Searcher agent. Error: {e}")