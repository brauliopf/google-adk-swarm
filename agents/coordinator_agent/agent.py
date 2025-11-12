from google.adk.agents import LlmAgent
from google.adk.tools import google_search


knowledge_agent = LlmAgent(
    name="Knowledge",
    model="gemini-2.0-flash",
    description="Uses RAG on the company's website or general web search to answer questions.",
    instruction="""Respond to the query using google search""",
    tools=[google_search])
support_agent = LlmAgent(name="Support", description="Addresses user requests based on data retrieved from the application DB.")

root_agent = LlmAgent(
    name="Coordinator",
    model="gemini-2.0-flash",
    instruction='Route user requests: Use "Knowledge agent" for general questions, "Support agent" for questions related to the user\'s data in the application.',
    description="Main coordinator agent.",
    sub_agents=[knowledge_agent, support_agent]
)
# "What is the cost of the Maquininha Smart?" -> Coordinator's LLM should call knowledge_agent
# "Quando foi o último jogo do Palmeiras?" -> Coordinator's LLM should call knowledge_agent
# "How much did I make on the last week of last month?" -> Coordinator's LLM should call support_agent