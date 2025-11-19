import gradio as gr
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1/agent-webhook")

def chat(message, history, user_id):
    try:
        response = requests.post(
            API_URL,
            json={"query": message, "user_id": user_id or "anon"}
        )
        response.raise_for_status()
        return response.json().get("response", "No response")
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"

with gr.Blocks(title="Agent Chat") as demo:
    gr.Markdown("# Agent Chat Interface")

    user_id = gr.Textbox(label="User ID", value="anon", placeholder="Enter your user ID")
    chatbot = gr.ChatInterface(
        fn=chat,
        type="messages",
        additional_inputs=[user_id]
    )

# https://www.gradio.app/guides/quickstart
demo.launch(
    server_name=os.getenv("GRADIO_SERVER_NAME", "127.0.0.1"),
    server_port=int(os.getenv("GRADIO_SERVER_PORT", "7860")),
    # share=True
)
