import streamlit as st
import requests
import urllib.parse

# URL da API FastAPI
API_URL = "http://127.0.0.1:8000/search"  # Altere para o URL correto se estiver hospedando remotamente

# URL base onde os PDFs estão acessíveis
BASE_URL = "http://127.0.0.1:8000/files/"  # Altere para a URL correta onde os PDFs estão armazenados e acessíveis

st.title("FindDoocs")
st.write("Seu buscador de documentos baseado em TF/IDF")

# Caixa de texto para o usuário digitar as palavras-chave
keywords = st.text_input("Digite as palavras-chave para buscar documentos relacionados")

# Botão para iniciar a busca
if st.button("Buscar"):
    if keywords:
        # Faz uma requisição GET para a API
        params = {"keywords": keywords}
        response = requests.get(API_URL, params=params)

        if response.status_code == 200:
            # Exibe a lista de documentos mais similares com as similaridades
            results = response.json()
            if results:
                st.write("## Resultados da Busca")
                for result in results:
                    doc_name = result['document']
                    similarity = result['similarity']
                    
                    # Codifica o nome do arquivo para URL
                    doc_url = urllib.parse.urljoin(BASE_URL, urllib.parse.quote(doc_name))

                    # Exibe o documento com um link para visualização e a similaridade
                    st.markdown(f"**Documento:** [{doc_name}]({doc_url})")
                    st.write(f"**Similaridade:** {similarity:.4f}")
                    st.write("---")
            else:
                st.write("Nenhum documento encontrado para as palavras-chave fornecidas.")
        else:
            st.error("Erro ao conectar com a API.")
    else:
        st.warning("Por favor, insira algumas palavras-chave para a busca.")

