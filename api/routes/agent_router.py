from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from google.genai import types

# Create router instance
router = APIRouter(prefix="/api/v1", tags=["Agent"])

class AgentWebhookRequest(BaseModel):
    query: str = Field(..., description="User's query to the agent")
    user_id: str = Field(default="anon", description="User ID")

def get_session_service(request: Request):
    return request.app.state.session_service


def get_runner(request: Request):
    return request.app.state.runner


@router.post("/agent-webhook")
async def call_agent_async(
    webhook_request: AgentWebhookRequest,
    session_service=Depends(get_session_service),
    runner=Depends(get_runner),
):
    user_query = webhook_request.query  # pydantic parses the json by default
    user_id = webhook_request.user_id
    session_id = f"session_{user_id}"

    # Run agent logic
    print('READY TO RUN THE AGENT LOGIC: ', user_query)

    # Create a proper message Content object
    message = types.Content(role="user", parts=[types.Part(text=user_query)])

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