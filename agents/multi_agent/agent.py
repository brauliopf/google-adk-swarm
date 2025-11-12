import asyncio
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types # For creating message Content/Parts
import warnings
import logging
import sys
from pathlib import Path
from agents.config import MODEL_GEMINI_2_0_FLASH, MODEL_GPT_4O, MODEL_CLAUDE_SONNET
from agents.multi_agent.tools import get_weather
from google.adk.tools import google_search
from agents.multi_agent.subagents import greeting_agent, farewell_agent

# --- Setup development environment ---
warnings.filterwarnings("ignore") # Ignore all warnings

logging.basicConfig(level=logging.ERROR)

sys.path.insert(0, str(Path(__file__).parent.parent.parent)) # Add path to import from agent module


# --- Define the agents ---
if greeting_agent and farewell_agent and 'get_weather' in globals():
    AGENT_MODEL = MODEL_GEMINI_2_0_FLASH

    weather_agent_team = Agent(
        name="weather_agent_team_v2",
        model=AGENT_MODEL,
        description="The main coordinator agent. Handles weather requests and delegates greetings/farewells to specialists.",
        instruction="You are the main Weather Agent coordinating a team. Your primary responsibility is to provide weather information. "
                    "Use the 'get_weather' tool ONLY for specific weather requests (e.g., 'weather in London'). "
                    "You have specialized sub-agents: "
                    "1. 'greeting_agent': Handles simple greetings like 'Hi', 'Hello'. Delegate to it for these. "
                    "2. 'farewell_agent': Handles simple farewells like 'Bye', 'See you'. Delegate to it for these. "
                    "Analyze the user's query. If it's a greeting, delegate to 'greeting_agent'. If it's a farewell, delegate to 'farewell_agent'. "
                    "If it's a weather request, handle it yourself using 'get_weather'. "
                    "For anything else, respond appropriately or state you cannot handle it.",
        tools=[get_weather],
        sub_agents=[greeting_agent, farewell_agent]
    )
    print(f"Agent '{weather_agent_team.name}' created using model '{AGENT_MODEL}'.")

else:
    print("❌ Cannot create root agent because one or more sub-agents failed to initialize or 'get_weather' tool is missing.")
    if not greeting_agent: print(" - Greeting Agent is missing.")
    if not farewell_agent: print(" - Farewell Agent is missing.")
    if 'get_weather' not in globals(): print(" - get_weather function is missing.")


########################################################
# Run a Conversation
########################################################
root_agent_var_name = "weather_agent_team"

async def run_team_conversation(runner):
    print("\n--- Testing Agent Team Delegation ---")
    
    # --- Interactions using await (correct within async def) ---
    await call_agent_async(query = "Hello there!",
                            runner=runner,
                            user_id=USER_ID,
                            session_id=SESSION_ID)
    await call_agent_async(query = "What is the weather in New York?",
                            runner=runner,
                            user_id=USER_ID,
                            session_id=SESSION_ID)
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

async def run_conversation(runner):
    await call_agent_async("What is the weather like in London?",
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID)

    await call_agent_async("How about Paris?",
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID) # Expecting the tool's error message

    await call_agent_async("Tell me the weather in New York",
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID)

if __name__ == "__main__":
    try:

        APP_NAME = "weather_tutorial_agent_team"
        USER_ID = "user_1_agent_team"
        SESSION_ID = "session_001_agent_team"

        session_service = InMemorySessionService()

        # Create the specific session where the conversation will happen
        session = asyncio.run(session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID))
        print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")

        root_agent_var_name = 'root_agent' # Default name from Step 3 guide
        if 'weather_agent_team' in globals(): # Check if user used this name instead
            root_agent_var_name = 'weather_agent_team'
        elif 'root_agent' not in globals():
            print("⚠️ Root agent ('root_agent' or 'weather_agent_team') not found. Cannot define run_team_conversation.")
            # Assign a dummy value to prevent NameError later if the code block runs anyway
            root_agent = None # Or set a flag to prevent execution
        
        if root_agent_var_name in globals() and globals()[root_agent_var_name]:
            root_agent = globals()[root_agent_var_name]
            runner_root = Runner(
                agent=root_agent,
                app_name=APP_NAME,
                session_service=session_service
            )
            print(f"Runner created for agent '{runner_root.agent.name}'.")
            asyncio.run(run_team_conversation(runner_root))
        else:
            print("⚠️ Root agent not found. Cannot run conversation.")

        actual_root_agent = globals()[root_agent_var_name]
        runner_agent_team = Runner(
            agent=actual_root_agent,
            app_name=APP_NAME,
            session_service=session_service
        )
        print(f"Runner created for agent.") # TODO: add agent name here

        # asyncio.run(run_team_conversation())

    except Exception as e:
        print(f"An error occurred: {e}")