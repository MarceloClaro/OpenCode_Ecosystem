import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Análise de Sentimento",
    page_icon="🧠",
    layout="centered",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0d1117;
    color: #e6edf3;
}

.stTextArea textarea {
    background-color: #161b22 !important;
    color: #e6edf3 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 15px !important;
}

.stButton > button {
    background-color: #238636 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 14px !important;
    padding: 0.5rem 2rem !important;
    width: 100%;
    transition: background 0.2s;
}

.stButton > button:hover {
    background-color: #2ea043 !important;
}

.result-box {
    margin-top: 1.5rem;
    padding: 1.5rem 2rem;
    border-radius: 10px;
    text-align: center;
    font-family: 'Space Mono', monospace;
    font-size: 1.3rem;
    font-weight: 700;
    letter-spacing: 0.05em;
}

.positivo {
    background-color: #0d2b1a;
    border: 1px solid #2ea043;
    color: #3fb950;
}

.negativo {
    background-color: #2d0f0f;
    border: 1px solid #da3633;
    color: #f85149;
}

.error-box {
    background-color: #1c1a12;
    border: 1px solid #d29922;
    color: #e3b341;
    padding: 1rem 1.5rem;
    border-radius: 8px;
    font-size: 0.9rem;
    margin-top: 1rem;
}

h1 {
    font-family: 'Space Mono', monospace !important;
    font-size: 1.8rem !important;
    color: #e6edf3 !important;
}

.subtitle {
    color: #8b949e;
    font-size: 0.95rem;
    margin-bottom: 2rem;
}

.api-badge {
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    color: #8b949e;
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 4px;
    padding: 2px 8px;
    display: inline-block;
    margin-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("# 🧠 Análise de Sentimento")
st.markdown('<p class="subtitle">Digite ou cole uma mensagem para descobrir se o sentimento é positivo ou negativo.</p>', unsafe_allow_html=True)
st.markdown(f'<span class="api-badge">API → {API_URL}/predict</span>', unsafe_allow_html=True)

texto = st.text_area("Mensagem", placeholder="Ex: adorei esse produto!", height=140, label_visibility="collapsed")

if st.button("Analisar sentimento"):
    if not texto.strip():
        st.warning("Digite alguma mensagem antes de analisar.")
    else:
        try:
            response = requests.post(
                f"{API_URL}/predict",
                json={"texto": texto},
                timeout=5,
            )
            response.raise_for_status()
            resultado = response.json().get("sentimento", "")

            emoji = "😊" if resultado == "positivo" else "😞"
            css_class = "positivo" if resultado == "positivo" else "negativo"
            st.markdown(
                f'<div class="result-box {css_class}">{emoji} {resultado.upper()}</div>',
                unsafe_allow_html=True,
            )
        except requests.exceptions.ConnectionError:
            st.markdown(
                f'<div class="error-box">⚠️ Não foi possível conectar à API.<br>Verifique se o contêiner <code>sentiment-api</code> está rodando e acessível em <code>{API_URL}</code>.</div>',
                unsafe_allow_html=True,
            )
        except requests.exceptions.Timeout:
            st.markdown(
                '<div class="error-box">⚠️ A API demorou demais para responder (timeout).</div>',
                unsafe_allow_html=True,
            )
        except Exception as e:
            st.markdown(
                f'<div class="error-box">⚠️ Erro inesperado: {e}</div>',
                unsafe_allow_html=True,
            )
