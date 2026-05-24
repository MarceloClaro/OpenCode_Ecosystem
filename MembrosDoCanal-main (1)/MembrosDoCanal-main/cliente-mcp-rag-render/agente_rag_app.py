import streamlit as st
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import AIMessage
from langchain_groq import ChatGroq
import os

#os.environ["GROQ_API_KEY"] = ""  # Substitua pela sua chave

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"  # ou "llama3-70b-8192"

model = ChatGroq(
    model=GROQ_MODEL,
    temperature=0.0,   
    # other params...
)

async def get_tools_and_check_connection():
    try:
        async with MultiServerMCPClient({
            "weather": {
                "url": "https://mcp-server-rag-groq.onrender.com/sse",
                "transport": "sse",
            }
        }) as client:
            tools = client.get_tools()
            return True, tools
    except Exception as e:
        return False, str(e)

async def run_agent(user_query):
    async with MultiServerMCPClient({
        "weather": {
            "url": "https://mcp-server-rag-groq.onrender.com/sse",
            "transport": "sse",
        }
    }) as client:
        tools = client.get_tools()
        agent = create_react_agent(model, tools)
        result = await agent.ainvoke({"messages": user_query})
        messages = result["messages"]
        for message in messages[::-1]:
            if isinstance(message, AIMessage) and message.content:
                return message.content
        return "Resposta não encontrada."

# Frontend
st.set_page_config(page_title="Agente MCP", page_icon="🧠")
st.title("🧠 Agente MCP-RAG")

# Conexão e ferramentas
with st.spinner("Conectando ao servidor MCP..."):
    connected, result = asyncio.run(get_tools_and_check_connection())

if connected:
    st.success("✅ Conectado ao servidor MCP!")
    st.subheader("🧰 Ferramentas disponíveis:")
    for tool in result:
        st.markdown(f"- **{tool.name}**: {tool.description}")
else:
    st.error("❌ Falha na conexão com o servidor MCP:")
    st.code(result)
    st.stop()

# Entrada do usuário
st.divider()
user_query = st.text_input("💬 Digite sua solicitação:")

if st.button("Enviar solicitação"):
    if user_query.strip():
        with st.spinner("Consultando o servidor MCP..."):
            response = asyncio.run(run_agent(user_query))
            st.success("🧠 Resposta do servidor MCP:")
            st.markdown(response)
    else:
        st.warning("Por favor, digite uma solicitação.")

