from typing import Optional, Callable
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.agent_router import router as agent_router
from api.routes.default import router as default_router


def init_api(lifespan: Optional[Callable] = None) -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Args:
        lifespan: Optional lifespan context manager for startup/shutdown events
        
    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title="Agents Swarm API",
        description="FastAPI server for the Agents Swarm project",
        version="0.1.0",
        lifespan=lifespan
    )
    
    # Include all route modules
    app.include_router(agent_router)
    app.include_router(default_router)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Modify this in production to specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app