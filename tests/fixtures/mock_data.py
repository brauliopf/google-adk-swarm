"""
Mock data and responses for unit tests.
"""

import numpy as np


# Sample HTML pages for crawler tests
SIMPLE_HTML = """
<!DOCTYPE html>
<html>
<head><title>Simple Page</title></head>
<body>
    <p>Hello World</p>
</body>
</html>
"""

COMPLEX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Complex Page</title>
    <script>
        function test() { console.log('script content'); }
    </script>
    <style>
        body { font-family: Arial; }
        .hidden { display: none; }
    </style>
</head>
<body>
    <header>
        <nav>
            <ul>
                <li><a href="/">Home</a></li>
                <li><a href="/about">About</a></li>
            </ul>
        </nav>
    </header>
    <main>
        <article>
            <h1>Main Article Title</h1>
            <p>This is the first paragraph of the article.</p>
            <p>This paragraph contains "double quotes" and 'single quotes'.</p>
            <blockquote>This is a quote from someone important.</blockquote>
        </article>
    </main>
    <aside>
        <h3>Related Links</h3>
        <ul>
            <li><a href="/related1">Related 1</a></li>
        </ul>
    </aside>
    <footer>
        <p>Copyright 2024</p>
        <path d="M0 0 L10 10" />
    </footer>
</body>
</html>
"""

EMPTY_HTML = """
<!DOCTYPE html>
<html>
<head><title>Empty</title></head>
<body></body>
</html>
"""

# Expected text after cleaning COMPLEX_HTML
EXPECTED_CLEANED_TEXT_KEYWORDS = [
    "Main Article Title",
    "first paragraph of the article",
    "double quotes",
    "single quotes",
    "quote from someone important"
]

# Text that should be removed from COMPLEX_HTML
SHOULD_NOT_APPEAR = [
    "console.log",
    "font-family",
    "Home",  # from nav
    "About",  # from nav
    "Related Links",  # from aside
    "Copyright 2024",  # from footer
]


# Knowledge base mock data
MOCK_KNOWLEDGE_BASE = {
    "https://www.infinitepay.io/products": "InfinitePay offers a variety of payment solutions including card machines, mobile payments, and online checkout.",
    "https://www.infinitepay.io/pricing": "Our pricing is transparent with no monthly fees. We charge only a small percentage per transaction.",
    "https://www.infinitepay.io/support": "Contact our support team 24/7 via chat, email, or phone. We're here to help with any questions."
}

MOCK_KNOWLEDGE_BASE_JSON = '''{
    "https://www.infinitepay.io/products": "InfinitePay offers a variety of payment solutions including card machines, mobile payments, and online checkout.",
    "https://www.infinitepay.io/pricing": "Our pricing is transparent with no monthly fees. We charge only a small percentage per transaction.",
    "https://www.infinitepay.io/support": "Contact our support team 24/7 via chat, email, or phone. We're here to help with any questions."
}'''


# Mock embeddings for semantic search tests
def create_mock_embeddings():
    """Create reproducible mock embeddings for testing."""
    np.random.seed(42)
    return {
        "https://www.infinitepay.io/products": np.random.rand(768),
        "https://www.infinitepay.io/pricing": np.random.rand(768),
        "https://www.infinitepay.io/support": np.random.rand(768)
    }


# Query embeddings for testing similarity
def create_query_embedding(query_type="products"):
    """Create mock query embeddings that will match specific content."""
    np.random.seed(42)
    if query_type == "products":
        # Similar to products embedding
        return np.random.rand(768)
    elif query_type == "pricing":
        np.random.seed(43)
        return np.random.rand(768)
    else:
        np.random.seed(44)
        return np.random.rand(768)


# Mock API responses
MOCK_EMBEDDING_RESPONSE = {
    "embedding": [0.1] * 768
}

MOCK_TAVILY_SEARCH_RESPONSE = {
    "results": [
        {
            "title": "Test Result",
            "url": "https://example.com",
            "content": "This is a test search result."
        }
    ]
}


# Guardrail test data
PALMEIRAS_LOSS_RESPONSE = "In yesterday's match, Palmeiras lost 2-1 to Corinthians in a dramatic game."
PALMEIRAS_WIN_RESPONSE = "Palmeiras won 3-0 against Santos in an impressive display of football."
NEUTRAL_RESPONSE = "The weather in São Paulo is sunny with temperatures around 25°C."
FUNCTION_CALL_ONLY_RESPONSE = None  # Represents a response with only function calls


# LLM guardrail check responses
GUARDRAIL_YES_RESPONSE = "YES"
GUARDRAIL_NO_RESPONSE = "NO"


# Tool context state samples
SAMPLE_TOOL_STATE = {
    "user_id": "test-user-123",
    "session_id": "session-456",
    "temperature_preference": "Celsius"
}


# Weather tool test data
WEATHER_TEST_CITIES = {
    "newyork": {
        "status": "success",
        "temperature": 25,
        "condition": "Sunny"
    },
    "london": {
        "status": "success",
        "temperature": 15,
        "condition": "Cloudy"
    },
    "tokyo": {
        "status": "success",
        "temperature": 20,
        "condition": "Rainy"
    }
}
