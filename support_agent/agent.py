from google.adk.agents.llm_agent import Agent
from google.genai import types
from support_agent.tools.get_weather import get_weather
from support_agent.prompt import ROOT_PROMPT
from support_agent.sub_agents.web_searcher.agent import root_agent as web_searcher_agent
from support_agent.sub_agents.crawler.agent import root_agent as crawler_agent
from support_agent.guardrails.block_keyword import block_keyword_guardrail
from support_agent.guardrails.block_paris_tool import block_paris_tool_guardrail
import os
from dotenv import load_dotenv
load_dotenv()

root_agent = Agent(
    name="root_agent",
    model=os.getenv("MODEL_GEMINI_2_0_FLASH"),
    description="The main coordinator agent. Handles general customer requests and delegates to specialists.",
    instruction=ROOT_PROMPT,
    tools=[get_weather],
    sub_agents=[crawler_agent, web_searcher_agent],
    output_key="root_response",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2,
    ),
    before_model_callback=block_keyword_guardrail,
    before_tool_callback=block_paris_tool_guardrail
)