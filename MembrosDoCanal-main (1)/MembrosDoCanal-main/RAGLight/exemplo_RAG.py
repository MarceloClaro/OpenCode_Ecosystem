from raglight.rag.simple_rag_api import RAGPipeline
from raglight.models.data_source_model import FolderSource
from raglight.config.settings import Settings
from raglight.config.rag_config import RAGConfig
from raglight.config.vector_store_config import VectorStoreConfig

# Ativa logs detalhados
Settings.setup_logging()

# Documentos a serem indexados
knowledge_base = [
    FolderSource(path="./meus_docs")
]

# Configuração do banco vetorial
vector_store_config = VectorStoreConfig(
    embedding_model=Settings.DEFAULT_EMBEDDINGS_MODEL,
    provider=Settings.HUGGINGFACE,
    database=Settings.CHROMA,
    persist_directory='./vetor_db',
    collection_name='base_conhecimento'
)

# Configuração do RAG com modelo local rodando via Ollama
config = RAGConfig(
    llm="qwen2.5vl:7b", # nome do modelo exatamente como aparece no Ollama
    provider=Settings.OLLAMA,
    knowledge_base=knowledge_base,
    k=5 # número de documentos buscados
)

# Inicializa pipeline
pipeline = RAGPipeline(config, vector_store_config)

# Indexa os documentos
pipeline.build()

# Faz uma pergunta
resposta = pipeline.generate("Qual foi o modelo de CNN que apresentou o melhor resultado? Responda em português brasileiro.")
print("Resposta da IA:\n", resposta)
