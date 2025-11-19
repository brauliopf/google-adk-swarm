import warnings
import selenium
from bs4 import BeautifulSoup
from google.adk.agents.llm_agent import Agent
from google.adk.tools.tool_context import ToolContext
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from . import prompt
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
load_dotenv()

warnings.filterwarnings("ignore", category=UserWarning)

ACTIVATE_WEB_DRIVER = int(os.getenv("ACTIVATE_WEB_DRIVER", "0"))

driver = None

if ACTIVATE_WEB_DRIVER:
    options = Options()
    options.binary_location = os.getenv("CHROME_BIN", "/usr/bin/chromium")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--verbose")
    options.add_argument("user-data-dir=/tmp/selenium")

    service = Service(os.getenv("CHROMEDRIVER_PATH", "/usr/bin/chromedriver"))
    driver = selenium.webdriver.Chrome(service=service, options=options)

def go_to_url(url: str) -> str:
    """Navigates the browser to the given URL."""
    driver.get(url.strip())
    return f"Navigated to URL: {url}"

def get_page_source() -> str:
    """Returns the current page source."""
    LIMIT = 4000000
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

    # Get cleaned text
    text = soup.get_text(separator=' ', strip=True)

    # Escape quotation marks to prevent JSON parsing issues
    text = text.replace('"', '\\"')

    return text

def extract_structured_content(
    page_text: str, user_task: str, tool_context: ToolContext
) -> str:
    """Analyzes the webpage text content and extracts relevant content."""

    analysis_prompt = prompt.ANALYSIS_PROMPT.format(**{'page_text':page_text, 'user_task':user_task})

    return analysis_prompt


class CrawlerResponse(BaseModel):
    source: str = Field(description="The URL of the page that was crawled.")
    content: str = Field(description="The text content of the page to the user using a markdown format. Use metadata to describe unstructured content.")

root_agent = Agent(
    model=os.getenv("MODEL_GEMINI_2_0_FLASH"),
    name="crawler_agent",
    description="Resourceful assistant that reviews websites and summarizes or reasons about their content give a URL.",
    instruction=prompt.CRAWLER_INSTRUCTION,
    # output_schema=CrawlerResponse,
    tools=[
        go_to_url,
        get_page_text,
    ],
    output_key="crawler_response",
)