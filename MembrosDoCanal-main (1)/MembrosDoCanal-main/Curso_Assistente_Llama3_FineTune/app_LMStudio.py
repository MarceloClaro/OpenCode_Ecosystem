# Example: reuse your existing OpenAI setup
from openai import OpenAI

# Point to the local server
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

completion = client.chat.completions.create(
  model="TheBloke/llmfinetuneCurso",
  messages=[
    {"role": "system", "content": "Responda as questões."},
    {"role": "user", "content": "Qual foi a CNN que apresentou o melhor desempenho?"}
  ],
  temperature=0.7,
)

print(completion.choices[0].message)