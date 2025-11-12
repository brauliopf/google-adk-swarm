import asyncio
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types # For creating message Content/Parts
import warnings
import logging
import sys
from pathlib import Path
# Add path to import from agent module
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from agents.config import MODEL_GEMINI_2_0_FLASH
from agents.multi_agent.tools import get_weather
from agents.multi_agent.subagents import greeting_agent, farewell_agent, searcher_agent
from agents.multi_agent.prompts import coordinator_prompt

# --- Setup development environment ---
warnings.filterwarnings("ignore") # Ignore all warnings

# Suppress asyncio asyncgen cleanup errors (MCP client cleanup issue)
logging.basicConfig(level=logging.CRITICAL)  # Only show critical errors
logging.getLogger('asyncio').setLevel(logging.CRITICAL)


# --- Define the agents ---
if greeting_agent and farewell_agent and searcher_agent and 'get_weather' in globals():
    AGENT_MODEL = MODEL_GEMINI_2_0_FLASH

    coordinator_agent = Agent(
        name="coordinator_agent",
        model=AGENT_MODEL,
        description="The main coordinator agent. Handles general customer requests and delegates to specialists.",
        instruction=coordinator_prompt,
        tools=[get_weather],
        sub_agents=[greeting_agent, farewell_agent, searcher_agent]
    )
    print(f"✅ Agent '{coordinator_agent.name}' created using model '{AGENT_MODEL}'.")

else:
    print("❌ Cannot create root agent because one or more sub-agents failed to initialize or 'get_weather' tool is missing.")
    if not greeting_agent: print(" - Greeting Agent is missing.")
    if not farewell_agent: print(" - Farewell Agent is missing.")
    if not searcher_agent: print(" - Searcher Agent is missing.")
    if 'get_weather' not in globals(): print(" - get_weather function is missing.")


# --- Run a Conversation ---
root_agent_var_name = "coordinator_agent"

async def run_team_conversation(runner):
    print("\n--- Testing Agent Team Delegation ---")
    
    # --- Interactions using await (correct within async def) ---
    await call_agent_async(query = "Quando foi o último jogo do Palmeiras?",
                            runner=runner,
                            user_id=USER_ID,
                            session_id=SESSION_ID)
    await call_agent_async(query = "What is the weather in New York?",
                            runner=runner,
                            user_id=USER_ID,
                            session_id=SESSION_ID)
    # await call_agent_async(query = "Who is the dean of the Instituto Tecnológico de Aeronáutica?",
    #                         runner=runner,
    #                         user_id=USER_ID,
    #                         session_id=SESSION_ID)
    await call_agent_async(query = "Thanks, bye!",
                            runner=runner,
                            user_id=USER_ID,
                            session_id=SESSION_ID)

# --- Define the agent interaction function ---
async def call_agent_async(query: str, runner, user_id, session_id):
  """Sends a query to the agent and prints the final response."""
  print(f"\n>>> User Query: {query}")

  # Prepare the user's message in ADK format
  content = types.Content(role='user', parts=[types.Part(text=query)])

  final_response_text = "Agent did not produce a final response." # Default

  # run_async executes the agent logic and yields Events.
  # Iterate through events to find the final answer --flagged with is_final_response()
  async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
    # print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")

    if event.is_final_response():
        if event.content and event.content.parts:
            final_response_text = event.content.parts[0].text # Assumes text response in the first part
        elif event.actions and event.actions.escalate:
            final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
        break

  print(f"<<< Agent Response: {final_response_text}")

if __name__ == "__main__":
    APP_NAME = "agents_swarm"
    USER_ID = "user_001"
    SESSION_ID = "session_001"

    session_service = InMemorySessionService()
    session = asyncio.run(session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID))

    if 'coordinator_agent' in globals():
        coordinator_agent = globals()['coordinator_agent']
        runner_coordinator = Runner(
            agent=coordinator_agent,
            app_name=APP_NAME,
            session_service=session_service
        )
        print(f"✅ Runner created for agent '{runner_coordinator.agent.name}'.")
        asyncio.run(run_team_conversation(runner_coordinator))