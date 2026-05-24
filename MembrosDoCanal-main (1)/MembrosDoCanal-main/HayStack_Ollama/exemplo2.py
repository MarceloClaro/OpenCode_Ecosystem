from haystack_integrations.components.generators.ollama import OllamaGenerator

from haystack import Pipeline, Document
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.document_stores.in_memory import InMemoryDocumentStore

template = """
Given the following information, answer the question.

Context: 
{% for document in documents %}
    {{ document.content }}
{% endfor %}

Question: {{ query }}?
"""

docstore = InMemoryDocumentStore()
docstore.write_documents([Document(content="I really like summer"),
                          Document(content="My favorite sport is soccer"),
                          Document(content="I don't like reading sci-fi books"),
                          Document(content="I don't like crowded places"),])

generator = OllamaGenerator(model="llama3.2:3b",
                            url = "http://localhost:11434",
                            generation_kwargs={
                              "num_predict": 100,
                              "temperature": 0.9,
                              })

pipe = Pipeline()
pipe.add_component("retriever", InMemoryBM25Retriever(document_store=docstore))
pipe.add_component("prompt_builder", PromptBuilder(template=template))
pipe.add_component("llm", generator)
pipe.connect("retriever", "prompt_builder.documents")
pipe.connect("prompt_builder", "llm")

query="What your favorite sport?"

result = pipe.run({"prompt_builder": {"query": query},
									"retriever": {"query": query}})

print(result)

