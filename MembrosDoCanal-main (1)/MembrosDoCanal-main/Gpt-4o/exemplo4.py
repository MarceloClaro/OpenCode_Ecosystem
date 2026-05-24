# 4 - Summarization: Video Summary
import cv2
from moviepy.editor import VideoFileClip
import base64
from openai import OpenAI
import os 

MODEL="gpt-4o"

client = OpenAI(api_key="coloque sua chave aqui")

VIDEO_PATH = "videos/seuvideo.mp4"

def process_video(video_path, seconds_per_frame=2):
    base64Frames = []
    base_video_path, _ = os.path.splitext(video_path)

    video = cv2.VideoCapture(video_path)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = video.get(cv2.CAP_PROP_FPS)
    frames_to_skip = int(fps * seconds_per_frame)
    curr_frame=0

    while curr_frame < total_frames - 1:
        video.set(cv2.CAP_PROP_POS_FRAMES, curr_frame)
        success, frame = video.read()
        if not success:
            break
        _, buffer = cv2.imencode(".jpg", frame)
        base64Frames.append(base64.b64encode(buffer).decode("utf-8"))
        curr_frame += frames_to_skip
    video.release()

    audio_path = f"{base_video_path}.mp3"
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path, bitrate="32k")
    clip.audio.close()
    clip.close()

    print(f"Extracted {len(base64Frames)} frames")
    print(f"Extracted audio to {audio_path}")
    return base64Frames, audio_path

base64Frames, audio_path = process_video(VIDEO_PATH, seconds_per_frame=1)

response = client.chat.completions.create(
    model=MODEL,
    messages=[
    {"role": "system", "content": "Você está gerando um resumo de vídeo. Forneça um resumo do vídeo. Responda em Markdown."},
    {"role": "user", "content": [
        "Esses são os frames do vídeo.",
        *map(lambda x: {"type": "image_url", 
                        "image_url": {"url": f'data:image/jpg;base64,{x}', "detail": "low"}}, base64Frames)
        ],
    }
    ],
    temperature=0,
)
print(response.choices[0].message.content)