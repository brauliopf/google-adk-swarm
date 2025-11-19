from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from support_agent.sub_agents.web_searcher.prompt import WEB_SEARCHER_AGENT_PROMPT
from support_agent.sub_agents.web_searcher.guardrails import block_palmeiras_haters
import os
from dotenv import load_dotenv
load_dotenv()

root_agent = None
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

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
    root_agent = Agent(
        model=os.getenv("MODEL_GEMINI_2_0_FLASH"),
        name="web_searcher_agent",
        instruction=WEB_SEARCHER_AGENT_PROMPT,
        description="Resourceful assistant that performs web searching and information retrieval.",
        tools=[tavily_search_tool()],
        output_key="web_searcher_response",
        after_model_callback=block_palmeiras_haters
    )
    print(f"✅ Agent '{root_agent.name}' created using model '{root_agent.model}'.")
except Exception as e:
    print(f"❌ Could not create Searcher agent. Error: {e}")