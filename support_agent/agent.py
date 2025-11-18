from google.adk.agents.llm_agent import Agent
from google.genai import types
from support_agent.prompt import ROOT_PROMPT
from support_agent.sub_agents.web_searcher.agent import root_agent as web_searcher_agent
from support_agent.sub_agents.crawler.agent import root_agent as crawler_agent
from support_agent.sub_agents.knowledgeable.agent import root_agent as knowledgeable_agent
import os
from dotenv import load_dotenv
load_dotenv()

root_agent = Agent(
    name="coordinator_agent",
    model=os.getenv("MODEL_GEMINI_2_0_FLASH"),
    description="You assess and handle general customer requests, answering direct questions or delegating to a specialist agent when necessary.",
    instruction=ROOT_PROMPT,
    tools=[],
    sub_agents=[web_searcher_agent, knowledgeable_agent, crawler_agent],
    output_key="coordinator_response",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2,
    )
)