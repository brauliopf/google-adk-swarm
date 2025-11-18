from fastapi import FastAPI
from contextlib import asynccontextmanager
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from support_agent.agent import root_agent
from api.main import init_api

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize resources
    print("🚀 Starting up Agents Swarm API...")

    # Initialize session service and runner
    app.state.session_service = InMemorySessionService()
    app.state.runner = Runner(
        agent=root_agent,
        app_name="support_agent",
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

app = init_api(lifespan=lifespan)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")