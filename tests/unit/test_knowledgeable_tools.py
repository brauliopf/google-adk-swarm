"""
Unit tests for knowledgeable agent tools.
"""

import pytest
import json
import numpy as np
from unittest.mock import patch, mock_open, MagicMock

from tests.fixtures.mock_data import (
    MOCK_KNOWLEDGE_BASE,
    MOCK_KNOWLEDGE_BASE_JSON,
    MOCK_EMBEDDING_RESPONSE
)


class TestLoadKnowledgeBase:
    """Tests for the load_knowledge_base function."""

    def test_load_knowledge_base_success(self, reset_knowledgeable_cache):
        """Test successful loading of knowledge base."""
        from support_agent.sub_agents.knowledgeable.agent import load_knowledge_base

        with patch("builtins.open", mock_open(read_data=MOCK_KNOWLEDGE_BASE_JSON)):
            result = load_knowledge_base()

        assert isinstance(result, dict)
        assert len(result) == 3
        assert "https://www.infinitepay.io/products" in result

    def test_load_knowledge_base_caching(self, reset_knowledgeable_cache):
        """Test that knowledge base is cached after first load."""
        from support_agent.sub_agents.knowledgeable import agent as kb_agent
        from support_agent.sub_agents.knowledgeable.agent import load_knowledge_base

        with patch("builtins.open", mock_open(read_data=MOCK_KNOWLEDGE_BASE_JSON)) as mock_file:
            # First call should read file
            result1 = load_knowledge_base()
            # Second call should use cache
            result2 = load_knowledge_base()

        # File should only be opened once
        assert mock_file.call_count == 1
        assert result1 is result2

    def test_load_knowledge_base_returns_dict_structure(self, reset_knowledgeable_cache):
        """Test that knowledge base has correct structure."""
        from support_agent.sub_agents.knowledgeable.agent import load_knowledge_base

        with patch("builtins.open", mock_open(read_data=MOCK_KNOWLEDGE_BASE_JSON)):
            result = load_knowledge_base()

        # Should have URLs as keys
        for key in result.keys():
            assert key.startswith("http")

        # Should have strings as values
        for value in result.values():
            assert isinstance(value, str)


class TestGetEmbedding:
    """Tests for the get_embedding function."""

    @patch('support_agent.sub_agents.knowledgeable.agent.genai')
    def test_get_embedding_returns_numpy_array(self, mock_genai):
        """Test that embedding is returned as numpy array."""
        from support_agent.sub_agents.knowledgeable.agent import get_embedding

        mock_genai.embed_content.return_value = {
            'embedding': [0.1, 0.2, 0.3, 0.4, 0.5]
        }

        result = get_embedding("test text")

        assert isinstance(result, np.ndarray)
        assert len(result) == 5

    @patch('support_agent.sub_agents.knowledgeable.agent.genai')
    def test_get_embedding_uses_correct_model(self, mock_genai):
        """Test that correct embedding model is used."""
        from support_agent.sub_agents.knowledgeable.agent import get_embedding

        mock_genai.embed_content.return_value = {'embedding': [0.1] * 768}

        get_embedding("test text")

        mock_genai.embed_content.assert_called_once()
        call_kwargs = mock_genai.embed_content.call_args
        assert call_kwargs[1]['model'] == "models/text-embedding-004"

    @patch('support_agent.sub_agents.knowledgeable.agent.genai')
    def test_get_embedding_uses_retrieval_task_type(self, mock_genai):
        """Test that retrieval_document task type is used."""
        from support_agent.sub_agents.knowledgeable.agent import get_embedding

        mock_genai.embed_content.return_value = {'embedding': [0.1] * 768}

        get_embedding("test text")

        call_kwargs = mock_genai.embed_content.call_args
        assert call_kwargs[1]['task_type'] == "retrieval_document"

    @patch('support_agent.sub_agents.knowledgeable.agent.genai')
    def test_get_embedding_with_custom_model(self, mock_genai):
        """Test embedding with custom model parameter."""
        from support_agent.sub_agents.knowledgeable.agent import get_embedding

        mock_genai.embed_content.return_value = {'embedding': [0.1] * 768}
        custom_model = "models/custom-embedding"

        get_embedding("test text", model=custom_model)

        call_kwargs = mock_genai.embed_content.call_args
        assert call_kwargs[1]['model'] == custom_model


