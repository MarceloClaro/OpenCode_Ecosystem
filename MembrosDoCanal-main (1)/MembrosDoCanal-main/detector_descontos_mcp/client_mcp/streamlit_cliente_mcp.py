import asyncio
import fitz  # PyMuPDF
import streamlit as st
from dotenv import load_dotenv
import os

from mcp_use import MCPClient, MCPAgent
from langchain_openai import ChatOpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="Análise de Descontos", layout="centered")
st.title("💰 Avaliador de Extrato Bancário (via MCP)")

uploaded_file = st.file_uploader("Envie um extrato bancário em PDF", type=["pdf"])

if uploaded_file:
    st.success("📄 PDF carregado com sucesso!")
    if st.button("🔍 Analisar Descontos"):

        async def analisar_extrato():
            # Salva PDF temporariamente
            temp_path = "/tmp/extrato.pdf"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.read())

            # Extrai texto via OCR (PyMuPDF)
            texto = ""
            with fitz.open(temp_path) as doc:
                for page in doc:
                    texto += page.get_text()

            comando = f"Avalie os descontos do seguinte extrato bancário:\n\n{texto}"

            # Inicializa cliente e agente
            config = {
                "mcpServers": {
                    "http": {
                        "url": "http://localhost:8000/mcp"
                    }
                }
            }

            client = MCPClient.from_dict(config)
            llm = ChatOpenAI(model="gpt-4o", api_key=OPENAI_API_KEY)

            agent = MCPAgent(
                llm=llm,
                client=client,
                max_steps=30
            )

            result = await agent.run(comando)
            return result

        with st.spinner("Analisando..."):
            resultado = asyncio.run(analisar_extrato())
            st.subheader("✅ Resultado Final:")
            st.write(resultado)
