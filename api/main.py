from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(
    title="Agents Swarm API",
    description="FastAPI server for the Agents Swarm project",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modify this in production to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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