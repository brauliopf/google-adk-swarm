"""
Unit tests for crawler agent tools.
"""

import pytest
from unittest.mock import MagicMock, patch
from bs4 import BeautifulSoup

from tests.fixtures.mock_data import (
    SIMPLE_HTML,
    COMPLEX_HTML,
    EMPTY_HTML,
    EXPECTED_CLEANED_TEXT_KEYWORDS,
    SHOULD_NOT_APPEAR
)


class TestGoToUrl:
    """Tests for the go_to_url tool."""

    @patch('support_agent.sub_agents.crawler.agent.get_driver')
    def test_go_to_url_success(self, mock_get_driver):
        """Test successful navigation to a URL."""
        from support_agent.sub_agents.crawler.agent import go_to_url

        mock_driver = MagicMock()
        mock_get_driver.return_value = mock_driver

        url = "https://example.com"
        result = go_to_url(url)

        mock_driver.get.assert_called_once_with(url)
        assert "Navigated to URL" in result
        assert url in result

    @patch('support_agent.sub_agents.crawler.agent.get_driver')
    def test_go_to_url_strips_whitespace(self, mock_get_driver):
        """Test that URL whitespace is stripped."""
        from support_agent.sub_agents.crawler.agent import go_to_url

        mock_driver = MagicMock()
        mock_get_driver.return_value = mock_driver

        url_with_spaces = "  https://example.com  "
        result = go_to_url(url_with_spaces)

        mock_driver.get.assert_called_once_with("https://example.com")
        assert "Navigated to URL" in result

    @patch('support_agent.sub_agents.crawler.agent.get_driver')
    def test_go_to_url_with_path(self, mock_get_driver):
        """Test navigation to URL with path."""
        from support_agent.sub_agents.crawler.agent import go_to_url

        mock_driver = MagicMock()
        mock_get_driver.return_value = mock_driver

        url = "https://example.com/page/subpage?query=test"
        result = go_to_url(url)

        mock_driver.get.assert_called_once_with(url)
        assert url in result


