import streamlit as st
import asyncio
import os
import json
from dotenv import load_dotenv

# Seu código de assistente (traga como função)
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient

# Carrega variáveis ambiente (OPENAI_API_KEY)
load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

# Função para enviar mensagens para o assistente
async def conversar_com_assistente(pergunta):
    config = {
        "mcpServers": {
            "http": {
                "url": "http://127.0.0.1:8000/sse"
            }
        }
    }
    client = MCPClient.from_dict(config)
    llm = ChatOpenAI(
        model="gpt-4o",
        api_key=OPENAI_KEY
    )
    agent = MCPAgent(llm=llm, client=client, max_steps=30)
    result = await agent.run(pergunta)
    # Tenta extrair link de pagamento do texto/JSON
    pagamento = None
    if isinstance(result, dict):
        pagamento = result.get("pagamento")
    elif isinstance(result, str):
        # Tenta extrair url no texto (markdown)
        if "stripe.com" in result:
            try:
                link = result.split("https://buy.stripe.com/")[1].split(")")[0]
                pagamento = {"payment_url": "https://buy.stripe.com/" + link}
            except Exception:
                pass
        try:
            result_json = json.loads(result)
            pagamento = result_json.get("pagamento")
        except Exception:
            pass
    return result, pagamento

# Streamlit config
st.set_page_config(page_title="HamburguerIA", page_icon="🍔", layout="centered")

st.title("🍔 HamburguerIA 🤖")
st.caption("Converse com o atendente virtual, peça lanches e pague com cartão de crédito!")

if "mensagens" not in st.session_state:
    st.session_state.mensagens = [
        {"role": "assistant", "content": "Olá! Sou o atendente da HamburguerIA 🍔. Como posso te ajudar hoje?"}
    ]

def exibir_chat():
    for m in st.session_state.mensagens:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

exibir_chat()

# Entrada de usuário via chat
pergunta = st.chat_input("Digite sua mensagem, ex: Quero um cheeseburger e uma coca-cola para fsantos@mail.com")

if pergunta:
    st.session_state.mensagens.append({"role": "user", "content": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)

    with st.spinner("Assistente está digitando..."):
        resposta, pagamento = asyncio.run(conversar_com_assistente(pergunta))
        resposta_final = resposta

        # Se tiver link Stripe, destaca!
        if pagamento and "payment_url" in pagamento:
            resposta_final += f"\n\n💳 [Clique para pagar com cartão]({pagamento['payment_url']})"

        st.session_state.mensagens.append({"role": "assistant", "content": resposta_final})

        with st.chat_message("assistant"):
            st.markdown(resposta_final)

