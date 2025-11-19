"""
Unit tests for guardrails and callbacks.
"""

import pytest
from unittest.mock import patch, MagicMock
from typing import Optional

from tests.fixtures.mock_data import (
    PALMEIRAS_LOSS_RESPONSE,
    PALMEIRAS_WIN_RESPONSE,
    NEUTRAL_RESPONSE,
    GUARDRAIL_YES_RESPONSE,
    GUARDRAIL_NO_RESPONSE
)


class TestBlockPalmeirasHaters:
    """Tests for the block_palmeiras_haters callback."""

    def create_mock_llm_response(self, text: Optional[str] = None, has_function_call: bool = False):
        """Helper to create mock LLM responses."""
        from google.adk.agents.llm_agent import LlmResponse

        mock_response = MagicMock(spec=LlmResponse)
        mock_response.content = MagicMock()

        if text is not None:
            mock_part = MagicMock()
            mock_part.text = text
            mock_response.content.parts = [mock_part]
        elif has_function_call:
            # Response with only function call, no text
            mock_part = MagicMock(spec=['function_call'])
            del mock_part.text  # Remove text attribute
            mock_response.content.parts = [mock_part]
        else:
            mock_response.content.parts = []

        return mock_response

    def create_mock_callback_context(self):
        """Helper to create mock callback context."""
        from google.adk.agents.llm_agent import CallbackContext

        mock_context = MagicMock(spec=CallbackContext)
        mock_context.agent_name = "web_searcher_agent"
        mock_context.state = {}

        return mock_context

    @patch('support_agent.sub_agents.web_searcher.guardrails.genai')
    def test_blocks_palmeiras_loss_response(self, mock_genai):
        """Test that response mentioning Palmeiras loss is blocked."""
        from support_agent.sub_agents.web_searcher.guardrails import block_palmeiras_haters

        # Setup mock to return YES (Palmeiras lost)
        mock_client = MagicMock()
        mock_check_response = MagicMock()
        mock_check_response.text = GUARDRAIL_YES_RESPONSE
        mock_client.models.generate_content.return_value = mock_check_response
        mock_genai.Client.return_value = mock_client

        context = self.create_mock_callback_context()
        response = self.create_mock_llm_response(text=PALMEIRAS_LOSS_RESPONSE)

        result = block_palmeiras_haters(context, response)

        # Should return a blocking response
        assert result is not None
        assert context.state.get("guardrail_palmeiras_loss_triggered") == True

    @patch('support_agent.sub_agents.web_searcher.guardrails.genai')
    def test_allows_palmeiras_win_response(self, mock_genai):
        """Test that response mentioning Palmeiras win is allowed."""
        from support_agent.sub_agents.web_searcher.guardrails import block_palmeiras_haters

        # Setup mock to return NO (Palmeiras did not lose)
        mock_client = MagicMock()
        mock_check_response = MagicMock()
        mock_check_response.text = GUARDRAIL_NO_RESPONSE
        mock_client.models.generate_content.return_value = mock_check_response
        mock_genai.Client.return_value = mock_client

        context = self.create_mock_callback_context()
        response = self.create_mock_llm_response(text=PALMEIRAS_WIN_RESPONSE)

        result = block_palmeiras_haters(context, response)

        # Should return None (allow response through)
        assert result is None
        assert "guardrail_palmeiras_loss_triggered" not in context.state

    @patch('support_agent.sub_agents.web_searcher.guardrails.genai')
    def test_allows_neutral_response(self, mock_genai):
        """Test that neutral response is allowed."""
        from support_agent.sub_agents.web_searcher.guardrails import block_palmeiras_haters

        # Setup mock to return NO
        mock_client = MagicMock()
        mock_check_response = MagicMock()
        mock_check_response.text = GUARDRAIL_NO_RESPONSE
        mock_client.models.generate_content.return_value = mock_check_response
        mock_genai.Client.return_value = mock_client

        context = self.create_mock_callback_context()
        response = self.create_mock_llm_response(text=NEUTRAL_RESPONSE)

        result = block_palmeiras_haters(context, response)

        # Should return None (allow response through)
        assert result is None

    @patch('support_agent.sub_agents.web_searcher.guardrails.genai')
    def test_allows_function_call_only_response(self, mock_genai):
        """Test that response with only function call is allowed."""
        from support_agent.sub_agents.web_searcher.guardrails import block_palmeiras_haters

        context = self.create_mock_callback_context()
        response = self.create_mock_llm_response(has_function_call=True)

        result = block_palmeiras_haters(context, response)

        # Should return None (allow response through)
        # genai should not be called since there's no text to check
        assert result is None
        mock_genai.Client.assert_not_called()

    @patch('support_agent.sub_agents.web_searcher.guardrails.genai')
    def test_allows_empty_response(self, mock_genai):
        """Test that empty response is allowed."""
        from support_agent.sub_agents.web_searcher.guardrails import block_palmeiras_haters

        context = self.create_mock_callback_context()
        response = self.create_mock_llm_response()  # No text, no function call

        result = block_palmeiras_haters(context, response)

        # Should return None (allow response through)
        assert result is None
        mock_genai.Client.assert_not_called()

    @patch('support_agent.sub_agents.web_searcher.guardrails.genai')
    def test_sets_state_flag_when_blocked(self, mock_genai):
        """Test that state flag is set when response is blocked."""
        from support_agent.sub_agents.web_searcher.guardrails import block_palmeiras_haters

        # Setup mock to return YES
        mock_client = MagicMock()
        mock_check_response = MagicMock()
        mock_check_response.text = GUARDRAIL_YES_RESPONSE
        mock_client.models.generate_content.return_value = mock_check_response
        mock_genai.Client.return_value = mock_client

        context = self.create_mock_callback_context()
        response = self.create_mock_llm_response(text=PALMEIRAS_LOSS_RESPONSE)

        block_palmeiras_haters(context, response)

        assert context.state["guardrail_palmeiras_loss_triggered"] == True

    @patch('support_agent.sub_agents.web_searcher.guardrails.genai')
    def test_uses_gemini_model_for_check(self, mock_genai):
        """Test that the guardrail uses gemini-2.0-flash for checking."""
        from support_agent.sub_agents.web_searcher.guardrails import block_palmeiras_haters

        mock_client = MagicMock()
        mock_check_response = MagicMock()
        mock_check_response.text = GUARDRAIL_NO_RESPONSE
        mock_client.models.generate_content.return_value = mock_check_response
        mock_genai.Client.return_value = mock_client

        context = self.create_mock_callback_context()
        response = self.create_mock_llm_response(text="Some text")

        block_palmeiras_haters(context, response)

        # Verify the model used
        call_args = mock_client.models.generate_content.call_args
        assert "gemini-2.0-flash" in str(call_args)

    @patch('support_agent.sub_agents.web_searcher.guardrails.genai')
    def test_blocking_response_content(self, mock_genai):
        """Test that blocking response has appropriate message."""
        from support_agent.sub_agents.web_searcher.guardrails import block_palmeiras_haters
        from google.adk.agents.llm_agent import LlmResponse

        # Setup mock to return YES
        mock_client = MagicMock()
        mock_check_response = MagicMock()
        mock_check_response.text = GUARDRAIL_YES_RESPONSE
        mock_client.models.generate_content.return_value = mock_check_response
        mock_genai.Client.return_value = mock_client

        context = self.create_mock_callback_context()
        response = self.create_mock_llm_response(text=PALMEIRAS_LOSS_RESPONSE)

        result = block_palmeiras_haters(context, response)

        # Should return an LlmResponse with blocking message
        assert result is not None
        assert isinstance(result, LlmResponse)

    @patch('support_agent.sub_agents.web_searcher.guardrails.genai')
    def test_multipart_response_with_text(self, mock_genai):
        """Test response with multiple parts including text."""
        from support_agent.sub_agents.web_searcher.guardrails import block_palmeiras_haters

        mock_client = MagicMock()
        mock_check_response = MagicMock()
        mock_check_response.text = GUARDRAIL_NO_RESPONSE
        mock_client.models.generate_content.return_value = mock_check_response
        mock_genai.Client.return_value = mock_client

        context = self.create_mock_callback_context()

        # Create response with multiple parts
        from google.adk.agents.llm_agent import LlmResponse
        mock_response = MagicMock(spec=LlmResponse)
        mock_response.content = MagicMock()

        part1 = MagicMock()
        part1.text = "First part of text"
        part2 = MagicMock()
        part2.text = "Second part of text"
        mock_response.content.parts = [part1, part2]

        result = block_palmeiras_haters(context, mock_response)

        # Should process and check concatenated text
        assert result is None

    @patch('support_agent.sub_agents.web_searcher.guardrails.genai')
    def test_case_insensitivity_of_yes_response(self, mock_genai):
        """Test that YES check is case-insensitive."""
        from support_agent.sub_agents.web_searcher.guardrails import block_palmeiras_haters

        # Setup mock to return lowercase "yes"
        mock_client = MagicMock()
        mock_check_response = MagicMock()
        mock_check_response.text = "yes"
        mock_client.models.generate_content.return_value = mock_check_response
        mock_genai.Client.return_value = mock_client

        context = self.create_mock_callback_context()
        response = self.create_mock_llm_response(text=PALMEIRAS_LOSS_RESPONSE)

        result = block_palmeiras_haters(context, response)

        # Should still block even with lowercase response
        # The actual implementation uses .upper() so this should work
        assert result is not None

    @patch('support_agent.sub_agents.web_searcher.guardrails.genai')
    def test_preserves_original_response_when_allowed(self, mock_genai):
        """Test that None is returned when response is allowed."""
        from support_agent.sub_agents.web_searcher.guardrails import block_palmeiras_haters

        mock_client = MagicMock()
        mock_check_response = MagicMock()
        mock_check_response.text = GUARDRAIL_NO_RESPONSE
        mock_client.models.generate_content.return_value = mock_check_response
        mock_genai.Client.return_value = mock_client

        context = self.create_mock_callback_context()
        original_response = self.create_mock_llm_response(text=NEUTRAL_RESPONSE)

        result = block_palmeiras_haters(context, original_response)

        # Should return None to signal that original response should be used
        assert result is None


class TestGuardrailPrompt:
    """Tests for the guardrail check prompt."""

    @patch('support_agent.sub_agents.web_searcher.guardrails.genai')
    def test_check_prompt_includes_response_text(self, mock_genai):
        """Test that check prompt includes the response text."""
        from support_agent.sub_agents.web_searcher.guardrails import block_palmeiras_haters

        mock_client = MagicMock()
        mock_check_response = MagicMock()
        mock_check_response.text = GUARDRAIL_NO_RESPONSE
        mock_client.models.generate_content.return_value = mock_check_response
        mock_genai.Client.return_value = mock_client

        context = MagicMock()
        context.agent_name = "test"
        context.state = {}

        test_text = "Unique test response content 12345"
        response = MagicMock()
        mock_part = MagicMock()
        mock_part.text = test_text
        response.content = MagicMock()
        response.content.parts = [mock_part]

        block_palmeiras_haters(context, response)

        # Check that generate_content was called with text that includes response
        call_args = mock_client.models.generate_content.call_args
        prompt_contents = str(call_args)
        assert test_text in prompt_contents or "Unique test response" in prompt_contents
