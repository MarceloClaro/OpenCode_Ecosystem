from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from typing import List
import cv2
from openai import OpenAI
import base64
from io import BytesIO
from PIL import Image

app = FastAPI()

client = OpenAI(api_key="sua chave aqui")

MODEL = "gpt-4o"

# Função para salvar o vídeo enviado
@app.post("/upload_video/")
async def upload_video(video: UploadFile = File(...)):
    video_path = f'videos/{video.filename}'
    with open(video_path, 'wb') as buffer:
        buffer.write(await video.read())
    
    # Processar o vídeo e gerar resumo
    summary = process_video(video_path)
    return JSONResponse(content={"summary": summary})

# Função para processar o vídeo e gerar o resumo
def process_video(video_path: str) -> str:
    frames = extract_frames(video_path, frame_interval=10)  # Extrai frames a cada 10 segundos
    descriptions = [describe_frame(encode_image(frame)) for frame in frames]  # Descreve cada frame
    summary = compile_summary(descriptions)  # Compila as descrições em um resumo
    response = detecta_parkinson(summary)

    return response

# Função para extrair frames de um vídeo
def extract_frames(video_path: str, frame_interval: int = 10) -> List:
    video = cv2.VideoCapture(video_path)
    frames = []
    success, image = video.read()
    count = 0
    
    while success:
        if count % frame_interval == 0:
            frames.append(image)
        success, image = video.read()
        count += 1
    video.release()
    return frames

# Função para codificar o frame em base64 sem salvá-lo como arquivo
def encode_image(frame):
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(image)
    buffered = BytesIO()
    pil_image.save(buffered, format="JPEG")
    encoded_string = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return encoded_string

# Função para descrever o conteúdo de cada frame
def describe_frame(frame) -> str:
   
    prompt = """Descreva com precisão os movimentos musculares observados neste frame, focando em sinais que possam indicar tremores,
       rigidez muscular, movimentos lentos, traços irregulares."""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{frame}"}},
                ],
            }
        ],
    )
    print(response.choices[0].message.content)   
    return response.choices[0].message.content

# Função para compilar o resumo a partir das descrições
def compile_summary(descriptions: List[str]) -> str:
    summary = "\n".join(descriptions)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": """Crie um texto fluído, evolutivo e temporal a partir de sequencia das descrições de cada frame de um vídeo."""},
            {"role": "user", "content": [{"type": "text", "text": f"As descrições dos frames são: {summary}"}]},
        ],
        temperature=0,
    )
    print(response.choices[0].message.content)  
    return response.choices[0].message.content

# Função para detectar sinais de Parkinson a partir do resumo
def detecta_parkinson(resumo: str) -> str:
    prompt = """ Você é um assistente que possui como objetivo principal a detecção de sinais da Doença de Parkinson a partir de um texto que descreve as ações motoras de um pessoa ao logo do tempo.
      O texto foca em aspectos que são clinicamente relevantes para a Doença de Parkinson, como: Movimentos Musculares, rigidez corporal  e Tremores.
      Descrições podem identificar movimentos finos, como tremores nas mãos, rigidez corporal ou movimentos reduzidos, dificuldade para escrever ou cobrir seguimentos pontilhados que são característicos da Doença de Parkinson.
      Considere os movimentos de uma perspectiva clínica e forneça uma descrição objetiva, clara e detalhada de quaisquer sinais motores que possam estar presentes. Se não houver evidência de sinais de tremor ou rigidez, indique 'sem sinais visíveis de Parkinson."""
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": [{"type": "text", "text": f"O resumo de descrições dos frames é: {resumo}"}]},
        ],
        temperature=0,
    )
    print(response.choices[0].message.content)  
    return response.choices[0].message.content

