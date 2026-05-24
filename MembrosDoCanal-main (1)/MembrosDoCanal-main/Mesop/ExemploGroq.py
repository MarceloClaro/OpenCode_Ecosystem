import mesop as me
import mesop.labs as mel
from mesop import stateclass

from groq import Groq

client = Groq(
    api_key="sua chave aqui",
)

@stateclass
class State:
    pass

@me.page(
    security_policy=me.SecurityPolicy(
        allowed_iframe_parents=["https://google.github.io"]
    ),
    path="/",
    title="Mesop Demo Chat",
)
def page():
    mel.chat(transform, title="Groq Chat", bot_user="Mesop Bot")

def transform(input: str, history: list[mel.ChatMessage]):
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    messages.extend([{"role": "user", "content": message.content} for message in history])
    messages.append({"role": "user", "content": input})

    stream = client.chat.completions.create(
        messages=messages,
        model="llama3-8b-8192",
        temperature=0.5,
        max_tokens=1024,
        top_p=1,
        stop=None,
        stream=True,
    )

    for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            yield content