# Application

* This is a multi-agent system (Agent Swarm) where agents collaborate to process user requests and generate responses.
* The "Swarm" has three distinct types of agents working together to process user messages.
 * Router Agent: manages the workflow and data flow between other agents.
 * Knowledge Agent: uses RAG on the company's website or general web search to answer questions.
 * Customer Support Agent: provides support based on data retrieved from the application DB. Use 2 tools: retrieve customer data (mock SQL DB), send email.

* Expose the swarm using a FastAPI.
 * Use a query webhook that takes a POST with message and a user_id and returns a structured output in JSON format.
  * The user_id is passed as a header parameter, for additional security

* Build and run application (FastAPI and Agent) with a single Docker command.