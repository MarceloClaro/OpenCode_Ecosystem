import asyncio
import streamlit as st
import dotenv
from llama_index.llms.openai import OpenAI
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from llama_index.core.agent.workflow import FunctionAgent, ToolCallResult, ToolCall
from llama_index.core.workflow import Context
from dotenv import load_dotenv
import os
import datetime
import threading
import time
import base64
import nest_asyncio

# Permite rodar asyncio.run mesmo se já houver um event loop (ex: no Streamlit)
nest_asyncio.apply()

# Função para codificar imagem em base64 para exibição no Streamlit

def encode_image(path):
    with open(path, "rb") as image_file:
        return "data:image/png;base64," + base64.b64encode(image_file.read()).decode()

user_avatar = encode_image("garoto.png")
bot_avatar = encode_image("chatbot.png")

# Carregar variáveis de ambiente
dotenv.load_dotenv()
api_key = os.getenv("OPEN_AI_API_KEY")
llm = OpenAI(model="gpt-4o", api_key=api_key)


#api_key = os.getenv("GOOGLE_API_KEY")

#llm = GoogleGenAI(
#    model="gemini-2.0-flash",
#    api_key=api_key # uses GOOGLE_API_KEY env var by default
#)

SYSTEM_PROMPT = """
You are LegalAgent AI, an advanced AI assistant specialized in Legal Database Management.

You have access to comprehensive tools that enable you to:
- Intelligently manage cases, clients, and legal professionals
- Perform sophisticated searches through legal case databases
- Create and organize new legal records with precision
- Retrieve specific information using various identifiers
- Analyze relationships and patterns between cases, clients, and lawyers
- Provide legal insights and recommendations based on data

Always maintain a professional, knowledgeable tone while being helpful and efficient.
Structure your responses clearly and provide actionable insights when possible.
"""

# Variáveis globais para agente e contexto
agent = None
agent_context = None
mcp_client = None

def get_example_queries():
    return {
    "📊 Visão Geral dos Dados": [
        "Mostre todos os casos no banco de dados",
        "Obter a lista completa de clientes",
        "Listar todos os advogados disponíveis e suas especializações"
    ],
    "➕ Adição de Registros": [
        "Adicionar novo cliente: João Silva, email: joao.silva@email.com, telefone: +55-11-5550-0123",
        "Criar perfil de advogado: Sarah Smith, especializada em Defesa Criminal",
        "Registrar novo caso: 'Disputa de Fusão Corporativa' para o cliente ID 1 com o advogado ID 2"
    ],
    "🔍 Busca & Análise": [
        "Encontrar todos os casos relacionados a contratos",
        "Mostrar casos tratados pelo advogado ID 1",
        "Buscar clientes com litígios pendentes",
        "Analisar os resultados dos casos por especialização do advogado"
    ],
    "📈 Informações Relevantes": [
        "Quais são os tipos de caso mais comuns?",
        "Quais advogados têm a maior carga de casos?",
        "Mostrar relação entre o cliente ID 1 e seus casos"
    ]
}


async def initialize_agent():
    try:
        # Apenas testa a conexão e ferramentas, não salva agent/contexto
        mcp_client = BasicMCPClient("http://127.0.0.1:3000/sse")
        mcp_tool = McpToolSpec(client=mcp_client)
        tools_list = await mcp_tool.to_tool_list_async()
        return True, f"🎯 LegalAgent AI activated successfully! Connected with {len(tools_list)} specialized tools."
    except Exception as e:
        return False, f"⚠️ Connection failed: {str(e)}"

async def handle_user_message(message_content: str):
    # Sempre cria o agent/contexto no mesmo event loop
    mcp_client = BasicMCPClient("http://127.0.0.1:3000/sse")
    mcp_tool = McpToolSpec(client=mcp_client)
    tools_list = await mcp_tool.to_tool_list_async()

    agent = FunctionAgent(
        name="LegalAgentAI",
        description="An advanced AI agent specialized in legal database management and analysis.",
        tools=tools_list,
        llm=llm,
        system_prompt=SYSTEM_PROMPT,
    )
    agent_context = Context(agent)
    try:
        tool_operations = []
        handler = agent.run(message_content, ctx=agent_context)
        async for event in handler.stream_events():
            if type(event) == ToolCall:
                tool_operations.append(f"⚡ Executing: `{event.tool_name}`")
            elif type(event) == ToolCallResult:
                tool_operations.append(f"✓ Completed: `{event.tool_name}`")
        response = await handler
        if tool_operations:
            operations_text = "\n".join(tool_operations)
            return f"""**🔧 System Operations:**\n```
{operations_text}
```
**💡 LegalAgent AI Response:**
{str(response)}"""
        else:
            return f"**💡 LegalAgent AI Response:**\n{str(response)}"
    except Exception as e:
        return f"""❌ **Error Processing Request:**\n```
{str(e)}
```"""