class TestGetPageText:
    """Tests for the get_page_text tool."""

    @patch('support_agent.sub_agents.crawler.agent.get_driver')
    def test_get_page_text_simple_html(self, mock_get_driver):
        """Test extracting text from simple HTML."""
        from support_agent.sub_agents.crawler.agent import get_page_text

        mock_driver = MagicMock()
        mock_driver.page_source = SIMPLE_HTML
        mock_get_driver.return_value = mock_driver

        result = get_page_text()

        assert "Hello World" in result

    @patch('support_agent.sub_agents.crawler.agent.get_driver')
    def test_get_page_text_removes_script_tags(self, mock_get_driver):
        """Test that script tags are removed."""
        from support_agent.sub_agents.crawler.agent import get_page_text

        mock_driver = MagicMock()
        mock_driver.page_source = COMPLEX_HTML
        mock_get_driver.return_value = mock_driver

        result = get_page_text()

        assert "console.log" not in result
        assert "function test()" not in result

    @patch('support_agent.sub_agents.crawler.agent.get_driver')
    def test_get_page_text_removes_style_tags(self, mock_get_driver):
        """Test that style tags are removed."""
        from support_agent.sub_agents.crawler.agent import get_page_text

        mock_driver = MagicMock()
        mock_driver.page_source = COMPLEX_HTML
        mock_get_driver.return_value = mock_driver

        result = get_page_text()

        assert "font-family" not in result
        assert "display: none" not in result

    @patch('support_agent.sub_agents.crawler.agent.get_driver')
    def test_get_page_text_removes_nav_tags(self, mock_get_driver):
        """Test that nav tags are removed."""
        from support_agent.sub_agents.crawler.agent import get_page_text

        mock_driver = MagicMock()
        mock_driver.page_source = COMPLEX_HTML
        mock_get_driver.return_value = mock_driver

        result = get_page_text()

        # Nav content should not appear
        assert "Home" not in result or result.count("Home") == 0

    @patch('support_agent.sub_agents.crawler.agent.get_driver')
    def test_get_page_text_removes_footer_tags(self, mock_get_driver):
        """Test that footer tags are removed."""
        from support_agent.sub_agents.crawler.agent import get_page_text

        mock_driver = MagicMock()
        mock_driver.page_source = COMPLEX_HTML
        mock_get_driver.return_value = mock_driver

        result = get_page_text()

        assert "Copyright 2024" not in result

    @patch('support_agent.sub_agents.crawler.agent.get_driver')
    def test_get_page_text_removes_aside_tags(self, mock_get_driver):
        """Test that aside tags are removed."""
        from support_agent.sub_agents.crawler.agent import get_page_text

        mock_driver = MagicMock()
        mock_driver.page_source = COMPLEX_HTML
        mock_get_driver.return_value = mock_driver

        result = get_page_text()

        assert "Related Links" not in result

    @patch('support_agent.sub_agents.crawler.agent.get_driver')
    def test_get_page_text_removes_header_tags(self, mock_get_driver):
        """Test that header tags are removed."""
        from support_agent.sub_agents.crawler.agent import get_page_text

        mock_driver = MagicMock()
        html_with_header = """
        <html>
        <body>
            <header>Header Content To Remove</header>
            <main>Main Content To Keep</main>
        </body>
        </html>
        """
        mock_driver.page_source = html_with_header
        mock_get_driver.return_value = mock_driver

        result = get_page_text()

        assert "Main Content To Keep" in result
        assert "Header Content To Remove" not in result

    @patch('support_agent.sub_agents.crawler.agent.get_driver')
    def test_get_page_text_preserves_main_content(self, mock_get_driver):
        """Test that main content is preserved."""
        from support_agent.sub_agents.crawler.agent import get_page_text

        mock_driver = MagicMock()
        mock_driver.page_source = COMPLEX_HTML
        mock_get_driver.return_value = mock_driver

        result = get_page_text()

        for keyword in EXPECTED_CLEANED_TEXT_KEYWORDS:
            assert keyword in result, f"Expected '{keyword}' to be in result"

    @patch('support_agent.sub_agents.crawler.agent.get_driver')
    def test_get_page_text_escapes_quotes(self, mock_get_driver):
        """Test that quotation marks are escaped for JSON."""
        from support_agent.sub_agents.crawler.agent import get_page_text

        mock_driver = MagicMock()
        mock_driver.page_source = COMPLEX_HTML
        mock_get_driver.return_value = mock_driver

        result = get_page_text()

        # Quotes should be escaped
        assert '\\"' in result or "double quotes" in result

    @patch('support_agent.sub_agents.crawler.agent.get_driver')
    def test_get_page_text_empty_page(self, mock_get_driver):
        """Test handling of empty page."""
        from support_agent.sub_agents.crawler.agent import get_page_text

        mock_driver = MagicMock()
        mock_driver.page_source = EMPTY_HTML
        mock_get_driver.return_value = mock_driver

        result = get_page_text()

        # Should return empty or minimal string
        assert isinstance(result, str)

    @patch('support_agent.sub_agents.crawler.agent.get_driver')
    def test_get_page_text_length_limit(self, mock_get_driver):
        """Test that output is limited to max characters."""
        from support_agent.sub_agents.crawler.agent import get_page_text

        mock_driver = MagicMock()
        # Create HTML with very long content
        long_content = "x" * 5000000
        html = f"<html><body><p>{long_content}</p></body></html>"
        mock_driver.page_source = html
        mock_get_driver.return_value = mock_driver

        result = get_page_text()

        # Should be limited to 4,000,000 characters
        assert len(result) <= 4000000

    @patch('support_agent.sub_agents.crawler.agent.get_driver')
    def test_get_page_text_removes_path_tags(self, mock_get_driver):
        """Test that SVG path tags are removed."""
        from support_agent.sub_agents.crawler.agent import get_page_text

        mock_driver = MagicMock()
        html_with_path = """
        <html>
        <body>
            <svg><path d="M0 0 L10 10" /></svg>
            <p>Real content</p>
        </body>
        </html>
        """
        mock_driver.page_source = html_with_path
        mock_get_driver.return_value = mock_driver

        result = get_page_text()

        assert "M0 0 L10 10" not in result
        assert "Real content" in result


class TestExtractStructuredContent:
    """Tests for the extract_structured_content function."""

    def test_extract_structured_content_returns_prompt(self):
        """Test that function returns formatted analysis prompt."""
        from support_agent.sub_agents.crawler.agent import extract_structured_content

        mock_context = MagicMock()
        page_text = "Sample page content"
        user_task = "Extract product information"

        result = extract_structured_content(page_text, user_task, mock_context)

        assert isinstance(result, str)
        assert page_text in result or "Sample" in result
        assert user_task in result or "Extract" in result
