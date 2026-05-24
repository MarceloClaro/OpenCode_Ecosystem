from openai import OpenAI

MODEL="gpt-4o"

client = OpenAI(api_key="coloque sua chave aqui")

AUDIO_PATH = "videos/seuvideo.mp3"

# 5 - Summarization: Audio Summary
transcription = client.audio.transcriptions.create(
    model="whisper-1",
    file=open(AUDIO_PATH, "rb"),
)

response = client.chat.completions.create(
    model=MODEL,
    messages=[
    {"role": "system", "content":"""Você está gerando um resumo da transcrição. Crie um resumo da transcrição fornecida. Responder em Markdown."""},
    {"role": "user", "content": [
        {"type": "text", "text": f"A transcrição do áudio é: {transcription.text}"}
        ],
    }
    ],
    temperature=0,
)
print(response.choices[0].message.content)

