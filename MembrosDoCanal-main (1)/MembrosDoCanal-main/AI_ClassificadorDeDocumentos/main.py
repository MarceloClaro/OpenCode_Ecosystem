import os
import streamlit as st
import pandas as pd
from transformers import pipeline
import fitz  # PyMuPDF
import matplotlib.pyplot as plt
from streamlit_pdf_viewer import pdf_viewer
from streamlit_option_menu import option_menu

# Definir os modelos disponíveis
models = {
    'facebook/bart-large-mnli': 'facebook/bart-large-mnli',
    'MoritzLaurer/deberta-v3-large-zeroshot-v2.0': 'MoritzLaurer/deberta-v3-large-zeroshot-v2.0',
    'MoritzLaurer/bge-m3-zeroshot-v2.0': 'MoritzLaurer/bge-m3-zeroshot-v2.0',
    'MoritzLaurer/deberta-v3-base-zeroshot-v2.0': 'MoritzLaurer/deberta-v3-base-zeroshot-v2.0'
}

# Função para carregar o modelo selecionado
@st.cache_resource
def load_model(model_name):
    return pipeline('zero-shot-classification', model=model_name)

# Função para classificar documentos
def classify_document(classifier, text, candidate_labels):
    result = classifier(text, candidate_labels)
    return result['labels'][0]

# Função para ler documentos PDF
def read_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Função para determinar o tipo de documento e ler o conteúdo
def read_document(file_path):
    if file_path.endswith('.pdf'):
        return read_pdf(file_path)
    else:
        raise ValueError(f"Formato de arquivo não suportado: {file_path}")

# Função para indexar documentos
def index_documents(classifier, documents_path, candidate_labels):
    indexed_data = []
    files = [f for f in os.listdir(documents_path) if os.path.isfile(os.path.join(documents_path, f)) and f.endswith('.pdf')]
    total_files = len(files)
    progress_bar = st.progress(0)

    for i, filename in enumerate(files):
        file_path = os.path.join(documents_path, filename)
        try:
            text = read_document(file_path)
            category = classify_document(classifier, text, candidate_labels)
            indexed_data.append({'filename': filename, 'category': category})
        except ValueError as e:
            st.error(e)
        progress_bar.progress((i + 1) / total_files)

    return pd.DataFrame(indexed_data)

# Função para carregar dados do arquivo CSV
@st.cache_data
def load_data():
    df = pd.read_csv('indexed_documents.csv')
    return df

# Função principal para classificação
def classification():
    st.title("Classificação de Documentos PDF")

    # Upload de arquivos
    uploaded_files = st.file_uploader("Envie seus arquivos PDF", accept_multiple_files=True, type=['pdf'])

    # Seleção do modelo de classificação
    selected_model = st.selectbox("Selecione o modelo de classificação", list(models.keys()))

    # Labels para classificação
    candidate_labels = st.text_input("Insira os rótulos separados por vírgula", 'LLMs, Blockchain, CNNs').split(',')

    if st.button('Classificar'):
        if uploaded_files:
            # Salvar arquivos enviados no diretório 'documents'
            documents_path = './documents'
            if not os.path.exists(documents_path):
                os.makedirs(documents_path)

            for uploaded_file in uploaded_files:
                file_path = os.path.join(documents_path, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

            # Carregar o modelo selecionado
            classifier = load_model(models[selected_model])

            # Indexar documentos e obter resultados
            results_df = index_documents(classifier, documents_path, candidate_labels)

            if not results_df.empty:
                # Salvar resultados no arquivo CSV
                results_df.to_csv('indexed_documents.csv', index=False)
                st.success('Classificação concluída!')
                st.dataframe(results_df)

                # Mostrar gráfico de barras
                st.subheader('Resultados da Classificação')
                bar_chart_data = results_df['category'].value_counts().reset_index()
                bar_chart_data.columns = ['Category', 'Count']

                plt.figure(figsize=(10, 5))
                plt.bar(bar_chart_data['Category'], bar_chart_data['Count'])
                plt.xlabel('Category')
                plt.ylabel('Count')
                plt.title('Distribuição das Categorias')
                st.pyplot(plt)
            else:
                st.warning('Nenhum documento foi classificado.')
        else:
            st.warning('Por favor, envie pelo menos um arquivo PDF.')

# Função principal para busca
def search():
    st.title("Busca de Documentos")

    # Carrega os dados classificados
    if os.path.exists('indexed_documents.csv'):
        data = load_data()

        # Exibe o dataframe completo
        st.subheader("Todos os Documentos")
        st.write(data)

        # Campo de busca
        search_term = st.text_input("Buscar por classe de documento")
        
        if search_term:
            if 'category' in data.columns:
                results = data[data['category'].str.contains(search_term, case=False, na=False)]
            else:
                st.error("A coluna 'category' não foi encontrada no arquivo CSV.")
                return
            
            # Exibe os resultados
            st.subheader("Resultados da Busca")
            st.write(results)

            # Adiciona botão para visualizar PDF
            for index, row in results.iterrows():
                pdf_path = os.path.join('documents', row['filename'])
                if st.button(f"Ver Documento {index}"):
                    st.write(f"Visualizando documento: {pdf_path}")
                    pdf_viewer(pdf_path)
    else:
        st.warning("Nenhum documento classificado encontrado. Por favor, classifique os documentos primeiro.")

# Função principal do Streamlit com menu de navegação
def main():
    with st.sidebar:
        selected = option_menu(
            menu_title="Menu",
            options=["Classificar Documentos", "Buscar Documentos"],
            icons=["upload", "search"],
            menu_icon="cast",
            default_index=0,
        )

    if selected == "Classificar Documentos":
        classification()
    elif selected == "Buscar Documentos":
        search()

# Executa a função principal
if __name__ == "__main__":
    main()

