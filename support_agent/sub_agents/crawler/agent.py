import warnings
import selenium
from bs4 import BeautifulSoup
from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.load_artifacts_tool import load_artifacts_tool
from google.adk.tools.tool_context import ToolContext
from google.genai import types
from PIL import Image
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from . import prompt

import os
from dotenv import load_dotenv
load_dotenv()

warnings.filterwarnings("ignore", category=UserWarning)

DISABLE_WEB_DRIVER = int(os.getenv("DISABLE_WEB_DRIVER", "0"))

if not DISABLE_WEB_DRIVER:
    options = Options()
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--verbose")
    options.add_argument("user-data-dir=/tmp/selenium")

    driver = selenium.webdriver.Chrome(options=options)


def go_to_url(url: str) -> str:
    """Navigates the browser to the given URL."""
    print(f"🌐 Navigating to URL: {url}")  # Added print statement
    driver.get(url.strip())
    return f"Navigated to URL: {url}"

def get_page_source() -> str:
    LIMIT = 4000000
    """Returns the current page source."""
    print("📄 Getting page source...")  # Added print statement
    return driver.page_source[0:LIMIT]

def get_page_text() -> str:
    """Returns the text content of the current page after excluding unwanted tags."""
    page_source = get_page_source()
    
    soup = BeautifulSoup(page_source, 'html.parser')

    # Remove unwanted tags
    tags_to_remove = ['script', 'style', 'nav', 'footer', 'aside', 'header', 'path']
    for tag in tags_to_remove:
        for element in soup.find_all(tag):
            element.decompose()

    # Return cleaned text
    return soup.get_text(separator=' ', strip=True)

def extract_structured_content(
    page_text: str, user_task: str, tool_context: ToolContext
) -> str:
    """Analyzes the webpage text content and extracts relevant content."""
    print(
        "🤔 Analyzing webpage text content and extracting relevant content..."
    )  # Added print statement

    analysis_prompt = prompt.ANALYSIS_PROMPT.format(**{'page_text':page_text, 'user_task':user_task})

    return analysis_prompt


root_agent = Agent(
    model=os.getenv("MODEL_GEMINI_2_0_FLASH"),
    name="crawler_agent",
    description="Crawl a specific website and gather information from it",
    instruction=prompt.CRAWLER_AGENT_PROMPT,
    tools=[
        go_to_url,
        get_page_text,
        extract_structured_content
    ],
    output_key="crawler_response",
)
