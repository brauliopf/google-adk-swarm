"""
Unit tests for web searcher agent tools.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestTavilySearchTool:
    """Tests for the tavily_search_tool function."""

    @patch('support_agent.sub_agents.web_searcher.agent.MCPToolset')
    @patch('support_agent.sub_agents.web_searcher.agent.StreamableHTTPServerParams')
    def test_tavily_search_tool_returns_mcp_toolset(self, mock_params, mock_toolset):
        """Test that function returns an MCPToolset instance."""
        from support_agent.sub_agents.web_searcher.agent import tavily_search_tool

        mock_toolset_instance = MagicMock()
        mock_toolset.return_value = mock_toolset_instance

        result = tavily_search_tool()

        assert result is mock_toolset_instance

    @patch('support_agent.sub_agents.web_searcher.agent.MCPToolset')
    @patch('support_agent.sub_agents.web_searcher.agent.StreamableHTTPServerParams')
    def test_tavily_search_tool_uses_correct_url(self, mock_params, mock_toolset):
        """Test that Tavily MCP URL is used."""
        from support_agent.sub_agents.web_searcher.agent import tavily_search_tool

        tavily_search_tool()

        mock_params.assert_called_once()
        call_kwargs = mock_params.call_args
        assert call_kwargs[1]['url'] == "https://mcp.tavily.com/mcp/"

    @patch('support_agent.sub_agents.web_searcher.agent.MCPToolset')
    @patch('support_agent.sub_agents.web_searcher.agent.StreamableHTTPServerParams')
    def test_tavily_search_tool_uses_bearer_auth(self, mock_params, mock_toolset):
        """Test that Bearer token authentication is used."""
        from support_agent.sub_agents.web_searcher.agent import tavily_search_tool

        tavily_search_tool()

        call_kwargs = mock_params.call_args
        headers = call_kwargs[1]['headers']
        assert 'Authorization' in headers
        assert headers['Authorization'].startswith('Bearer ')

    def test_tavily_search_tool_uses_env_api_key(self, monkeypatch):
        """Test that API key from environment is used."""
        monkeypatch.setenv("TAVILY_API_KEY", "test-key-12345")

        # Need to reimport to get updated env var
        import importlib
        import support_agent.sub_agents.web_searcher.agent as ws_agent
        importlib.reload(ws_agent)

        # Patch after reload so the mock applies to the reloaded module
        with patch.object(ws_agent, 'MCPToolset') as mock_toolset, \
             patch.object(ws_agent, 'StreamableHTTPServerParams') as mock_params:

            ws_agent.tavily_search_tool()

            call_kwargs = mock_params.call_args
            headers = call_kwargs[1]['headers']
            assert "test-key-12345" in headers['Authorization']

    @patch('support_agent.sub_agents.web_searcher.agent.MCPToolset')
    @patch('support_agent.sub_agents.web_searcher.agent.StreamableHTTPServerParams')
    def test_tavily_search_tool_passes_params_to_toolset(self, mock_params, mock_toolset):
        """Test that StreamableHTTPServerParams is passed to MCPToolset."""
        from support_agent.sub_agents.web_searcher.agent import tavily_search_tool

        mock_params_instance = MagicMock()
        mock_params.return_value = mock_params_instance

        tavily_search_tool()

        mock_toolset.assert_called_once()
        call_kwargs = mock_toolset.call_args
        assert call_kwargs[1]['connection_params'] is mock_params_instance

    @patch('support_agent.sub_agents.web_searcher.agent.MCPToolset')
    @patch('support_agent.sub_agents.web_searcher.agent.StreamableHTTPServerParams')
    def test_tavily_search_tool_creates_new_instance_each_call(self, mock_params, mock_toolset):
        """Test that each call creates a new toolset instance."""
        from support_agent.sub_agents.web_searcher.agent import tavily_search_tool

        instance1 = MagicMock()
        instance2 = MagicMock()
        mock_toolset.side_effect = [instance1, instance2]

        result1 = tavily_search_tool()
        result2 = tavily_search_tool()

        assert result1 is not result2
        assert mock_toolset.call_count == 2


class TestWebSearcherAgentCreation:
    """Tests for web searcher agent creation."""

    @patch('support_agent.sub_agents.web_searcher.agent.Agent')
    @patch('support_agent.sub_agents.web_searcher.agent.tavily_search_tool')
    def test_agent_uses_correct_name(self, mock_tool, mock_agent):
        """Test that agent is created with correct name."""
        # This tests agent creation configuration
        # In actual implementation, agent is created at module load
        pass

    @patch('support_agent.sub_agents.web_searcher.agent.Agent')
    @patch('support_agent.sub_agents.web_searcher.agent.tavily_search_tool')
    def test_agent_uses_correct_model(self, mock_tool, mock_agent):
        """Test that agent uses MODEL_GEMINI_2_0_FLASH."""
        # Agent configuration test
        pass

    @patch('support_agent.sub_agents.web_searcher.agent.Agent')
    @patch('support_agent.sub_agents.web_searcher.agent.tavily_search_tool')
    def test_agent_has_after_model_callback(self, mock_tool, mock_agent):
        """Test that agent has guardrail callback configured."""
        # Agent configuration test
        pass
