import streamlit as st
import requests
import pandas as pd
from dotenv import load_dotenv
import os

# Carrega variáveis do .env
load_dotenv()
API_KEY = os.getenv("WREN_API_KEY")

# Cabeçalhos comuns
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": f"Bearer {API_KEY}"
}

# Constantes fixas
PROJECT_ID = "7740"
GRAFICO_KEYWORDS = ["gráfico", "gráficos", "visualização", "mostrar visualmente", "plotar"]

st.title("📊 Inteligência Generativa de Negócios (GenBI)")

question = st.text_input("Digite sua pergunta:", "Quero uma lista de nomes de clientes")

if st.button("Executar Demanda"):
    with st.spinner("Gerando SQL..."):
        # 1. Gerar SQL
        url_generate = "https://cloud.getwren.ai/api/v1/generate_sql"
        payload_generate = {
            "projectId": PROJECT_ID,
            "question": question,
            "returnSqlDialect": False
        }
        response_sql = requests.post(url_generate, json=payload_generate, headers=headers)

        if response_sql.status_code != 200:
            st.error("Erro ao gerar SQL")
            st.text(response_sql.text)
        else:
            sql = response_sql.json().get("sql")
            st.code(sql, language="sql")

            # 2. Executar SQL
            st.info("Executando consulta no banco de dados...")
            url_run = "https://cloud.getwren.ai/api/v1/run_sql"
            payload_run = {
                "projectId": PROJECT_ID,
                "sql": sql,
                "limit": 1000
            }
            response_run = requests.post(url_run, json=payload_run, headers=headers)

            if response_run.status_code != 200:
                st.error("Erro ao executar SQL")
                st.text(response_run.text)
            else:
                records = response_run.json()["records"]
                if not records:
                    st.warning("Nenhum dado encontrado.")
                else:
                    df = pd.DataFrame(records)
                    st.success("Consulta executada com sucesso!")
                    st.dataframe(df)

                    # Baixar CSV
                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button("📥 Baixar resultados como CSV", csv, "consulta.csv", "text/csv")

                    # 3. Verificar se a pergunta pede gráfico
                    if any(keyword in question.lower() for keyword in GRAFICO_KEYWORDS):
                        st.info("Gerando gráfico com base na pergunta...")

                        url_vega = "https://cloud.getwren.ai/api/v1/generate_vega_chart"
                        payload_vega = {
                            "projectId": PROJECT_ID,
                            "question": question,
                            "sql": sql,                            
                            "sampleSize": 10000
                        }
                        response_vega = requests.post(url_vega, json=payload_vega, headers=headers)

                        if response_vega.status_code != 200:
                            st.warning("Não foi possível gerar o gráfico.")
                            st.text(response_vega.text)
                        else:
                            vega_spec = response_vega.json().get("vegaSpec")
                            if vega_spec:
                                st.success("Gráfico gerado com sucesso:")
                                st.vega_lite_chart(vega_spec.get("data", {}).get("values", []), spec=vega_spec)
                            else:
                                st.warning("A resposta não continha um gráfico válido.")
                    else:
                        st.info("Nenhum gráfico foi solicitado explicitamente na pergunta.")
