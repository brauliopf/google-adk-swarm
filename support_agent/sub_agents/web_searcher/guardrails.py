from google.adk.agents.llm_agent import CallbackContext, LlmResponse
from typing import Optional
from google.genai import types
from google import genai

def block_palmeiras_haters(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """
    Inspects the model response for 'Palmeiras lost a game'. If found, blocks the LLM call
    and returns a predefined LlmResponse. Otherwise, returns None to proceed.
    """
    agent_name = callback_context.agent_name # Get the name of the agent whose model call is being intercepted
    print(f"--- Callback: block_palmeiras_haters running for agent: {agent_name} ---")

    # Extract text from the model response parts
    model_response_text = ""
    for part in llm_response.content.parts:
        if hasattr(part, 'text') and part.text:
            model_response_text += part.text

    if not model_response_text:
        # No text content (probably a function_call), let it pass
        print(f"--- Callback: No text in response, allowing to proceed ---")
        return None

    print(f"--- Callback: Inspecting model response: '{model_response_text[:100]}...' ---") # Log first 100 chars

    # --- Guardrail Logic ---
    # Use LLM to check if the message states Palmeiras lost a game
    client = genai.Client()
    check_prompt = f"""Analyze the following message and determine if it states that the Brazilian football team "Palmeiras" lost a game.
Respond with only "YES" if the message states Palmeiras lost, or "NO" otherwise.

Message: {model_response_text}"""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=check_prompt
    )

    result = response.text.strip().upper()
    print(f"--- Callback: LLM check for Palmeiras loss: '{result}' ---")

    if "YES" in result:
            print(f"--- Callback: Detected message about Palmeiras losing. Blocking! ---")
            callback_context.state["guardrail_palmeiras_loss_triggered"] = True

            return LlmResponse(
                content=types.Content(
                    role="model",
                    parts=[types.Part(text="I cannot process this request because it mentions Palmeiras losing a game.")],
                )
            )

    # No blocking condition met, allow the request to proceed
    print(f"--- Callback: No blocking condition met. Allowing LLM call for {agent_name}. ---")
    return None # Returning None signals ADK to continue normally

print("✅ block_keyword_guardrail function defined.")