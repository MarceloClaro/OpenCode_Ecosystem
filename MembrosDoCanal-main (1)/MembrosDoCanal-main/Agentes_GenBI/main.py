# main.py
import os
import re
import traceback
from typing import Any

import pandas as pd
import streamlit as st
from langchain_ollama import ChatOllama
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain.prompts import ChatPromptTemplate

# ---------------------- UI base ----------------------
st.set_page_config(page_title="Agentes – Streaming", page_icon="🤖", layout="centered")
st.title("🤖 Agentes business intelligence")

st.sidebar.header("Configuração do LLM / Banco")
OLLAMA_URL = st.sidebar.text_input("Ollama Base URL", os.getenv("OLLAMA_URL", "http://localhost:11434"))
MODEL_NAME = st.sidebar.text_input("Modelo Ollama", os.getenv("OLLAMA_MODEL", "llama3.1:8b"))
DB_PATH = st.sidebar.text_input("Arquivo SQLite", os.getenv("DB_PATH", "empresa.db"))
st.sidebar.caption("Dica: rode `ollama serve` e tenha o modelo baixado.")

# ---------------------- Estilo de bolhas ----------------------
BUBBLE_CSS = """
<style>
.bubble{ margin:.5rem 0; padding:.85rem 1rem; border-radius:12px; line-height:1.45;
         border:1px solid rgba(255,255,255,.08); }
.bubble .who{ font-weight:700; opacity:.9; margin-bottom:.35rem; display:block; color:#e5e7eb; }
.pesquisador{ background:#0f766e; color:#e5f3f1; border-color:#115e59; }
.analista   { background:#92400e; color:#fff7ed; border-color:#b45309; }
.redator    { background:#166534; color:#e8fbe8; border-color:#15803d; }
.erro       { background:#7f1d1d; color:#fee2e2; border-color:#ef4444; white-space:pre-wrap; }
.debug      { background:#3b0764; color:#f3e8ff; border-color:#9333ea; white-space:pre-wrap; font-size:.9rem; }
.system     { background:#0f172a; color:#cbd5e1; border-color:#1f2937; font-size:.9rem; }
table[data-testid="stTable"]{ filter:none; }
</style>
"""
st.markdown(BUBBLE_CSS, unsafe_allow_html=True)

def bubble(role: str, text: str, placeholder: st.delta_generator.DeltaGenerator | None = None):
    html = f'<div class="bubble {role}"><span class="who">{role}</span>{text}</div>'
    (placeholder or st).markdown(html, unsafe_allow_html=True)

# ---------------------- Helpers SQL ----------------------
FALLBACK_SQL = (
    "SELECT produto, regiao, SUM(valor) AS total_vendido "
    "FROM vendas GROUP BY produto, regiao "
    "ORDER BY total_vendido DESC LIMIT 3;"
)

def clean_sql(text: str) -> str:
    if not isinstance(text, str):
        text = str(text)
    text = re.sub(r"```(?:sql)?\s*(.*?)```", r"\\1", text, flags=re.DOTALL | re.IGNORECASE)
    pref = re.search(r"SQLQuery:\\s*(SELECT.+?;)", text, flags=re.IGNORECASE | re.DOTALL)
    if pref:
        return pref.group(1).strip()
    matches = re.findall(r"(SELECT.+?;)", text, flags=re.IGNORECASE | re.DOTALL)
    if matches:
        return matches[-1].strip()
    return ""

def rows_to_df(rows: Any) -> pd.DataFrame:
    import ast
    try:
        if isinstance(rows, list):
            if not rows:
                return pd.DataFrame()
            first = rows[0]
            if isinstance(first, dict):
                return pd.DataFrame(rows)
            if hasattr(first, "_mapping"):
                return pd.DataFrame([dict(r._mapping) for r in rows])
            return pd.DataFrame(rows)
        if isinstance(rows, dict):
            return pd.DataFrame([rows])
        if isinstance(rows, str):
            try:
                parsed = ast.literal_eval(rows)
                return rows_to_df(parsed)
            except Exception:
                return pd.DataFrame()
        return pd.DataFrame(rows)
    except Exception:
        return pd.DataFrame()

# ---------------------- Streaming util ----------------------
# --- helper robusto para extrair texto do chunk ---
def _extract_text_from_chunk(chunk) -> str:
    # já é string?
    if isinstance(chunk, str):
        return chunk

    def _call_or_str(v):
        if callable(v):
            try:
                v = v()
            except TypeError:
                pass
        return v if isinstance(v, str) else ""

    # caminhos comuns
    if hasattr(chunk, "content"):
        s = _call_or_str(getattr(chunk, "content"))
        if s:
            return s

    # alguns provedores aninham em delta/message/generation
    for outer in ("delta", "message", "generation"):
        if hasattr(chunk, outer):
            obj = getattr(chunk, outer)
            for inner in ("content", "text"):
                if hasattr(obj, inner):
                    s = _call_or_str(getattr(obj, inner))
                    if s:
                        return s

    # sem texto => nada a acrescentar
    return ""


