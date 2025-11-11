from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from dotenv import load_dotenv
import sys
from pathlib import Path

# Add parent directory to path to import from agent module
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.config import MODEL_GEMINI_2_0_FLASH

load_dotenv()

AGENT_MODEL = MODEL_GEMINI_2_0_FLASH

root_agent = LlmAgent(
    model=AGENT_MODEL,
    name="search_agent",
    description="A helpful assistant agent that can search the web.",
    instruction="""Respond to the query using google search""",
    tools=[google_search],
)