def main():
    st.set_page_config(
        page_title="LegalAgent AI - Advanced Legal Database Assistant",
        page_icon="⚖️",
        layout="wide"
    )
    st.markdown("""
        <style>
        .stChatMessage.user {background: #f0fdf4;}
        .stChatMessage.assistant {background: #f3e8ff;}
        .avatar-img {width: 40px; height: 40px; border-radius: 50%;}
        </style>
    """, unsafe_allow_html=True)

    st.title("⚖️ LegalAgent AI")
    st.caption("Advanced Legal Database Management & Intelligence System")

    # Sidebar com exemplos e status
    with st.sidebar:
        st.header("💡 Exemplos de Comandos")
        examples = get_example_queries()
        for category, queries in examples.items():
            st.markdown(f"**{category}**")
            for q in queries:
                if st.button(q, key=f"ex_{q}"):
                    st.session_state["input_message"] = q
        st.divider()
        st.header("📊 Status do Sistema")
        st.markdown(f"- **AI Model:** Gemini 2.5 Flash\n- **MCP Server:** localhost:3000\n- **Interface:** v2.0.0\n- **Last Updated:** {datetime.datetime.now().strftime('%H:%M')}")

    # Estado da sessão para histórico e conexão
    if "history" not in st.session_state:
        st.session_state["history"] = []
    if "connected" not in st.session_state:
        st.session_state["connected"] = False
    if "status_msg" not in st.session_state:
        st.session_state["status_msg"] = "🔴 Disconnected - Ready to connect to legal database"
    if "input_message" not in st.session_state:
        st.session_state["input_message"] = ""

    # Painel de conexão
    with st.container():
        st.subheader("🔌 Conexão com Banco de Dados")
        col1, col2 = st.columns([4,1])
        with col1:
            st.info(st.session_state["status_msg"])
        with col2:
            if not st.session_state["connected"]:
                if st.button("🔗 Connectar ao Banco de dados", key="connect_btn"):
                    with st.spinner("Connecting..."):
                        success, msg = asyncio.run(initialize_agent())
                        st.session_state["connected"] = success
                        st.session_state["status_msg"] = msg
                        st.rerun()  # Força a atualização imediata
            else:
                if st.button("🔄 Reconnect", key="reconnect_btn"):
                    with st.spinner("Reconnecting..."):
                        success, msg = asyncio.run(initialize_agent())
                        st.session_state["connected"] = success
                        st.session_state["status_msg"] = msg

    st.divider()

    # Chatbot
    st.subheader("🤖 Assistente LegalAgent AI")
    chat_container = st.container()
    with chat_container:
        for i, (user, bot) in enumerate(st.session_state["history"]):
            cols = st.columns([1, 10])
            with cols[0]:
                st.image(user_avatar, width=40)
            with cols[1]:
                st.markdown(f"**You:** {user}")
            if bot:
                cols = st.columns([1, 10])
                with cols[0]:
                    st.image(bot_avatar, width=40)
                with cols[1]:
                    st.markdown(bot, unsafe_allow_html=True)

    # Input de mensagem
    if st.session_state["connected"]:
        input_message = st.text_input(
            "Type your message:",
            value=st.session_state.get("input_message", ""),
            key="input_box"
        )
        st.session_state["input_message"] = ""
        if st.button("📤 Send", key="send_btn") or input_message:
            if input_message.strip():
                st.session_state["history"].append([input_message, None])
                with st.spinner("LegalAgent AI está pensando..."):
                    response = asyncio.run(handle_user_message(input_message))
                st.session_state["history"][-1][1] = response
                st.rerun()
    else:
        st.text_input(
            "Digite sua mensagem:",
            value="",
            key="input_box",
            disabled=True,
            placeholder="Connect to database first..."
        )
        st.button("📤 Send", key="send_btn_disabled", disabled=True)

    st.markdown("""
    ---
    <div style='text-align: center; color: #888; font-size: 0.9rem;'>
        ⚖️ LegalAgent AI • Powered by Gemini 2.5 & MCP Protocol<br>
        Advanced Legal Database Intelligence • Secure • Professional • Efficient
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 