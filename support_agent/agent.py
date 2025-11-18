from google.adk.agents.llm_agent import Agent
from google.genai import types
from support_agent.prompt import ROOT_PROMPT
from support_agent.sub_agents.web_searcher.agent import root_agent as web_searcher_agent
from support_agent.sub_agents.crawler.agent import root_agent as crawler_agent
from google.adk.tools.agent_tool import AgentTool
import os
from dotenv import load_dotenv
load_dotenv()

crawler_agent_tool = AgentTool(agent=crawler_agent)
web_searcher_agent_tool = AgentTool(agent=web_searcher_agent)

root_agent = Agent(
    name="root_agent",
    model=os.getenv("MODEL_GEMINI_2_0_FLASH"),
    description="The main orchestrator agent. Handles general customer requests and delegates to a specialist agent.",
    instruction=ROOT_PROMPT,
    tools=[crawler_agent_tool],
    output_key="root_response",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2,
    )
)