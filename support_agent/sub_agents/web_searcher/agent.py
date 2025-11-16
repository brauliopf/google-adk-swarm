from google.adk.agents.llm_agent import Agent
from shared_libraries.constants import MODEL_GEMINI_2_0_FLASH
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from support_agent.sub_agents.web_searcher.prompt import SEARCH_RESULT_AGENT_PROMPT

web_searcher_agent = None
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

try:
    web_searcher_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="web_searcher_agent",
        instruction=SEARCH_RESULT_AGENT_PROMPT,
        description="Handles web searching and information retrieval using the 'tavily_search_tool'.", # Crucial for delegation
        tools=[tavily_search_tool()],
    )
    print(f"✅ Agent '{web_searcher_agent.name}' created using model '{web_searcher_agent.model.model}'.")
except Exception as e:
    print(f"❌ Could not create Searcher agent. Error: {e}")