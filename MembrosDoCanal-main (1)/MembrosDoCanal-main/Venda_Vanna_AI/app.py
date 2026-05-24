import time
import streamlit as st
from vanna_calls import (
    generate_sql_cached,
    run_sql_cached,
    generate_plotly_code_cached,
    generate_plot_cached,
    should_generate_chart_cached       
)

avatar_url = "🤖"
st.set_page_config(layout="wide")

# ====== THEME / SKIN ======
st.markdown("""
<style>
html, body { font-family: "Segoe UI", system-ui, -apple-system, sans-serif; }
:root {
  --brand-blue: #0a019e;
  --brand-blue-light: #3b82f6;
  --text-dark: #0f172a;
  --chip-bg: #eef2ff;
}
.block-container { max-width: 980px; margin: 0 auto; }
h1, h2, h3 { color: var(--brand-blue) !important; font-weight: 800; }
[data-testid="stSidebar"]{
  background: var(--brand-blue) !important;
  color: #fff !important;
  min-height: 100vh !important;
  height: 100% !important;
  padding-top: 20px !important;
}
[data-testid="stSidebar"] * { color:#fff !important; }
.sidebar-card{
  background:#ffffff;
  border-radius: 14px;
  padding: 18px 16px;
  color: var(--text-dark) !important;
}
.sidebar-card h4{ margin:0 0 10px 0; color: var(--text-dark) !important; font-weight:700; }
.sidebar-card small{ color:#334155 !important; }
[data-testid="stSidebar"] .stButton>button{
  width:100%;
  background:#2b59ff !important;
  border:none !important; color:#fff !important;
  border-radius:10px !important; padding:10px 14px !important;
}
[data-testid="stSidebar"] .stButton>button:hover{ filter:brightness(0.95); }
[data-testid="stSidebar"] .stCheckbox>label{ display:flex; gap:.5rem; align-items:center; font-weight:500; }
header, [data-testid="stHeader"]{ background:#fff !important; }
footer[data-testid="stChatInput"]{ background: var(--brand-blue) !important; }

/* Campo de input: azul do sidebar */
[data-testid="stChatInput"] textarea{
  background: var(--brand-blue) !important;
  color: #ffffff !important;
  border-radius: 999px !important;
  padding: 14px 18px !important;
  border: 2px solid #ffffff22 !important;
}
[data-testid="stChatInput"] textarea::placeholder{
  color: #e5e7eb !important;
  opacity: 0.95 !important;
}

/* Botão enviar */
button[data-testid="stChatInputSubmitButton"]{
  background: #ffffff !important;
  color: var(--brand-blue) !important;
  border-radius: 999px !important;
  border: none !important;
  box-shadow: none !important;
}
button[data-testid="stChatInputSubmitButton"]:hover{
  filter: brightness(0.95);
}

.suggestion-wrap{
  background:#f3f4f6; border-radius:14px; padding:12px 16px; border:1px solid #eef2ff;
}
.stButton>button{
  background: var(--brand-blue-light) !important;
  color:#fff !important; border:none !important;
  border-radius: 10px !important; padding:10px 14px !important;
  font-weight:600 !important;
}
.stButton>button:hover{ background:#2563eb !important; }
.stChatMessage>div{
  background:#f8fafc !important; color: var(--text-dark) !important;
  border-radius: 12px; padding: 14px; margin-bottom: 8px;
  box-shadow: none !important; border:1px solid #e5e7eb;
}
.stChatMessage:nth-child(even)>div{ background:#ffffff !important; }
.hero-sub{ color:#334155; font-weight:500; font-size:0.95rem; text-align:center; }
 /* Troca fundo roxo do st.code por azul */
.stCode, pre, code {
    background-color: #0a019e !important;   /* azul escuro do sidebar */
    color: #ffffff !important;              /* texto branco */
    border-radius: 8px !important;
    padding: 12px !important;
    font-size: 0.9rem !important;
}

/* Mantém numeração da linha legível */
.stCode .stHighlight, .stCode pre {
    background-color: transparent !important;
    color: #ffffff !important;
}

/* Força cabeçalho da tabela para azul */
[data-testid="stDataFrame"] div[role="columnheader"] {
    background-color: #010a43 !important;  /* azul escuro personalizado */
    color: #ffffff !important;
    font-weight: 600 !important;
    text-align: center !important;
    border: none !important;
}

/* Bordas mais clean */
[data-testid="stDataFrame"] div[role="gridcell"] {
    border: none !important;
    color: #111827 !important;
}

/* Alternância de linhas */
[data-testid="stDataFrame"] div[role="row"]:nth-child(even) {
    background-color: #f9fafb !important;
}
[data-testid="stDataFrame"] div[role="row"]:nth-child(odd) {
    background-color: #ffffff !important;
}

</style>
""", unsafe_allow_html=True)

# ====== SIDEBAR ======
with st.sidebar:
    try:
        st.image("logo.png", use_container_width=True)
    except Exception:
        st.markdown("<div style='font-size:58px; line-height:0.9; font-weight:900;'>z<span style='letter-spacing:-2px'>i</span>lla<br><span style='font-size:14px; font-weight:700;'>IA</span></div>", unsafe_allow_html=True)
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

        
    st.markdown("<h4>Configurar Resposta</h4>", unsafe_allow_html=True)
    st.checkbox("Mostrar Tabela", value=True, key="show_table")   
    st.checkbox("Mostrar Gráfico", value=True, key="show_chart")   
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    st.button("Reset", on_click=lambda: set_question(None), use_container_width=True)

# ====== HERO ======
st.markdown("<h1 style='text-align:center;'>🤖 Assistente Inteligente</h1>", unsafe_allow_html=True)
st.markdown("<p class='hero-sub'>Essa IA responde a consultas sobre as vendas.</p>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align:center; margin-top:8px;'>Como posso ajudar você hoje?</h2>", unsafe_allow_html=True)


# Função para armazenar a pergunta
def set_question(question):
    st.session_state["my_question"] = question


# Processamento principal da pergunta
def process_question(question):
    st.chat_message("user").write(question)

    sql = generate_sql_cached(question=question)
    if not sql:
        st.chat_message("assistant", avatar=avatar_url).error("I wasn't able to generate SQL for that question")
        return
    
    df = run_sql_cached(sql=sql)
    if df is None:
        st.chat_message("assistant", avatar=avatar_url).error("No data returned from SQL")
        return

    st.session_state["df"] = df

    # Mostrar tabela
    if st.session_state.get("show_table", True):
        chat = st.chat_message("assistant", avatar=avatar_url)
        chat.text("First 10 rows of data" if len(df) > 10 else "")
        chat.dataframe(df.head(10) if len(df) > 10 else df)

    # Mostrar gráfico
    if should_generate_chart_cached(question=question, sql=sql, df=df):
        code = generate_plotly_code_cached(question=question, sql=sql, df=df)        

        if code and st.session_state.get("show_chart", True):
            fig = generate_plot_cached(code=code, df=df)
            chart_message = st.chat_message("assistant", avatar=avatar_url)
            if fig is not None:
                chart_message.plotly_chart(fig)
            else:
                chart_message.error("I couldn't generate a chart")


# Entrada do usuário
my_question = st.session_state.get("my_question")
if my_question is None:
    my_question = st.chat_input("Digite sua consulta", key="chat_input")

if my_question:
    st.session_state["my_question"] = my_question
    
    try:
        process_question(my_question)
    except Exception as e:
        st.error(f"Não foi possível processar esse tipo de consulta tente refazer sua consulta.")
    
    st.session_state["my_question"] = None
    