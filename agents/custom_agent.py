from google.adk.agents import LlmAgent
from google.adk.events import Event
from google.adk.agents.invocation_context import InvocationContext
from typing import AsyncGenerator, ClassVar
from groq import Groq

class GrokLlmAgent(LlmAgent):
    """
    Drop-in replacement for LlmAgent that calls Grok's API instead of Gemini.
    """

    

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        prompt = ctx.session.state.get("prompt") or "Hi! This is Braulio"

        client: ClassVar[Groq] = Groq(api_key='***REMOVED***')

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
        )

        print("\n\n\n##### DEBUG:", chat_completion, "\n\n-------------\n")
