from haystack.components.builders import ChatPromptBuilder
from haystack_integrations.components.generators.ollama import OllamaChatGenerator
from haystack.dataclasses import ChatMessage
from haystack import Pipeline

# no parameter init, we don't use any runtime template variables
prompt_builder = ChatPromptBuilder()

generator = OllamaChatGenerator(model="llama3.2:3b",
                            url = "http://localhost:11434",
                            generation_kwargs={
                              "temperature": 0.9,
                              })

pipe = Pipeline()
pipe.add_component("prompt_builder", prompt_builder)
pipe.add_component("llm", generator)

pipe.connect("prompt_builder.prompt", "llm.messages")

location = "Brazil"
messages = [ChatMessage.from_system("Always respond in Portuguese even if some input data is in other languages."),
            ChatMessage.from_user("Tell me about {{location}}")]

print(pipe.run(data={"prompt_builder": {"template_variables":{"location": location}, "template": messages}}))