class TestComputeEmbeddings:
    """Tests for the compute_embeddings function."""

    @patch('support_agent.sub_agents.knowledgeable.agent.get_embedding')
    def test_compute_embeddings_returns_list(self, mock_get_embedding, reset_knowledgeable_cache):
        """Test that embeddings are returned as list."""
        from support_agent.sub_agents.knowledgeable.agent import compute_embeddings

        mock_get_embedding.return_value = np.array([0.1, 0.2, 0.3])

        result = compute_embeddings(MOCK_KNOWLEDGE_BASE)

        assert isinstance(result, list)
        assert len(result) == 3

    @patch('support_agent.sub_agents.knowledgeable.agent.get_embedding')
    def test_compute_embeddings_structure(self, mock_get_embedding, reset_knowledgeable_cache):
        """Test that each embedding entry has correct structure."""
        from support_agent.sub_agents.knowledgeable.agent import compute_embeddings

        mock_embedding = np.array([0.1, 0.2, 0.3])
        mock_get_embedding.return_value = mock_embedding

        result = compute_embeddings(MOCK_KNOWLEDGE_BASE)

        for entry in result:
            assert 'url' in entry
            assert 'embedding' in entry
            assert 'content' in entry
            assert isinstance(entry['url'], str)
            assert isinstance(entry['embedding'], np.ndarray)
            assert isinstance(entry['content'], str)

    @patch('support_agent.sub_agents.knowledgeable.agent.get_embedding')
    def test_compute_embeddings_caching(self, mock_get_embedding, reset_knowledgeable_cache):
        """Test that embeddings are cached."""
        from support_agent.sub_agents.knowledgeable.agent import compute_embeddings

        mock_get_embedding.return_value = np.array([0.1, 0.2, 0.3])

        # First call
        result1 = compute_embeddings(MOCK_KNOWLEDGE_BASE)
        # Second call should use cache
        result2 = compute_embeddings(MOCK_KNOWLEDGE_BASE)

        # get_embedding should only be called for first computation
        assert mock_get_embedding.call_count == 3  # Once per KB entry
        assert result1 is result2

    @patch('support_agent.sub_agents.knowledgeable.agent.get_embedding')
    def test_compute_embeddings_calls_for_each_entry(self, mock_get_embedding, reset_knowledgeable_cache):
        """Test that get_embedding is called for each KB entry."""
        from support_agent.sub_agents.knowledgeable.agent import compute_embeddings

        mock_get_embedding.return_value = np.array([0.1, 0.2, 0.3])

        compute_embeddings(MOCK_KNOWLEDGE_BASE)

        assert mock_get_embedding.call_count == len(MOCK_KNOWLEDGE_BASE)


