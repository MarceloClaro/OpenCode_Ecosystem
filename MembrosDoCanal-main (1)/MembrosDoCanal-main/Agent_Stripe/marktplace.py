import streamlit as st
from langgraph.prebuilt import create_react_agent
from stripe_agent_toolkit.langchain.toolkit import StripeAgentToolkit
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

# Configuração inicial
load_dotenv()

def initialize_agent():
    llm = ChatGroq(temperature=0.5,
                   model_name="llama-3.1-8b-instant",
                   api_key=os.getenv('GROQ_API_KEY'))

    stripe_agent_toolkit = StripeAgentToolkit(
        secret_key=os.getenv("STRIPE_SECRET_KEY"),
        configuration={
            "actions": {
                "payment_links": {"create": True},
                "products": {"create": True},
                "prices": {"create": True},
            },
        },
    )

    tools = stripe_agent_toolkit.get_tools()
    agent = create_react_agent(llm, tools)
    return agent

# Inicializar agente
agent = initialize_agent()

# Simulação de produtos
products = [
    {"name": "Produto 1", "price": 50},
    {"name": "Produto 2", "price": 100},
    {"name": "Produto 3", "price": 150},
]

st.title("Marketplace")
st.write("Escolha um produto e clique em 'Comprar' para gerar um link de pagamento.")

for product in products:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"**{product['name']}** - R$ {product['price']}")
    with col2:
        if st.button(f"Comprar {product['name']}"):
            input_state = {
                "messages": f"Create a payment link for a new product called '{product['name']}' with a price of ${product['price']}."
            }
            with st.spinner("Gerando link de pagamento..."):
                try:
                    output_state = agent.invoke(input_state)
                    payment_link = output_state["messages"][-1].content
                    st.success("Link de pagamento gerado!")
                    st.write(payment_link)
                except Exception as e:
                    st.error("Erro ao gerar link de pagamento: " + str(e))
