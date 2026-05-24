import streamlit as st
import os
import pandas as pd
from utils.extractor import extract_text_markdown
from utils.classifier import classify_with_llama
from database import save_classification, get_all_classifications

# ===== Configuração =====
st.set_page_config(page_title="📂 Classificador de Documentos Financeiros", layout="wide")

st.title("📂 Classificador de Documentos Financeiros")
st.markdown("Envie um documento (PDF, PNG, JPG, DOCX, XLSX, PPTX) para classificar automaticamente.")

# ===== Upload =====
uploaded = st.file_uploader("Selecione o arquivo", type=["pdf", "png", "jpg", "jpeg", "docx", "xlsx", "pptx"])

if uploaded:
    file_path = os.path.join("uploads", uploaded.name)
    os.makedirs("uploads", exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(uploaded.getvalue())

    with st.spinner("🔍 Processando documento..."):
        text = extract_text_markdown(file_path)
        category, confidence = classify_with_llama(text)
        save_classification(uploaded.name, category, confidence, text)

    st.success("✅ Classificação concluída!")
    st.metric("Categoria", category)
    st.metric("Confiança", f"{confidence * 100:.1f}%")

    with st.expander("🧾 Conteúdo extraído"):
        st.markdown(text[:8000])

# ===== Sidebar =====
st.sidebar.header("⚙️ Opções")
st.sidebar.markdown("### Filtros e Histórico")

rows = get_all_classifications()
if rows:
    df = pd.DataFrame(rows, columns=["id", "Arquivo", "Categoria", "Confiança", "Data"])
    df["Confiança (%)"] = (df["Confiança"] * 100).round(1)

    categorias = ["Todas"] + sorted(df["Categoria"].dropna().unique().tolist())
    filtro = st.sidebar.selectbox("Filtrar por categoria:", categorias)

    if filtro != "Todas":
        df = df[df["Categoria"] == filtro]

    st.sidebar.write(f"**{len(df)}** documentos encontrados")

    if st.sidebar.button("📥 Exportar CSV"):
        csv_path = "historico_classificacoes.csv"
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        with open(csv_path, "rb") as file:
            st.sidebar.download_button("Baixar CSV", file, file_name=csv_path)

    st.divider()
    st.subheader("📜 Histórico de Classificações")
    st.dataframe(df[["Arquivo", "Categoria", "Confiança (%)", "Data"]], use_container_width=True)
else:
    st.sidebar.info("Nenhuma classificação registrada ainda.")
