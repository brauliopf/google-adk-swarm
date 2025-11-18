"""Unit tests for the knowledgeable agent."""

import json
import os
import unittest
from unittest.mock import patch, mock_open
import sys

# Add the project root to the path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from support_agent.sub_agents.knowledgeable.agent import load_knowledge_base


class TestLoadKnowledgeBase(unittest.TestCase):
    """Test cases for the load_knowledge_base function."""

    def setUp(self):
        """Set up test fixtures before each test."""
        # Reset the global cache before each test
        import support_agent.sub_agents.knowledgeable.agent as agent_module
        agent_module._knowledge_base_cache = None

    def test_load_knowledge_base_with_correct_structure(self):
        """Test that load_knowledge_base correctly loads data with 'knowledge_base' key."""
        # Create mock data with the expected structure
        mock_data = {
            "knowledge_base": [
                {
                    "url": "https://example.com/page1",
                    "title": "Test Page 1",
                    "content": "This is test content 1"
                },
                {
                    "url": "https://example.com/page2",
                    "title": "Test Page 2",
                    "content": "This is test content 2"
                }
            ]
        }

        # Mock the file reading operation
        with patch('builtins.open', mock_open(read_data=json.dumps(mock_data))):
            result = load_knowledge_base()

        # Assert that the function returns the knowledge_base list
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["url"], "https://example.com/page1")
        self.assertEqual(result[0]["title"], "Test Page 1")
        self.assertEqual(result[1]["url"], "https://example.com/page2")

    def test_load_knowledge_base_from_actual_file(self):
        """Test that load_knowledge_base reads from the actual mock_knowledge_base.json file."""
        # Get the actual file path
        mock_data_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "..",
            "data",
            "mock_knowledge_base.json"
        )

        # Verify the file exists
        self.assertTrue(os.path.exists(mock_data_path),
                       f"mock_knowledge_base.json should exist at {mock_data_path}")

        # Load the actual file to verify its structure
        with open(mock_data_path, 'r', encoding='utf-8') as f:
            actual_data = json.load(f)

        # Verify it's a dictionary
        self.assertIsInstance(actual_data, dict,
                            "mock_knowledge_base.json should contain a JSON object")

        # Load using the function
        result = load_knowledge_base()

        # The function looks for a 'knowledge_base' key
        # If it doesn't exist, it returns an empty list
        if "knowledge_base" in actual_data:
            self.assertEqual(result, actual_data["knowledge_base"])
        else:
            # Current behavior: returns empty list if 'knowledge_base' key doesn't exist
            self.assertEqual(result, [])
            # Document the current structure for future reference
            self.assertIsInstance(actual_data, dict)
            # The file currently has URLs as keys, not a 'knowledge_base' list

    def test_load_knowledge_base_caching(self):
        """Test that load_knowledge_base caches the result on subsequent calls."""
        mock_data = {
            "knowledge_base": [
                {"url": "https://example.com", "title": "Test", "content": "Content"}
            ]
        }

        # First call should read the file
        with patch('builtins.open', mock_open(read_data=json.dumps(mock_data))) as mock_file:
            result1 = load_knowledge_base()
            # File should be opened once
            mock_file.assert_called_once()

        # Second call should use cache, not read file again
        with patch('builtins.open', mock_open(read_data=json.dumps(mock_data))) as mock_file:
            result2 = load_knowledge_base()
            # File should NOT be opened again
            mock_file.assert_not_called()

        # Both results should be the same
        self.assertEqual(result1, result2)

    def test_load_knowledge_base_empty_list_when_key_missing(self):
        """Test that load_knowledge_base returns empty list when 'knowledge_base' key is missing."""
        # Mock data without 'knowledge_base' key (like current actual file)
        mock_data = {
            "https://example.com": "Some content",
            "https://example.org": "More content"
        }

        with patch('builtins.open', mock_open(read_data=json.dumps(mock_data))):
            result = load_knowledge_base()

        # Should return empty list when key doesn't exist
        self.assertEqual(result, [])

    def test_load_knowledge_base_file_path_construction(self):
        """Test that the file path is correctly constructed."""
        with patch('builtins.open', mock_open(read_data='{"knowledge_base": []}')) as mock_file:
            load_knowledge_base()

            # Get the path that was used to open the file
            call_args = mock_file.call_args[0][0]

            # Verify the path ends with the expected file
            self.assertTrue(call_args.endswith('data/mock_knowledge_base.json') or
                          call_args.endswith('data\\mock_knowledge_base.json'),
                          f"Path should end with data/mock_knowledge_base.json, got: {call_args}")


if __name__ == '__main__':
    unittest.main()
