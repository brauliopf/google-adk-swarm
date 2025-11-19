# Multi-Agent Swarm System with Google ADK

## Problem Statement

This project is a solution to the **Coding Challenge: Building an Agent Swarm** ([original prompt](https://gist.github.com/yoschihirokaimoto/12a1d85b315c7429fbf9c4caa4670a75)).

### Challenge Requirements

Build a multi-agent system (Agent Swarm) with at least **three distinct types of agents** that collaborate to process user requests:

1. **Router Agent**: Analyzes incoming messages and routes to appropriate specialized agents
2. **Knowledge Agent**: Handles information retrieval using RAG from InfinitePay's website (https://www.infinitepay.io) and general web search
3. **Customer Support Agent**: Provides customer support with at least 2 tools for retrieving user data

**Core Deliverables**:
- HTTP endpoint accepting POST requests with `{"message": "query", "user_id": "id"}`
- Functional RAG pipeline ingesting content from specified URLs
- Docker containerization for easy deployment
- Comprehensive testing and documentation

**Bonus Challenges Implemented**:
- ✅ **Guardrails**: Content filtering using LLM-based callbacks (e.g., `block_palmeiras_haters()`)
- ✅ **Additional Custom Agent**: Web crawler agent for dynamic content extraction

---

## Solution: Multi-Agent Architecture

The solution implements a coordinated swarm of specialized agents built on Google's Agent Development Kit (ADK) framework, powered by Gemini models.

### Architecture Overview

```
User Request → FastAPI Endpoint → Coordinator Agent → Specialized Sub-Agents
                                         ↓
                    ┌────────────────────┼────────────────────┐
                    ↓                    ↓                    ↓
            Web Searcher         Knowledge Agent        Crawler Agent
           (Tavily Search)      (RAG with Vectors)   (Selenium Scraper)
```

---

## Core Components

### 1. Coordinator Agent

**Location**: [support_agent/agent.py](support_agent/agent.py)

The root orchestrator that manages workflow and routes queries to appropriate sub-agents:

- **Model**: Gemini 2.0 Flash
- **Temperature**: 0.2 (deterministic routing)
- **Role**: Analyzes incoming queries and delegates to specialist agents
- **Sub-agents**: web_searcher_agent, knowledgeable_agent, crawler_agent
- **Behavior**: Routes autonomously without asking permission, responds in user's language

### 2. Knowledge Agent (RAG System)

**Location**: [support_agent/sub_agents/knowledgeable/agent.py](support_agent/sub_agents/knowledgeable/agent.py)

Implements semantic search using vector embeddings for knowledge retrieval:

- **Model**: Gemini 2.0 Flash
- **Embedding Model**: Google text-embedding-004 (768 dimensions)
- **Tool**: `query_knowledge_base(query, top_k=2)`
- **Algorithm**:
  1. Loads knowledge base from JSON (cached)
  2. Pre-computes embeddings for all documents (cached)
  3. Generates query embedding
  4. Computes cosine similarity between query and all KB items
  5. Returns top-k results sorted by relevance score

**Knowledge Base Creation**: The mock knowledge base was built using the crawler in [notebooks/build_knowledge_base.ipynb](notebooks/build_knowledge_base.ipynb):

1. **Data Collection**: Crawled 18 URLs from infinitepay.io domain
2. **Content Extraction**: Used Selenium + BeautifulSoup to extract clean text
3. **Processing**: Removed unwanted tags (script, style, nav, footer, aside, header, path)
4. **Storage**: Saved to [data/mock_knowledge_base.json](data/mock_knowledge_base.json)

The notebook demonstrates the complete pipeline from URL list to structured knowledge base.

### 3. Crawler Agent (Web Content Extractor)

**Location**: [support_agent/sub_agents/crawler/agent.py](support_agent/sub_agents/crawler/agent.py)

Web scraping agent using Selenium for dynamic content extraction:

- **Model**: Gemini 2.0 Flash
- **Tools**:
  - `go_to_url(url)`: Navigate browser to URL
  - `get_page_text()`: Extract clean text content
  - `extract_structured_content()`: Analyze page structure

**Chromium Driver Configuration**:

The crawler uses a lazy-loaded WebDriver with special Docker support via the `get_driver()` function:

```python
def get_driver():
    global driver
    if driver is None:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # Docker configuration for Chromium
        options.binary_location = "/usr/bin/chromium"
        driver = webdriver.Chrome(
            service=Service("/usr/bin/chromedriver"),
            options=options
        )
    return driver
```

**Docker Setup** ([Dockerfile](Dockerfile)):
```dockerfile
RUN apt-get install -y chromium chromium-driver
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
```

This configuration ensures Chromium runs in headless mode within the Docker container, with proper paths for both the browser binary and driver executable.

### 4. Web Searcher Agent (Tavily Integration)

**Location**: [support_agent/sub_agents/web_searcher/agent.py](support_agent/sub_agents/web_searcher/agent.py)

Real-time web search using Tavily API via Model Context Protocol (MCP):

- **Model**: Gemini 2.5 Pro
- **Tool**: `tavily_search_tool()` - Creates MCPToolset instances
- **MCP Configuration**:
  - **URL**: `https://mcp.tavily.com/mcp/`
  - **Authentication**: Bearer token from `TAVILY_API_KEY` environment variable
  - Creates fresh instances per call to avoid async context issues

**Features**:
- Search filters: start_date, end_date, country
- Returns specific, factual answers (dates, weather, current events)
- Asks clarifying follow-up questions

---

## API Layer

### FastAPI Implementation

**Main Entry Point**: [main.py](main.py)

- **Host**: 0.0.0.0
- **Port**: 8000
- **Session Management**: InMemorySessionService for user tracking
- **Lifespan Management**: Startup/shutdown context manager
- **Agent Runner**: Orchestrates agent execution with event streaming

**Webhook Endpoint**: [api/routes/agent_router.py](api/routes/agent_router.py)

```
POST /api/v1/agent-webhook
```

**Request**:
```json
{
  "query": "What payment solutions does InfinitePay offer?",
  "user_id": "user123"
}
```

**Response**:
```json
{
  "response": "InfinitePay offers multiple payment solutions including..."
}
```

**Additional Endpoints**:
- `GET /api/v1/` - Welcome message
- `GET /api/v1/health` - Health check

---

## Testing Strategy

### Unit Tests Coverage

The project includes comprehensive unit tests with mocks and fixtures:

#### 1. Crawler Tools Tests
**File**: [tests/unit/test_crawler_tools.py](tests/unit/test_crawler_tools.py)

- 20+ test cases covering:
  - URL navigation and path handling
  - HTML cleanup (removing script, style, nav, footer, aside, header, path tags)
  - Content preservation and quote escaping
  - Output length limits
  - Empty page handling

#### 2. Knowledge Base Tests
**File**: [tests/unit/test_knowledgeable_tools.py](tests/unit/test_knowledgeable_tools.py)

- 30+ test cases covering:
  - Knowledge base loading and caching
  - Embedding generation (768-dimensional vectors)
  - Cosine similarity calculations (identical=1.0, orthogonal=0.0, opposite=-1.0)
  - Semantic search with top_k parameter
  - Edge cases and error handling

#### 3. Web Searcher Tests
**File**: [tests/unit/test_web_searcher_tools.py](tests/unit/test_web_searcher_tools.py)

- 8 test cases covering:
  - MCPToolset instance creation
  - MCP URL verification
  - Bearer token authentication
  - Environment variable API key usage

#### 4. Guardrail Tests
**File**: [tests/unit/test_guardrails.py](tests/unit/test_guardrails.py)

- 14 test cases covering the `block_palmeiras_haters()` guardrail function:
  - Blocking responses mentioning "Palmeiras losing"
  - Allowing responses about wins or neutral content
  - Function call-only responses
  - State flag verification (`guardrail_palmeiras_loss_triggered`)
  - Case-insensitive detection
  - Multipart response handling

**Test Infrastructure**:
- **Fixtures**: [tests/conftest.py](tests/conftest.py) provides mock WebDrivers, knowledge bases, embeddings
- **Mock Data**: [tests/fixtures/mock_data.py](tests/fixtures/mock_data.py) contains sample HTML, responses, test cases

---

## Guardrails Implementation

**Location**: [support_agent/sub_agents/web_searcher/guardrails.py](support_agent/sub_agents/web_searcher/guardrails.py)

The `block_palmeiras_haters()` function demonstrates content filtering using LLM-based callbacks:

- **Type**: After-model callback
- **Model**: Gemini 2.0 Flash
- **Purpose**: Inspects responses and blocks content mentioning "Palmeiras losing a game"
- **Behavior**:
  - Analyzes LLM response text
  - Returns blocking message in Portuguese if triggered
  - Sets state flag for tracking
  - Allows function calls to pass through

This showcases how guardrails can enforce content policies at runtime using AI-powered evaluation.

---

## Deployment

### Docker Compose

**File**: [docker-compose.yml](docker-compose.yml)

Run the entire system with a single command:

```bash
docker-compose up --build
```

**Services**:

1. **API Service** (Port 8000)
   - FastAPI server
   - Chromium + ChromeDriver installed
   - All agent functionality

2. **Gradio UI** (Port 7860)
   - Chat interface ([grapp.py](grapp.py))
   - Connects to API service
   - User ID support

### Environment Variables

Create a `.env` file with:

```bash
GOOGLE_API_KEY=your_google_api_key
TAVILY_API_KEY=your_tavily_api_key
CHROME_BIN=/usr/bin/chromium
CHROMEDRIVER_PATH=/usr/bin/chromedriver
```

---

## Technology Stack

- **Framework**: Google Agent Development Kit (ADK)
- **LLMs**: Gemini 2.0 Flash, Gemini 2.5 Pro
- **Embeddings**: Google text-embedding-004
- **API**: FastAPI + Uvicorn
- **Web Scraping**: Selenium + BeautifulSoup4
- **Search**: Tavily via MCP
- **UI**: Gradio
- **Testing**: Pytest with mocks
- **Containerization**: Docker + Docker Compose

---

## Project Structure

```
swarm-google-adk/
├── api/
│   ├── routes/
│   │   ├── agent_router.py    # Webhook endpoint
│   │   └── default.py         # Health/welcome endpoints
│   └── main.py                # FastAPI app initialization
├── support_agent/
│   ├── agent.py               # Coordinator agent
│   ├── sub_agents/
│   │   ├── knowledgeable/     # RAG agent
│   │   ├── crawler/           # Web scraper agent
│   │   └── web_searcher/      # Tavily search agent
│   └── prompt.py              # Coordinator prompt
├── notebooks/
│   └── build_knowledge_base.ipynb  # KB creation pipeline
├── data/
│   └── mock_knowledge_base.json    # Vector search data
├── tests/
│   ├── unit/                  # Comprehensive unit tests
│   └── conftest.py            # Test fixtures
├── main.py                    # Application entry point
├── grapp.py                   # Gradio chat interface
├── Dockerfile                 # Container definition
├── docker-compose.yml         # Multi-service orchestration
└── requirements.txt           # Python dependencies
```

---

## Usage Examples

### Via API

```bash
curl -X POST http://localhost:8000/api/v1/agent-webhook \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the payment methods available?",
    "user_id": "user123"
  }'
```

### Via Gradio UI

1. Open browser to `http://localhost:7860`
2. Enter user ID (optional)
3. Type your question in the chat interface
4. The coordinator routes to appropriate agent automatically

---

## Key Features

1. **Intelligent Routing**: Coordinator analyzes queries and delegates to specialist agents
2. **Semantic Search**: Vector embeddings enable accurate knowledge retrieval
3. **Real-time Web Search**: Tavily integration for current information
4. **Dynamic Content Extraction**: Selenium-based web crawling with HTML cleanup
5. **Content Guardrails**: LLM-powered content filtering
6. **Session Management**: User tracking across conversations
7. **Async Processing**: Event-streaming agent responses
8. **Docker-First**: Complete containerization with Chromium support
9. **Comprehensive Testing**: Unit tests for all tools and guardrails
10. **Production-Ready**: Health checks, error handling, CORS support

---

## How LLM Tools Were Leveraged

This solution extensively leverages LLM capabilities throughout the development process:

### 1. **Agent Orchestration with Google ADK**
- **Gemini 2.0 Flash** powers the coordinator and specialized agents
- **Gemini 2.5 Pro** handles complex web search queries
- Agents use natural language understanding to route queries intelligently

### 2. **RAG Implementation**
- **Google text-embedding-004** generates 768-dimensional semantic vectors
- Embeddings enable similarity-based knowledge retrieval from InfinitePay content
- LLM combines retrieved context with query to generate accurate responses

### 3. **Guardrails with LLM Callbacks**
- `block_palmeiras_haters()` uses Gemini to analyze response content
- LLM determines if responses violate content policies
- Demonstrates AI-powered content moderation at runtime

### 4. **Prompt Engineering**
- Each agent has carefully crafted system prompts defining scope and behavior
- Prompts ensure agents stay within their responsibilities
- Language detection ensures responses match user's language

### 5. **Tool Usage**
- LLMs decide when to invoke tools (search, crawl, query KB)
- Function calling enables structured interaction with external systems
- Agents autonomously chain tool calls to complete complex tasks

### 6. **Development Assistance**
- Used Claude Code to architect the multi-agent system
- LLM-assisted code generation for boilerplate and tool implementations
- AI-powered test generation for comprehensive coverage

---

## Example Test Scenarios

These are the test scenarios from the coding challenge:

### Knowledge Base Queries (InfinitePay Products)

```bash
curl -X POST http://localhost:8000/api/v1/agent-webhook \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the fees of the Maquininha Smart", "user_id": "client789"}'

curl -X POST http://localhost:8000/api/v1/agent-webhook \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the cost of the Maquininha Smart?", "user_id": "client789"}'

curl -X POST http://localhost:8000/api/v1/agent-webhook \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the rates for debit and credit card transactions?", "user_id": "client789"}'

curl -X POST http://localhost:8000/api/v1/agent-webhook \
  -H "Content-Type: application/json" \
  -d '{"message": "How can I use my phone as a card machine?", "user_id": "client789"}'
```

### Web Search Queries (Current Information)

```bash
curl -X POST http://localhost:8000/api/v1/agent-webhook \
  -H "Content-Type: application/json" \
  -d '{"message": "Quando foi o último jogo do Palmeiras?", "user_id": "client789"}'

curl -X POST http://localhost:8000/api/v1/agent-webhook \
  -H "Content-Type: application/json" \
  -d '{"message": "Quais as principais notícias de São Paulo hoje?", "user_id": "client789"}'
```

### Customer Support Queries

```bash
curl -X POST http://localhost:8000/api/v1/agent-webhook \
  -H "Content-Type: application/json" \
  -d '{"message": "Why I am not able to make transfers?", "user_id": "client789"}'

curl -X POST http://localhost:8000/api/v1/agent-webhook \
  -H "Content-Type: application/json" \
  -d '{"message": "I can'\''t sign in to my account.", "user_id": "client789"}'
```

**Expected Behavior**:
- Product queries → Knowledge Agent (RAG from InfinitePay website)
- Current events → Web Searcher Agent (Tavily search)
- Support issues → Crawler Agent (investigates user data/issues)
- Portuguese queries receive Portuguese responses (language detection)

---

## Development

### Running Tests

```bash
pytest tests/unit -v
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run API server
python main.py

# Run Gradio UI (in separate terminal)
python grapp.py
```

---

## License

This project demonstrates a production-grade multi-agent system architecture using Google's Agent Development Kit.
