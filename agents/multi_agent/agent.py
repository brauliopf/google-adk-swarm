import asyncio
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types # For creating message Content/Parts
import warnings
import logging
import sys
from pathlib import Path
from google.adk.models.lite_llm import LiteLlm
# Add path to import from agent module
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from agents.config import MODEL_GEMINI_2_0_FLASH, MODEL_GPT_4O, MODEL_CLAUDE_SONNET
from agents.multi_agent.tools import get_weather, get_weather_stateful
from agents.multi_agent.subagents import greeting_agent, farewell_agent, searcher_agent
from agents.multi_agent.prompts import coordinator_prompt, stateful_coordinator_prompt
from agents.multi_agent.guardrails import block_keyword_guardrail, block_paris_tool_guardrail

# --- Setup development environment ---
warnings.filterwarnings("ignore") # Ignore all warnings

# Suppress asyncio asyncgen cleanup errors (MCP client cleanup issue)
logging.basicConfig(level=logging.CRITICAL)  # Only show critical errors
logging.getLogger('asyncio').setLevel(logging.CRITICAL)

# --- Define the agents ---
AGENT_MODEL = MODEL_GPT_4O

root_agent = Agent(
    name="router_agent_stateful",
    model=LiteLlm(model=AGENT_MODEL),
    description="The main coordinator agent. Handles general customer requests and delegates to specialists.",
    instruction=stateful_coordinator_prompt,
    tools=[get_weather_stateful],
    sub_agents=[greeting_agent, farewell_agent, searcher_agent],
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
print(f"✅ Agent '{root_agent.name}' created using stateful tool and output_key.")

# --- Define the agent interaction function ---
async def call_agent_async(query: str, runner, user_id, session_id):
    """Sends a query to the agent and prints the final response."""
    print(f"\n>>> User Query: {query}")

    final_response_text = "Agent did not produce a final response." # Default

    content = types.Content(role='user', parts=[types.Part(text=query)])
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        # run_async executes the agent logic and yields Events --final response is flagged with is_final_response()
        # print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")

        if event.is_final_response():
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text # Assumes text response in the first part
            elif event.actions and event.actions.escalate:
                final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
            break

    print(f"<<< Agent Response: {final_response_text}")
    pass

# --- Run a Conversation ---
async def run_team_conversation(runner):
    print("\n--- Testing Agent Team Delegation ---")
    
    # --- Interactions using await (correct within async def) ---
    await call_agent_async(query = "What is the weather in Paris?",
                            runner=runner,
                            user_id=USER_ID,
                            session_id=SESSION_ID)
    await call_agent_async(query = "What is the weather in London?",
                            runner=runner,
                            user_id=USER_ID,
                            session_id=SESSION_ID)
    await call_agent_async(query = "BLOCK the request for weather in Tokyo.",
                            runner=runner,
                            user_id=USER_ID,
                            session_id=SESSION_ID)
    await call_agent_async(query = "Quando foi o último jogo do Palmeiras?",
                            runner=runner,
                            user_id=USER_ID,
                            session_id=SESSION_ID)
    # await call_agent_async(query = "Who is the dean of the Instituto Tecnológico de Aeronáutica?",
    #                         runner=runner,
    #                         user_id=USER_ID,
    #                         session_id=SESSION_ID)
    await call_agent_async(query = "Oh hi, there! How are you?",
                            runner=runner,
                            user_id=USER_ID,
                            session_id=SESSION_ID)


if __name__ == "__main__":
    APP_NAME = "agents"
    USER_ID = "user_001"
    SESSION_ID = "session_001"
    initial_state = {
    }

    session_service = InMemorySessionService()
    session = asyncio.run(session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID, state=initial_state if initial_state else None))

    print("\n--- Initial Session State ---")
    if session:
        print(f"Session state: {session.state}")
    else:
        print("Error: Could not retrieve session.")

    # Create the runner using the appropriate session service
    if 'root_agent' in globals():
        root_agent = globals()['root_agent']
        runner_coordinator = Runner(
            agent=root_agent,
            app_name=APP_NAME,
            session_service=session_service
        )
        print(f"✅ Runner created for agent '{runner_coordinator.agent.name}'.")

        # Run the conversation
        asyncio.run(run_team_conversation(runner_coordinator))
        print(f"✅ Conversation completed.")