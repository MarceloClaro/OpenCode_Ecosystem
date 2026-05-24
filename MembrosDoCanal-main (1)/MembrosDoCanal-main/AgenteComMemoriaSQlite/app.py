# app.py
"""
Este arquivo é a UI em Streamlit.
A UI faz 3 coisas no modo "aula":

1) Você faz uma pergunta em linguagem natural
2) O agente gera o SQL, executa no SQLite e mostra o resultado
3) Se estiver errado, você cola o SQL correto e salva uma "lição" na memória

A memória ajuda o agente a melhorar em perguntas similares no futuro.
"""

import streamlit as st

from utils import (
    init_sample_db,
    ensure_sample_db,          # ✅ novo
    read_schema_sqlite,        # ✅ opcional (para mostrar schema)
    format_schema_for_prompt,  # ✅ opcional (para mostrar schema)
    validate_sql_readonly,
    execute_sql,
    MemoryStore,
    agent_answer,
)

DB_PATH = "sample_data.db"
MEMORY_PATH = "agent_memory.db"

# ✅ garante que o DB principal existe e tem tabelas (evita schema vazio no prompt)
ensure_sample_db(DB_PATH)

st.set_page_config(page_title="NL→SQL + Memória", layout="wide")
st.title("Agente NL→SQL + Memória")
st.caption("Suporte a consulta em linguagem natural, geração de SQL, execução no SQLite e feedback humano para aprendizado contínuo.")

with st.sidebar:
    st.header("Config (Ollama)")
    ollama_base_url = st.text_input("Ollama base URL", value="http://localhost:11434")
    ollama_model = st.text_input("Ollama model", value="granite4:latest")

    st.divider()

    if st.button("Criar/Resetar DB de exemplo"):
        init_sample_db(DB_PATH)
        st.success("DB de exemplo criado/resetado.")

    # ✅ opcional: checkbox pra mostrar schema e debug
    if st.checkbox("Mostrar schema do DB (debug)"):
        schema_txt = format_schema_for_prompt(read_schema_sqlite(DB_PATH))
        st.text(schema_txt)

memory = MemoryStore(MEMORY_PATH)

colL, colR = st.columns([1.2, 0.8])

with colL:
    st.subheader("Pergunta")
    question = st.text_input(
        "Pergunte em linguagem natural",
        value="Qual o total de amount por cidade?"
    )

    run = st.button("Gerar SQL e executar", type="primary")

    show_prompt = st.checkbox("Mostrar prompt", value=True)
    show_raw = st.checkbox("Mostrar resposta bruta (LLM)", value=False)

    if "res" not in st.session_state:
        st.session_state.res = None
    if "validated" not in st.session_state:
        st.session_state.validated = False

    if run:
        st.session_state.res = agent_answer(
            question=question,
            db_path=DB_PATH,
            memory=memory,
            ollama_model=ollama_model,
            ollama_base_url=ollama_base_url,
        )
        st.session_state.validated = False

    res = st.session_state.res
    if res:
        st.markdown("### SQL gerado")
        st.code(res["sql"], language="sql")

        if show_prompt:
            with st.expander("Prompt"):
                st.code(res["prompt"])

        if show_raw:
            with st.expander("LLM raw"):
                st.text(res["llm_raw"])

        if res["ok"]:
            st.success("Executou com sucesso.")
            st.dataframe(res["rows"])
        else:
            st.error(f"Falhou: {res['error']}")

        st.divider()
        st.subheader("Feedback humano (salvar lição)")

        correct = st.radio("Resultado está correto?", ["Sim", "Não"], horizontal=True)

        if correct == "Não":
            corrected_sql = st.text_area("Cole o SQL correto", height=140)

            rule = st.text_area(
                "Lição/Regra (curta)",
                height=90,
                value="Ex.: Faça JOIN customers->orders por customer_id."
            )

            title = st.text_input("Título da lição", value="Correção do usuário")
            note = st.text_input("Nota (opcional)", value="")

            c1, c2 = st.columns(2)

            with c1:
                if st.button("Validar SQL corrigido"):
                    ok, msg = validate_sql_readonly(corrected_sql.strip())
                    if not ok:
                        st.error(msg)
                        st.session_state.validated = False
                    else:
                        try:
                            _ = execute_sql(DB_PATH, corrected_sql.strip(), max_rows=20)
                            st.success("SQL corrigido validado (executou).")
                            st.session_state.validated = True
                        except Exception as e:
                            st.error(f"Erro ao executar SQL corrigido: {e}")
                            st.session_state.validated = False

            with c2:
                if st.button("Salvar lição"):
                    if not corrected_sql.strip():
                        st.error("Cole um SQL corrigido.")
                    elif not st.session_state.validated:
                        st.error("Valide o SQL corrigido antes de salvar.")
                    else:
                        memory.add_lesson(
                            dialect="sqlite",
                            intent=res["intent"],
                            title=title.strip() or "Correção",
                            rule=rule.strip() or "Use o SQL corrigido como referência.",
                            bad_sql=res["sql"],
                            good_sql=corrected_sql.strip(),
                            user_note=note.strip(),
                            query_text=question.strip(),
                        )
                        st.success("Lição salva na memória ✅")

with colR:
    st.subheader("Lições salvas")
    lessons = memory.list_lessons("sqlite")
    st.write(f"Total: **{len(lessons)}**")

    for l in lessons[:15]:
        with st.expander(f"#{l.id} — {l.title} ({l.intent})"):
            st.write("**Regra:**", l.rule)
            if l.user_note:
                st.write("**Nota:**", l.user_note)

            st.write("**Bad SQL:**")
            st.code(l.bad_sql, language="sql")

            st.write("**Good SQL:**")
            st.code(l.good_sql, language="sql")