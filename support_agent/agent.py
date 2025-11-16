from google.adk.agents.llm_agent import Agent
from google.genai import types
from support_agent.tools.get_weather import get_weather
from support_agent.prompt import ROOT_PROMPT
from support_agent.sub_agents.web_searcher.agent import web_searcher_agent
from support_agent.guardrails.block_keyword import block_keyword_guardrail
from support_agent.guardrails.block_paris_tool import block_paris_tool_guardrail

from shared_libraries.constants import MODEL_GEMINI_2_0_FLASH

root_agent = Agent(
    name="router_agent_stateful",
    model=MODEL_GEMINI_2_0_FLASH,
    description="The main coordinator agent. Handles general customer requests and delegates to specialists.",
    instruction=ROOT_PROMPT,
    tools=[get_weather],
    sub_agents=[web_searcher_agent],
    output_key="last_weather_report",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2,
        # max_output_tokens=1000,
        # top_p=0.95,
        # frequency_penalty=0.0,
        # presence_penalty=0.0
    ),
    before_model_callback=block_keyword_guardrail,
    before_tool_callback=block_paris_tool_guardrail
)