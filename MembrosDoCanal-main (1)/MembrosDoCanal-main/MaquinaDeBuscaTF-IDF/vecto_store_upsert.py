from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams
from embbeding import embeddings
from chunks import chunked_pdfs 

# Insira o URL e a chave de API da sua instância Qdrant Cloud
QDRANT_CLOUD_URL = "https://20e89b3a-838b-49ae-aab2-99e82571dbae.us-east4-0.gcp.cloud.qdrant.io:6333"
API_KEY = "Lju12sgNtT32767Z6wpWNwhyINPo8o3doyLDJwdnSGiKdEvQzNWpLA"

# Conectando ao Qdrant Cloud com timeout aumentado
client = QdrantClient(url=QDRANT_CLOUD_URL, api_key=API_KEY, timeout=60.0)  # Timeout de 60 segundos

# Criação da coleção, caso não exista
if not client.collection_exists("papers-test"):
    client.create_collection(
        collection_name="papers-test",
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )

print("Coleções disponíveis:", client.get_collections())

# Preparação dos pontos a serem inseridos
points = [
    {
        "id": i,
        "vector": embedding,
        "payload": {
            "content": doc['content'],
            "paragraph": doc['paragraph'],
            "source": doc['source'] 
        },
    }
    for i, (embedding, doc) in enumerate(zip(embeddings, chunked_pdfs))
]

# Inserção dos pontos em lotes
batch_size = 100  # Define o tamanho do lote para inserção
for i in range(0, len(points), batch_size):
    batch = points[i:i + batch_size]
    client.upsert(
        collection_name="papers-test",
        points=batch
    )
    print(f"Lote {i // batch_size + 1} inserido com sucesso.")

print("Upsert concluído com sucesso.")
