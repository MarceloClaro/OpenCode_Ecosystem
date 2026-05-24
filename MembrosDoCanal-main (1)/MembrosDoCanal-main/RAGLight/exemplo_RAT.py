from raglight.rat.simple_rat_api import RATPipeline
from raglight.models.data_source_model import FolderSource
from raglight.config.settings import Settings
from raglight.config.rat_config import RATConfig
from raglight.config.vector_store_config import VectorStoreConfig

# Ativa logs para depuração
Settings.setup_logging()

# Documentos locais a serem indexados
knowledge_base = [
    FolderSource(path="./meus_docs")
]

# Configuração do banco vetorial
vector_store_config = VectorStoreConfig(
    embedding_model=Settings.DEFAULT_EMBEDDINGS_MODEL,  # Usa MiniLM via HuggingFace
    provider=Settings.HUGGINGFACE,
    database=Settings.CHROMA,
    persist_directory='./vetor_db',
    collection_name='base_conhecimento'
)

# Configuração do RAT
config = RATConfig(
    cross_encoder_model=Settings.DEFAULT_CROSS_ENCODER_MODEL,
    llm="qwen2.5vl:7b",  # LLM principal via Ollama
    provider=Settings.OLLAMA,
    system_prompt=Settings.DEFAULT_SYSTEM_PROMPT,
    reasoning_llm="qwen2.5vl:7b", # LLM para reflexão também é o gemma
    reflection=10, # Duas rodadas de reflexão
    k=5  # Top-k documentos mais relevantes
)

# Inicializa a pipeline RAT
pipeline = RATPipeline(config, vector_store_config)

# Constrói (indexa) os documentos. Pule se já tiver rodado antes.
pipeline.build()

# Faz uma pergunta
pergunta = "Qual foi o modelo de CNN que apresentou o melhor resultado? Responda de forma objetiva qual foi o melhor modelo em português brasileiro."
resposta = pipeline.generate(pergunta)

# Exibe a resposta
print("\n📘 Resposta final com reflexão:\n")
print(resposta)
