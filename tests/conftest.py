"""
Shared fixtures and configuration for tests.
"""

import os
import sys
import pytest
import numpy as np
from unittest.mock import MagicMock, patch, AsyncMock

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(autouse=True)
def set_env_vars(monkeypatch):
    """Set environment variables for all tests."""
    monkeypatch.setenv("MODEL_GEMINI_2_0_FLASH", "gemini-2.0-flash")
    monkeypatch.setenv("GOOGLE_API_KEY", "test-api-key")
    monkeypatch.setenv("TAVILY_API_KEY", "test-tavily-key")
    monkeypatch.setenv("DISABLE_WEB_DRIVER", "1")


@pytest.fixture
def reset_knowledgeable_cache():
    """Reset the knowledge base caches before each test."""
    from support_agent.sub_agents.knowledgeable import agent as knowledgeable_agent
    knowledgeable_agent._knowledge_base_cache = None
    knowledgeable_agent._embeddings_cache = None
    yield
    # Clean up after test
    knowledgeable_agent._knowledge_base_cache = None
    knowledgeable_agent._embeddings_cache = None


@pytest.fixture
def mock_webdriver():
    """Create a mock Selenium WebDriver."""
    mock_driver = MagicMock()
    mock_driver.page_source = "<html><body><p>Test content</p></body></html>"
    return mock_driver


@pytest.fixture
def sample_html_content():
    """Sample HTML content for crawler tests."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
        <script>console.log('script');</script>
        <style>body { color: black; }</style>
    </head>
    <body>
        <header>Header content</header>
        <nav>Navigation</nav>
        <main>
            <h1>Main Title</h1>
            <p>This is the main content.</p>
            <p>Second paragraph with "quotes" and 'apostrophes'.</p>
        </main>
        <aside>Sidebar content</aside>
        <footer>Footer content</footer>
    </body>
    </html>
    """


@pytest.fixture
def sample_knowledge_base():
    """Sample knowledge base data for testing."""
    return {
        "https://example.com/page1": "This is content about product features and pricing.",
        "https://example.com/page2": "Information about customer support and help desk.",
        "https://example.com/page3": "Details about payment methods and transactions."
    }


@pytest.fixture
def mock_embedding():
    """Create a mock embedding vector."""
    return np.array([0.1, 0.2, 0.3, 0.4, 0.5])


@pytest.fixture
def mock_embeddings_list():
    """Create mock embeddings for knowledge base entries."""
    return [
        {
            "url": "https://example.com/page1",
            "embedding": np.array([0.1, 0.2, 0.3, 0.4, 0.5]),
            "content": "This is content about product features and pricing."
        },
        {
            "url": "https://example.com/page2",
            "embedding": np.array([0.2, 0.3, 0.4, 0.5, 0.6]),
            "content": "Information about customer support and help desk."
        },
        {
            "url": "https://example.com/page3",
            "embedding": np.array([0.3, 0.4, 0.5, 0.6, 0.7]),
            "content": "Details about payment methods and transactions."
        }
    ]


@pytest.fixture
def mock_llm_response():
    """Create a mock LLM response for callback tests."""
    from google.adk.agents.llm_agent import LlmResponse
    from google.genai import types

    mock_response = MagicMock(spec=LlmResponse)
    mock_part = MagicMock()
    mock_part.text = "This is a test response."
    mock_response.content = MagicMock()
    mock_response.content.parts = [mock_part]

    return mock_response


@pytest.fixture
def mock_callback_context():
    """Create a mock callback context for guardrail tests."""
    from google.adk.agents.llm_agent import CallbackContext

    mock_context = MagicMock(spec=CallbackContext)
    mock_context.agent_name = "web_searcher_agent"
    mock_context.state = {}

    return mock_context


@pytest.fixture
def mock_tool_context():
    """Create a mock tool context."""
    mock_context = MagicMock()
    mock_context.state = {}
    return mock_context


@pytest.fixture
def mock_genai_client():
    """Create a mock Google GenAI client."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "NO"
    mock_client.models.generate_content.return_value = mock_response
    return mock_client
