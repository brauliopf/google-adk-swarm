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

# --- Setup development environment ---
warnings.filterwarnings("ignore") # Ignore all warnings

logging.basicConfig(level=logging.ERROR)

sys.path.insert(0, str(Path(__file__).parent.parent.parent)) # Add path to import from agent module


# --- Define the agents ---
AGENT_MODEL = MODEL_GPT_4O

weather_agent = Agent(
    name="weather_agent_v1",
    model=LiteLlm(model=AGENT_MODEL),
    description="Provides weather information for specific cities.",
    instruction="You are a helpful weather assistant. "
                "When the user asks for the weather in a specific city, "
                "use the 'get_weather' tool for city weather requests. "
                "Clearly present successful reports or polite error messages based on the tool's output status.",
    tools=[get_weather],
)
print(f"Agent '{weather_agent.name}' created using model '{AGENT_MODEL}'.")

########################################################
# Run the Initial Conversation
########################################################

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
        APP_NAME = "search_tutorial_app"
        USER_ID = "user_1"
        SESSION_ID = "session_001" # Using a fixed ID for simplicity

        session_service = InMemorySessionService()

        # Create the specific session where the conversation will happen
        session = asyncio.run(session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID))

        print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")

        runner = Runner(
            agent=weather_agent, # The agent we want to run
            app_name=APP_NAME,   # Associates runs with our app
            session_service=session_service # Uses our session manager
        )
        print(f"Runner created for agent '{runner.agent.name}'.")
        
        asyncio.run(run_conversation(runner))

        # asyncio.run(call_agent_async("who is the dean of the Instituto Tecnológico de Aeronáutica?",
        #                                runner=runner,
        #                                user_id=USER_ID,
        #                                session_id=SESSION_ID))

    except Exception as e:
        print(f"An error occurred: {e}")