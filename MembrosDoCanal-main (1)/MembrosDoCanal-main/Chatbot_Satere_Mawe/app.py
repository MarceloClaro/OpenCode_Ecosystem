import streamlit as st
from ollama import Client

# =======================
#  CONFIGURAÇÃO VISUAL
# =======================

st.set_page_config(
    page_title="Chatbot Sateré-Mawé",
    page_icon="🟣",
    layout="wide"
)

# CSS para estilização total
st.markdown("""
<style>

    /* Fundo geral */
    body {
        background-color: #0e0e11;
    }

    /* Caixa do input */
    .stTextInput > div > div > input {
        background-color: #1a1a1d;
        color: #ffffff;
        border-radius: 12px;
        border: 1px solid #6a4ff7;
    }

    /* Balões do chat */
    .stChatMessage {
        border-radius: 16px;
        padding: 10px;
    }

    /* Avatar circular */
    .avatar img {
        border-radius: 50%;
    }

</style>
""", unsafe_allow_html=True)

# =========================
#  LOGO E TÍTULO
# =========================

col1, col2 = st.columns([0.2, 1])

with col1:
    st.image("assets/logo_sateremawe.png", width=170)

with col2:
    st.markdown(
        "<h1 style='color:#c59cff;'><br>Botwaré</h1><h1 style='color:#7DF2C9;'> É um chatbot que fala a língua Sateré-Mawé.</h1>",
        unsafe_allow_html=True
    )


# =========================
#  Cliente Ollama
# =========================

client = Client(host='http://localhost:11434')

# =========================
#  Estado da conversa
# =========================

if "messages" not in st.session_state:
    st.session_state.messages = []


# =========================
#  Exibir histórico com AVATARES
# =========================

for msg in st.session_state.messages:
    if msg["role"] == "user":
        avatar = "assets/avatar_user.png"
    else:
        avatar = "assets/avatar_bot.png"

    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])


# =========================
#  Input do usuário
# =========================

user_msg = st.chat_input("Digite sua mensagem...")

if user_msg:
    # Exibe mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": user_msg})
    with st.chat_message("user", avatar="assets/avatar_user.png"):
        st.markdown(user_msg)

    # ==============================
    #  🔥 CHAMADA EXATAMENTE IGUAL AO SEU app.py
    # ==============================
    response = client.chat(
        model="satere_q8:latest",
        messages=[{"role": "user", "content": user_msg}]
    )

    bot_msg = response["message"]["content"]

    # Exibe resposta do modelo
    st.session_state.messages.append({"role": "assistant", "content": bot_msg})

    with st.chat_message("assistant", avatar="assets/avatar_bot.png"):
        st.markdown(bot_msg)
    
    