class TestCosineSimilarity:
    """Tests for the cosine_similarity function."""

    def test_cosine_similarity_identical_vectors(self):
        """Test similarity of identical vectors is 1."""
        from support_agent.sub_agents.knowledgeable.agent import cosine_similarity

        vec = np.array([1.0, 2.0, 3.0])
        result = cosine_similarity(vec, vec)

        assert np.isclose(result, 1.0)

    def test_cosine_similarity_orthogonal_vectors(self):
        """Test similarity of orthogonal vectors is 0."""
        from support_agent.sub_agents.knowledgeable.agent import cosine_similarity

        vec1 = np.array([1.0, 0.0, 0.0])
        vec2 = np.array([0.0, 1.0, 0.0])
        result = cosine_similarity(vec1, vec2)

        assert np.isclose(result, 0.0)

    def test_cosine_similarity_opposite_vectors(self):
        """Test similarity of opposite vectors is -1."""
        from support_agent.sub_agents.knowledgeable.agent import cosine_similarity

        vec1 = np.array([1.0, 2.0, 3.0])
        vec2 = np.array([-1.0, -2.0, -3.0])
        result = cosine_similarity(vec1, vec2)

        assert np.isclose(result, -1.0)

    def test_cosine_similarity_known_value(self):
        """Test with known cosine similarity value."""
        from support_agent.sub_agents.knowledgeable.agent import cosine_similarity

        vec1 = np.array([1.0, 0.0])
        vec2 = np.array([1.0, 1.0])
        result = cosine_similarity(vec1, vec2)

        # cos(45 degrees) = 1/sqrt(2) ≈ 0.7071
        expected = 1 / np.sqrt(2)
        assert np.isclose(result, expected)

    def test_cosine_similarity_different_magnitudes(self):
        """Test that magnitude doesn't affect similarity."""
        from support_agent.sub_agents.knowledgeable.agent import cosine_similarity

        vec1 = np.array([1.0, 2.0, 3.0])
        vec2 = np.array([2.0, 4.0, 6.0])  # Same direction, double magnitude
        result = cosine_similarity(vec1, vec2)

        assert np.isclose(result, 1.0)

    def test_cosine_similarity_high_dimensional(self):
        """Test with high-dimensional vectors like real embeddings."""
        from support_agent.sub_agents.knowledgeable.agent import cosine_similarity

        np.random.seed(42)
        vec1 = np.random.rand(768)
        vec2 = np.random.rand(768)
        result = cosine_similarity(vec1, vec2)

        # Result should be between -1 and 1
        assert -1.0 <= result <= 1.0


