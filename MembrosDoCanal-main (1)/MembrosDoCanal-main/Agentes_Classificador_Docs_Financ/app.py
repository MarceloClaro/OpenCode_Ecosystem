import streamlit as st
import os
import pandas as pd
import time
from agents.orchestrator import OrchestratorAgent

# ===== Configuração =====
st.set_page_config(page_title="📂 Classificador de Documentos Financeiros", layout="wide")

st.title("📂 Classificador de Documentos Financeiros")
st.markdown("Envie um documento (PDF, PNG, JPG, DOCX, XLSX, PPTX) para classificar automaticamente com IA em múltiplos agentes.")

orc = OrchestratorAgent()

# ===== Inicialização de estado =====
if "classification_done" not in st.session_state:
    st.session_state.classification_done = False
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "last_uploaded_name" not in st.session_state:
    st.session_state.last_uploaded_name = None

# ===== Upload =====
uploaded = st.file_uploader("Selecione o arquivo", type=["pdf", "png", "jpg", "jpeg", "docx", "xlsx", "pptx"])

# Detecta se o usuário enviou um novo arquivo
if uploaded:
    if uploaded.name != st.session_state.last_uploaded_name:
        # Novo arquivo → reseta estado
        st.session_state.classification_done = False
        st.session_state.last_uploaded_name = uploaded.name

# Executa apenas se há novo upload e classificação ainda não foi feita
if uploaded and not st.session_state.classification_done:
    os.makedirs("uploads", exist_ok=True)
    file_path = os.path.join("uploads", uploaded.name)
    with open(file_path, "wb") as f:
        f.write(uploaded.getvalue())

    # ===== Workflow =====
    st.subheader("🚀 Execução do Workflow dos Agentes")

    steps = [
        {"name": "ExtractorAgent", "emoji": "🧾", "desc": "Extraindo texto do documento..."},
        {"name": "ClassifierAgent", "emoji": "🧠", "desc": "Classificando conteúdo com LLM..."},
        {"name": "ValidationAgent", "emoji": "✅", "desc": "Validando confiança e integridade..."},
        {"name": "PersistenceAgent", "emoji": "💾", "desc": "Salvando histórico..."},
    ]

    status_container = st.container()
    progress_bar = st.progress(0)
    progress_text = st.empty()

    result = {"success": True}
    total_steps = len(steps)

    for i, step in enumerate(steps, start=1):
        with status_container:
            st.info(f"{step['emoji']} {step['name']}: {step['desc']}")
        progress_text.text(f"Etapa {i}/{total_steps}: {step['desc']}")
        progress_bar.progress(i / total_steps)
        time.sleep(0.6)

        if step["name"] == "ExtractorAgent":
            res = orc.extractor.run(file_path=file_path)
            if not res["success"]:
                result = res
                break
            result["text"] = res["data"]["text"]

        elif step["name"] == "ClassifierAgent":
            res = orc.classifier.run(text=result["text"])
            if not res["success"]:
                result = res
                break
            result["category"] = res["data"]["category"]
            result["confidence"] = res["data"]["confidence"]

        elif step["name"] == "ValidationAgent":
            res = orc.validator.run(
                text=result["text"],
                category=result["category"],
                confidence=result["confidence"],
            )
            result["validation"] = res["data"]

        elif step["name"] == "PersistenceAgent":
            orc.persistence.save(
                uploaded.name,
                result["category"],
                result["confidence"],
                result["text"],
            )

        with status_container:
            st.success(f"✅ {step['name']} concluído com sucesso!")

    st.divider()

    if not result.get("success", True):
        st.error(f"Falha na etapa {result.get('agent', '')}: {result.get('error', '')}")
    else:
        st.success("✅ Classificação concluída com sucesso!")
        st.session_state.classification_done = True
        st.session_state.last_result = result

# ===== Exibir resultado da última classificação =====
if st.session_state.last_result:
    result = st.session_state.last_result
    col1, col2, col3 = st.columns(3)
    col1.metric("📄 Arquivo", st.session_state.last_uploaded_name or "—")
    col2.metric("🏷️ Categoria", result["category"])
    col3.metric("🤖 Confiança", f"{result['confidence'] * 100:.1f}%")

    validation = result["validation"]
    if validation["needs_human_review"]:
        st.warning("⚠️ Revisão humana recomendada:")
        for issue in validation["issues"]:
            st.write(f"- {issue}")
    else:
        st.success("✅ Validação concluída sem observações.")

    with st.expander("🧾 Conteúdo extraído"):
        st.markdown(result["text"][:8000])

# ===== Sidebar =====
st.sidebar.header("⚙️ Opções")
st.sidebar.markdown("### Filtros e Histórico")

history = orc.get_history()
if history["success"] and history["data"]["rows"]:
    df = pd.DataFrame(history["data"]["rows"], columns=["id", "Arquivo", "Categoria", "Confiança", "Data"])
    df["Confiança (%)"] = (df["Confiança"] * 100).round(1)

    categorias = ["Todas"] + sorted(df["Categoria"].dropna().unique().tolist())
    filtro = st.sidebar.selectbox("Filtrar por categoria:", categorias, key="filtro_categoria")

    df_filtrado = df if filtro == "Todas" else df[df["Categoria"] == filtro]

    st.sidebar.write(f"**{len(df_filtrado)}** documentos encontrados")

    if st.sidebar.button("📥 Exportar CSV"):
        csv = df_filtrado.to_csv(index=False, encoding="utf-8-sig")
        st.sidebar.download_button("Baixar CSV", data=csv, file_name="historico_classificacoes.csv", mime="text/csv")

    st.divider()
    st.subheader("📜 Histórico de Classificações")
    st.dataframe(df_filtrado[["Arquivo", "Categoria", "Confiança (%)", "Data"]], width='stretch')
else:
    st.sidebar.info("Nenhuma classificação registrada ainda.")
