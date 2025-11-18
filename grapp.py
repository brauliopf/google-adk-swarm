import gradio as gr
import requests

API_URL = "http://localhost:8000/api/v1/agent-webhook"

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
        fn=lambda msg, history: chat(msg, history, user_id.value),
        type="messages"
    )

demo.launch()
