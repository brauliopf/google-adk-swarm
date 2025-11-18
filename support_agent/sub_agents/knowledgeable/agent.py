from google.adk.agents.llm_agent import Agent
from . import prompt
import os
import json
import numpy as np
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

# Initialize embeddings model
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Cache for knowledge base data and embeddings
_knowledge_base_cache = None
_embeddings_cache = None


def load_knowledge_base() -> dict:
    """Load knowledge base data from mock.json file."""
    global _knowledge_base_cache

    if _knowledge_base_cache is not None:
        return _knowledge_base_cache

    mock_data_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "..",
        "data",
        "mock_knowledge_base.json"
    )

    with open(mock_data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    _knowledge_base_cache = data
    return _knowledge_base_cache


def get_embedding(text: str, model: str = "models/text-embedding-004") -> np.ndarray:
    """Generate embedding for given text using Google's embedding model."""
    result = genai.embed_content(
        model=model,
        content=text,
        task_type="retrieval_document"
    )
    return np.array(result['embedding'])


def compute_embeddings(knowledge_base: dict) -> list[dict]:
    """Compute embeddings for all content in the knowledge base."""
    global _embeddings_cache

    if _embeddings_cache is not None:
        return _embeddings_cache

    embeddings = []
    for url, content in knowledge_base.items():
        print(f"Computing embedding for item: {url}")
        embedding = get_embedding(content)
        embeddings.append({"url": url, "embedding": embedding, "content": content})
    _embeddings_cache = embeddings
    return embeddings
    

def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors."""
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    return dot_product / (norm1 * norm2)


def query_knowledge_base(query: str, top_k: int = 3) -> list[dict]:
    """
    Query the knowledge base using semantic search with embeddings.

    Args:
        query: The user's search query
        top_k: Number of top results to return (default: 2)

    Returns:
        A formatted string containing the most relevant results in markdown format.
    """
    # Load knowledge base and compute embeddings
    knowledge_base = load_knowledge_base()
    kb_embeddings = compute_embeddings(knowledge_base)

    # Get query embedding
    query_embedding = get_embedding(query, model="models/text-embedding-004")

    # Calculate similarities
    similarities = []
    print(f"Calculating similarities for query: {query}", f"Number of embeddings: {len(kb_embeddings)}")
    for i, kb_embedding in enumerate(kb_embeddings):
        similarity = cosine_similarity(query_embedding, kb_embedding['embedding'])
        similarities.append((i, similarity))

    # Sort by similarity (descending)
    similarities.sort(key=lambda x: x[1], reverse=True)

    # Get top-k results
    top_results = similarities[:top_k]

    # Format results
    results = []
    for idx, score in top_results:
        kb_item = kb_embeddings[idx]
        results.append({
            'url': kb_item['url'],
            'score': score,
            'content': kb_item['content'].strip()
        })

    return results


root_agent = Agent(
    model=os.getenv("MODEL_GEMINI_2_0_FLASH"),
    name="knowledgeable_agent",
    description="Queries the knowledge base and returns the most relevant information.",
    instruction=prompt.RETRIEVER_PROMPT,
    tools=[
        query_knowledge_base,
    ],
    output_key="knowledgeable_response",
)