def stream_llm_to_placeholder(llm: ChatOllama, prompt: str, role: str, ph: st.delta_generator.DeltaGenerator) -> str:
    """
    Stream token-a-token para o placeholder SEM imprimir metadados.
    """
    text = ""
    try:
        if hasattr(llm, "stream"):
            for chunk in llm.stream(prompt):
                part = _extract_text_from_chunk(chunk)
                if not part:
                    # ignora frames sem delta de texto (evita repr com metadados)
                    continue
                text += part
                bubble(role, text, placeholder=ph)
        else:
            resp = llm.invoke(prompt)
            # mesma regra: extraia só .content
            if hasattr(resp, "content"):
                text = resp.content() if callable(resp.content) else str(resp.content)
            else:
                text = ""
            bubble(role, text, placeholder=ph)
    except Exception:
        text = f"(Falha no streaming)\n{traceback.format_exc()}"
        bubble("erro", text, placeholder=ph)
    return text


# ---------------------- UI principal ----------------------
default_q = "Quais foram os 3 produtos mais vendidos e em quais regiões venderam mais?"
q = st.text_area("Pergunta do usuário (Pesquisador → Analista → Redator):", value=default_q, height=80)

if st.button("▶️ Rodar pipeline (streaming)", type="primary", use_container_width=True):
    try:
        # Verificação: DB precisa existir e ter tabela 'vendas'
        if not os.path.exists(DB_PATH):
            st.error(
                f"Arquivo de banco não encontrado: **{DB_PATH}**. "
                "Rode antes: `python setup_db.py --db {DB_PATH}`"
            )
            st.stop()

        # Placeholders
        pesquisador_ph = st.empty()
        tabela_ph = st.empty()
        analista_ph = st.empty()
        redator_ph = st.empty()
        debug_ph = st.expander("Ver resposta crua do LLM (debug)", expanded=False)

        # Conexões
        llm = ChatOllama(model=MODEL_NAME.strip(), base_url=OLLAMA_URL.strip(), temperature=0.1)
        db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH.strip()}")

        # 1) PESQUISADOR — gerar SQL
        bubble("pesquisador", "Gerando SQL…", placeholder=pesquisador_ph)
        query_chain = create_sql_query_chain(llm, db)
        sql_raw = query_chain.invoke({"question": q.strip()})
        with debug_ph:
            st.code(str(sql_raw))
        sql = clean_sql(sql_raw) or FALLBACK_SQL
        if not sql.lower().startswith("select"):
            sql = FALLBACK_SQL
        bubble("pesquisador", f"SQL gerado:\\n{sql}", placeholder=pesquisador_ph)

        # 2) Executa e mostra tabela IMEDIATAMENTE
        try:
            rows = db.run(sql)
        except Exception as e:
            tabela_ph.error(
                "Erro ao consultar o banco. "
                f"Confira se a tabela **vendas** existe.\\n\\nDetalhe: `{e}`\\n"
                f"Se necessário, rode: `python setup_db.py --db {DB_PATH}`"
            )
            st.stop()

        df = rows_to_df(rows)
        if not df.empty:
            tabela_ph.dataframe(df, use_container_width=True)
        else:
            tabela_ph.info("Nenhuma linha retornada ou formato não reconhecido.")

        # 3) ANALISTA — streaming
        analise_prompt = ChatPromptTemplate.from_template(
            "Você é um analista de negócios. A partir dos dados abaixo, descreva tendências, "
            "regiões fortes e oportunidades de melhoria.\\n{res}"
        ).format(res=rows)
        bubble("analista", "", placeholder=analista_ph)
        analise_text = stream_llm_to_placeholder(llm, analise_prompt, "analista", analista_ph)

        # 4) REDATOR — streaming
        relatorio_prompt = ChatPromptTemplate.from_template(
            "Você é um redator corporativo. Transforme a análise a seguir em um relatório executivo "
            "claro e objetivo para gestores:\\n\\n{analise}"
        ).format(analise=analise_text)
        bubble("redator", "", placeholder=redator_ph)
        _ = stream_llm_to_placeholder(llm, relatorio_prompt, "redator", redator_ph)

    except Exception:
        bubble("erro", f"Falha ao executar agentes:\\n{traceback.format_exc()}")
