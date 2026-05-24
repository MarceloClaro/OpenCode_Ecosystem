import time
import google.generativeai as genai
import mesop as me
import mesop.labs as mel
import os

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

@me.page(
    security_policy=me.SecurityPolicy(
        allowed_iframe_parents=["https://google.github.io"]
    ),
    path="/chat",
    title="Mesop Demo Chat",
)
def page():
    mel.chat(transform, title="Gemini Chat", bot_user="Mesop Bot")

generation_config = {
    "temperature": 0.5,
    "top_p": 0.90,
    "top_k": 65,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction="You are a helpful assistant, you provide helpful answers."
)

def transform(input: str, history: list[mel.ChatMessage]):
    chat_history = "\n".join(message.content for message in history)
    full_input = f"{chat_history}\n{input}"

    response = model.generate_content(full_input, stream=True)
    
    for chunk in response:
        yield chunk.text