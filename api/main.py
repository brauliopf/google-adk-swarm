from typing import Union
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel, Field
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

from agent.main import weather_agent


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize resources
    print("🚀 Starting up Agents Swarm API...")

    # Initialize session service and runner
    app.state.session_service = InMemorySessionService()
    app.state.runner = Runner(
        agent=weather_agent,
        app_name="agents",
        session_service=app.state.session_service
    )

    print("🟢 Session service and runner initialized")

    yield

    # Shutdown: Clean up resources
    print("🛑 Shutting down Agents Swarm API...")

    # Clean up resources if needed
    app.state.session_service = None
    app.state.runner = None

    print("✓ Cleanup completed")


app = FastAPI(
    title="Agents Swarm API",
    description="FastAPI server for the Agents Swarm project",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modify this in production to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AgentWebhookRequest(BaseModel):
    query: str = Field(..., description="User's query to the agent")
    user_id: str = Field(default="anon", description="User ID")

@app.post("/agent-webhook")
async def call_agent_async(request: AgentWebhookRequest):
    user_query = request.query # pydantic parses the json by default
    user_id = request.user_id
    session_id = f"session_{user_id}"

    # Run agent logic
    print('READY TO RUN THE AGENT LOGIC: ', user_query)

    # Create a proper message Content object
    message = types.Content(role="user", parts=[types.Part(text=user_query)])

    # Ensure session exists before running
    session_service = app.state.session_service
    runner = app.state.runner

    # Try to get an existing session
    session = await session_service.get_session(
        app_name=runner.app_name,
        user_id=user_id,
        session_id=session_id
    )

    # If session doesn't exist, create one
    if not session:
        print(f"Creating new session: {session_id} for user: {user_id}")
        session = await session_service.create_session(
            app_name=runner.app_name,
            user_id=user_id,
            session_id=session_id
        )

    # Run the agent asynchronously and return the final response
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=message
    ):
        if event.is_final_response():
            return {"response": event.content.parts[0].text}

    return {"response": "No final response"}



# ----------- TEST

@app.get("/")
def read_root():
    return {"message": "Welcome to Swarm API", "status": "running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = "Blah"):
    return {"item_id": item_id, "q": q}


if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )