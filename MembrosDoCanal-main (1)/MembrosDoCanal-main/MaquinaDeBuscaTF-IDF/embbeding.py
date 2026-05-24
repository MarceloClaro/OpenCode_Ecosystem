from chunks import chunked_pdfs

from sentence_transformers import SentenceTransformer
#sentences = ["This is an example sentence", "Each sentence is converted"]

model = SentenceTransformer('sentence-transformers/all-MiniLM-L12-v2')
#embeddings = model.encode(sentences)
#print(embeddings)

embeddings = model.encode([chunked_pdf['content'] for chunked_pdf in chunked_pdfs])

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