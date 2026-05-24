import streamlit as st
from PIL import Image
import chromadb
from chromadb.utils import embedding_functions
import google.generativeai as genai

# Configurar a chave da API
genai.configure(api_key="sua chave aqui")

CHROMA_DATA_PATH = "chroma_data/"
EMBED_MODEL = "all-MiniLM-L6-v2"
COLLECTION_NAME = "demo_docs"

client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)

embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=EMBED_MODEL
)

multimodal_db = client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=embedding_func,
    metadata={"hnsw:space": "cosine"},
)

# Verifica se a session_state já foi inicializada
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None

# Função para lidar com o upload de imagem e adicionar ao banco de dados
def upload_and_add_to_db():
    st.sidebar.header("Menu")
    menu_option = st.sidebar.radio("Select an option:", ["Upload Image", "Semantic Search"])

    if menu_option == "Upload Image":
        st.header("Upload Image to Database")
        # Usa o st.session_state.uploaded_file em vez de uploaded_file
        st.session_state.uploaded_file = st.file_uploader("Choose an image...", type="jpg")

        if st.session_state.uploaded_file is not None:
            image = Image.open(st.session_state.uploaded_file)
            st.image(image, caption="Uploaded Image.", use_column_width=True)

            vision_description = None
            # Gerar descrição da imagem usando gemini-pro-vision
            model_vision = genai.GenerativeModel('gemini-pro-vision')
            vision_description = model_vision.generate_content(["Descreve com detalhes o que você vê na imagem ",  image])

            # Exibir a descrição no frontend
            st.subheader("Descrição da Imagem:")
            st.write(vision_description.text)

            unique_id = str(multimodal_db.count() + 1)
            image_path = f"imagens/{st.session_state.uploaded_file.name}"
            image.save(image_path)

            multimodal_db.add(
                ids=[unique_id],
                documents=vision_description.text,
                metadatas=[{'img_category': "imagem", 'item_name': "pessoa"}],
                uris=[image_path],
            )
            st.success("Image added to the database!")

            # Limpar o estado da imagem após a adição ao banco de dados
            st.session_state.uploaded_file = None

    elif menu_option == "Semantic Search":
        st.header("Search Images in Database")
        query_database()

# Função para lidar com a consulta no banco de dados
def query_database():
    query_text = st.text_input("Search for images:")

    if st.button("Search"):

        query_results = multimodal_db.query(
            query_texts=[query_text],
            n_results=multimodal_db.count(),
            include=['documents', 'distances', 'metadatas', 'uris'],
        )

        st.session_state.uploaded_file = None
        print_query_results([query_text], query_results)

# Função para imprimir os resultados de uma consulta
def print_query_results(query_list: list, query_results: dict) -> None:
    result_count = len(query_results['ids'][0])

    for i in range(len(query_list)):
        st.write(f'Results for query: {query_list[i]}')

        for j in range(result_count):
            id = query_results["ids"][i][j]
            distance = query_results['distances'][i][j]
            document = query_results['documents'][i][j]
            #metadata = query_results['metadatas'][i][j]
            uri = query_results['uris'][i][j]

            st.write(f'id: {id}, distance: {distance}, document: {document}')

            # Exibir a imagem do resultado
            result_image = Image.open(uri)
            st.image(result_image, caption=f"Result Image {j + 1}", use_column_width=True)

# Interface do Streamlit
st.title("Multimodal Image Database")

# Chamada para a função principal
upload_and_add_to_db()

