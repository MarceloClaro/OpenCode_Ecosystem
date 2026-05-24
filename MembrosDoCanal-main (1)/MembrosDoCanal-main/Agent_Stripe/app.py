import os
from dotenv import load_dotenv
from langchain import hub
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from stripe_agent_toolkit.langchain.toolkit import StripeAgentToolkit
from langchain_groq import ChatGroq

load_dotenv()

llm=ChatGroq(temperature=0,
             model_name="llama-3.1-8b-instant",
             api_key='GROQ_API_KEY')


stripe_agent_toolkit = StripeAgentToolkit(
    secret_key=os.getenv("STRIPE_SECRET_KEY"),
    configuration={
        "actions": {
            "payment_links": {
                "create": True,
            },
            "products": {
                "create": True,
            },
            "prices": {
                "create": True,
            },
        }
    },
)

tools = []
tools.extend(stripe_agent_toolkit.get_tools())

langgraph_agent_executor = create_react_agent(llm, tools)

input_state = {
    "messages": """
        Create a payment link for a new product called 'teste' with a price
        of $300. Come up with a funny description about buy bots,
        maybe a haiku.
    """,
}

output_state = langgraph_agent_executor.invoke(input_state)

print(output_state["messages"][-1].content)