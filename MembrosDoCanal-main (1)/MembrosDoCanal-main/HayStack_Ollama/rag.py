
from haystack import Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.retrievers import InMemoryEmbeddingRetriever
from haystack.components.converters import TextFileToDocument
from haystack.components.preprocessors import DocumentCleaner, DocumentSplitter
from haystack.components.writers import DocumentWriter
from haystack_integrations.components.embedders.ollama.document_embedder import OllamaDocumentEmbedder
from haystack_integrations.components.embedders.ollama.text_embedder import OllamaTextEmbedder
from haystack.components.builders import ChatPromptBuilder
from haystack_integrations.components.generators.ollama import OllamaChatGenerator
from haystack.dataclasses import ChatMessage

# Criando um armazenamento de documentos na memória
document_store = InMemoryDocumentStore()

# Componentes para processar documentos
text_file_converter = TextFileToDocument() # Converte arquivos de texto em documentos
cleaner = DocumentCleaner() # Limpa documentos removendo caracteres indesejados
splitter = DocumentSplitter() # Divide os documentos em partes menores
embedder = OllamaDocumentEmbedder() # Gera embeddings para os documentos
writer = DocumentWriter(document_store) # Escreve os documentos processados no armazenamento

# Criando pipeline de indexação
indexing_pipeline = Pipeline()
indexing_pipeline.add_component("converter", text_file_converter)
indexing_pipeline.add_component("cleaner", cleaner)
indexing_pipeline.add_component("splitter", splitter)
indexing_pipeline.add_component("embedder", embedder)
indexing_pipeline.add_component("writer", writer)

# Conectando os componentes do pipeline de indexação
indexing_pipeline.connect("converter.documents", "cleaner.documents")
indexing_pipeline.connect("cleaner.documents", "splitter.documents")
indexing_pipeline.connect("splitter.documents", "embedder.documents")
indexing_pipeline.connect("embedder.documents", "writer.documents")

# Executando a pipeline para processar e indexar o arquivo "bob.txt"
indexing_pipeline.run(data={"sources": ["bob.txt"]})

# Criando um embedder para consultas de texto
text_embedder = OllamaTextEmbedder()

# Criando um recuperador de documentos baseado em embeddings
retriever = InMemoryEmbeddingRetriever(document_store)

# Definindo o template do prompt para a geração de respostas
prompt_template = [
    ChatMessage.from_user(
      """
      Given these documents, answer the question.
      Documents:
      {% for doc in documents %}
          {{ doc.content }}
      {% endfor %}
      Question: {{query}}
      Answer:
      """
    )
]
prompt_builder = ChatPromptBuilder(template=prompt_template)

# Criando um modelo de linguagem generativa com Ollama
llm = OllamaChatGenerator(model="llama3.2:3b",
                            url = "http://localhost:11434",
                            generation_kwargs={
                              "temperature": 0.9,
                              })

# Criando pipeline RAG (retrieval-augmented generation)
rag_pipeline = Pipeline()
rag_pipeline.add_component("text_embedder", text_embedder)
rag_pipeline.add_component("retriever", retriever)
rag_pipeline.add_component("prompt_builder", prompt_builder)
rag_pipeline.add_component("llm", llm)

# Conectando os componentes do pipeline RAG
rag_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
rag_pipeline.connect("retriever.documents", "prompt_builder.documents")
rag_pipeline.connect("prompt_builder", "llm")

# Definição da consulta
query = "O que fez o Bob quando pegou a bola?"

# Executando a pipeline RAG para responder à consulta
result = rag_pipeline.run(data={"prompt_builder": {"query":query}, "text_embedder": {"text": query}})

# Exibindo a resposta gerada pelo modelo
print(result["llm"]["replies"][0].text)
