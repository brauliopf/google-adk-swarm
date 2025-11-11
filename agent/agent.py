# @title Import necessary libraries
from google.adk.agents import Agent
from dotenv import load_dotenv
from agent.tools import get_weather
from agent.config import MODEL_GEMINI_2_0_FLASH
import warnings
import logging

load_dotenv()

# Ignore all warnings
warnings.filterwarnings("ignore")

logging.basicConfig(level=logging.ERROR)


# @title Define the Weather Agent
AGENT_MODEL = MODEL_GEMINI_2_0_FLASH # Starting with Gemini

weather_agent = Agent(
    name="weather_agent_v1",
    model=AGENT_MODEL, # Can be a string for Gemini or a LiteLlm object
    description="Provides weather information for specific cities.",
    instruction="You are a helpful weather assistant. "
                "When the user asks for the weather in a specific city, "
                "use the 'get_weather' tool to find the information. "
                "If the tool returns an error, inform the user politely. "
                "If the tool is successful, present the weather report clearly.",
    tools=[get_weather], # Pass the function directly
)