import streamlit as st
import cv2
from moviepy.editor import VideoFileClip
import base64
from openai import OpenAI
import os
from pytube import YouTube
import tempfile

# OpenAI API key
client = OpenAI(api_key="sua chave aqui")
MODEL = "gpt-4o"

# Extrair frames do vídeo e representar em base64
def process_video(video_path, seconds_per_frame=2):
    base64Frames = []
    base_video_path, _ = os.path.splitext(video_path)

    video = cv2.VideoCapture(video_path)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = video.get(cv2.CAP_PROP_FPS)
    frames_to_skip = int(fps * seconds_per_frame)
    curr_frame = 0

    while curr_frame < total_frames - 1:
        video.set(cv2.CAP_PROP_POS_FRAMES, curr_frame)
        success, frame = video.read()
        if not success:
            break
        _, buffer = cv2.imencode(".jpg", frame)
        base64Frames.append(base64.b64encode(buffer).decode("utf-8"))
        curr_frame += frames_to_skip
        if len(base64Frames) == 1:  # Stop after the first frame is captured
            break
    video.release()

    #Gerar o mp3
    audio_path = f"{base_video_path}.mp3"
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path, bitrate="32k")
    clip.audio.close()
    clip.close()

    return base64Frames, audio_path

st.title("AI Youtube")

# Input URL
video_url = st.text_input("Enter the YouTube video URL:")

# verifica se certas chaves estão presentes no estado da sessão 
# (st.session_state). Se essas chaves não estiverem presentes,
# ele as inicializa com um valor padrão (None).
if 'video_file_path' not in st.session_state:
    st.session_state['video_file_path'] = None
if 'base64Frames' not in st.session_state:
    st.session_state['base64Frames'] = None
if 'audio_path' not in st.session_state:
    st.session_state['audio_path'] = None
if 'transcription' not in st.session_state:
    st.session_state['transcription'] = None

if st.button("Process Video"):
    with st.spinner('Processing video...'):
        #Obter o vídeo do Youtube
        yt = YouTube(video_url)
        video_stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
        video_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        video_stream.download(output_path=os.path.dirname(video_file.name), filename=os.path.basename(video_file.name))
        st.session_state['video_file_path'] = video_file.name
        video_file.close()

        st.session_state['base64Frames'], st.session_state['audio_path'] = process_video(st.session_state['video_file_path'], seconds_per_frame=1)
        
        # Sumariza áudio
        with open(st.session_state['audio_path'], "rb") as audio_file:
            st.session_state['transcription'] = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
            )

if st.session_state['base64Frames']:
    st.write("First Extracted Frame:")
    st.image(f"data:image/jpg;base64,{st.session_state['base64Frames'][0]}")
    st.success('Video processed successfully!')


if st.session_state['transcription']:
    st.write("Audio Transcription:")
    st.write(st.session_state['transcription'].text)  
    
    # Q&A Seção
    st.write("Ask a question about the video:")
    question = st.text_input("Your question:")

    if st.button("Get Answer"):
        with st.spinner('Generating answer...'):
            qa_both_response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "Use the video and the transcription to answer the provided question."},
                    {
                        "role": "user",
                        "content": f"""
                            These are the frames of the video.
                            ![Frame](data:image/jpg;base64,{st.session_state['base64Frames'][0]})
                            The audio transcription is: {st.session_state['transcription'].text}
                            {question}
                        """
                    }
                ],
                temperature=0,
            )
            answer = qa_both_response.choices[0].message.content
            st.write("Answer:")
            st.markdown(answer)
