from haystack_integrations.components.generators.ollama import OllamaGenerator

generator = OllamaGenerator(model="llama3.2:3b",
                            url = "http://localhost:11434",
                            generation_kwargs={
                              "num_predict": 100,
                              "temperature": 0.9,
                              })

print(generator.run("Who is the best American actor?"))

