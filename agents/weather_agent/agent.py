from google.adk.agents import Agent
from dotenv import load_dotenv
import sys
from pathlib import Path

# Add parent directory to path to import from agent module
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.config import MODEL_GEMINI_2_0_FLASH
from agents.weather_agent.tools import get_weather

load_dotenv()

AGENT_MODEL = MODEL_GEMINI_2_0_FLASH

root_agent = Agent(
    name="weather_agent_v1",
    model=AGENT_MODEL,
    description="Provides weather information for specific cities.",
    instruction="You are a helpful weather assistant. "
                "When the user asks for the weather in a specific city, "
                "use the 'get_weather' tool to find the information. "
                "If the tool returns an error, inform the user politely. "
                "If the tool is successful, present the weather report clearly.",
    tools=[get_weather],
)