class TestQueryKnowledgeBase:
    """Tests for the query_knowledge_base function."""

    @patch('support_agent.sub_agents.knowledgeable.agent.get_embedding')
    @patch('support_agent.sub_agents.knowledgeable.agent.compute_embeddings')
    @patch('support_agent.sub_agents.knowledgeable.agent.load_knowledge_base')
    def test_query_knowledge_base_returns_list(
        self, mock_load_kb, mock_compute, mock_get_embedding, reset_knowledgeable_cache
    ):
        """Test that query returns a list of results."""
        from support_agent.sub_agents.knowledgeable.agent import query_knowledge_base

        mock_load_kb.return_value = MOCK_KNOWLEDGE_BASE
        mock_compute.return_value = [
            {"url": "url1", "embedding": np.array([0.1, 0.2]), "content": "content1"},
            {"url": "url2", "embedding": np.array([0.2, 0.3]), "content": "content2"},
        ]
        mock_get_embedding.return_value = np.array([0.1, 0.2])

        result = query_knowledge_base("test query")

        assert isinstance(result, list)

    @patch('support_agent.sub_agents.knowledgeable.agent.get_embedding')
    @patch('support_agent.sub_agents.knowledgeable.agent.compute_embeddings')
    @patch('support_agent.sub_agents.knowledgeable.agent.load_knowledge_base')
    def test_query_knowledge_base_result_structure(
        self, mock_load_kb, mock_compute, mock_get_embedding, reset_knowledgeable_cache
    ):
        """Test that each result has correct structure."""
        from support_agent.sub_agents.knowledgeable.agent import query_knowledge_base

        mock_load_kb.return_value = MOCK_KNOWLEDGE_BASE
        mock_compute.return_value = [
            {"url": "url1", "embedding": np.array([0.1, 0.2]), "content": "content1"},
            {"url": "url2", "embedding": np.array([0.2, 0.3]), "content": "content2"},
        ]
        mock_get_embedding.return_value = np.array([0.1, 0.2])

        result = query_knowledge_base("test query")

        for item in result:
            assert 'url' in item
            assert 'score' in item
            assert 'content' in item

    @patch('support_agent.sub_agents.knowledgeable.agent.get_embedding')
    @patch('support_agent.sub_agents.knowledgeable.agent.compute_embeddings')
    @patch('support_agent.sub_agents.knowledgeable.agent.load_knowledge_base')
    def test_query_knowledge_base_default_top_k(
        self, mock_load_kb, mock_compute, mock_get_embedding, reset_knowledgeable_cache
    ):
        """Test that default top_k is 2."""
        from support_agent.sub_agents.knowledgeable.agent import query_knowledge_base

        mock_load_kb.return_value = MOCK_KNOWLEDGE_BASE
        mock_compute.return_value = [
            {"url": "url1", "embedding": np.array([0.9, 0.1]), "content": "content1"},
            {"url": "url2", "embedding": np.array([0.5, 0.5]), "content": "content2"},
            {"url": "url3", "embedding": np.array([0.1, 0.9]), "content": "content3"},
        ]
        mock_get_embedding.return_value = np.array([0.9, 0.1])

        result = query_knowledge_base("test query")

        assert len(result) == 2

    @patch('support_agent.sub_agents.knowledgeable.agent.get_embedding')
    @patch('support_agent.sub_agents.knowledgeable.agent.compute_embeddings')
    @patch('support_agent.sub_agents.knowledgeable.agent.load_knowledge_base')
    def test_query_knowledge_base_custom_top_k(
        self, mock_load_kb, mock_compute, mock_get_embedding, reset_knowledgeable_cache
    ):
        """Test with custom top_k parameter."""
        from support_agent.sub_agents.knowledgeable.agent import query_knowledge_base

        mock_load_kb.return_value = MOCK_KNOWLEDGE_BASE
        mock_compute.return_value = [
            {"url": "url1", "embedding": np.array([0.9, 0.1]), "content": "content1"},
            {"url": "url2", "embedding": np.array([0.5, 0.5]), "content": "content2"},
            {"url": "url3", "embedding": np.array([0.1, 0.9]), "content": "content3"},
        ]
        mock_get_embedding.return_value = np.array([0.9, 0.1])

        result = query_knowledge_base("test query", top_k=1)

        assert len(result) == 1

    @patch('support_agent.sub_agents.knowledgeable.agent.get_embedding')
    @patch('support_agent.sub_agents.knowledgeable.agent.compute_embeddings')
    @patch('support_agent.sub_agents.knowledgeable.agent.load_knowledge_base')
    def test_query_knowledge_base_sorted_by_score(
        self, mock_load_kb, mock_compute, mock_get_embedding, reset_knowledgeable_cache
    ):
        """Test that results are sorted by score descending."""
        from support_agent.sub_agents.knowledgeable.agent import query_knowledge_base

        mock_load_kb.return_value = MOCK_KNOWLEDGE_BASE
        # Create embeddings where url1 will have highest similarity
        mock_compute.return_value = [
            {"url": "url1", "embedding": np.array([1.0, 0.0]), "content": "best match"},
            {"url": "url2", "embedding": np.array([0.0, 1.0]), "content": "worst match"},
            {"url": "url3", "embedding": np.array([0.5, 0.5]), "content": "medium match"},
        ]
        mock_get_embedding.return_value = np.array([1.0, 0.0])

        result = query_knowledge_base("test query", top_k=3)

        # Results should be sorted by score descending
        scores = [item['score'] for item in result]
        assert scores == sorted(scores, reverse=True)
        assert result[0]['url'] == "url1"

    @patch('support_agent.sub_agents.knowledgeable.agent.get_embedding')
    @patch('support_agent.sub_agents.knowledgeable.agent.compute_embeddings')
    @patch('support_agent.sub_agents.knowledgeable.agent.load_knowledge_base')
    def test_query_knowledge_base_top_k_larger_than_results(
        self, mock_load_kb, mock_compute, mock_get_embedding, reset_knowledgeable_cache
    ):
        """Test when top_k is larger than available results."""
        from support_agent.sub_agents.knowledgeable.agent import query_knowledge_base

        mock_load_kb.return_value = {"url1": "content1"}
        mock_compute.return_value = [
            {"url": "url1", "embedding": np.array([0.1, 0.2]), "content": "content1"},
        ]
        mock_get_embedding.return_value = np.array([0.1, 0.2])

        result = query_knowledge_base("test query", top_k=10)

        # Should return all available results
        assert len(result) == 1
