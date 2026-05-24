import os
import whisper
import ollama
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn

# Cria a aplicação FastAPI
app = FastAPI()

# Carrega o modelo Whisper uma única vez (pode levar alguns instantes)
print("Carregando o modelo Whisper 'base'...")
whisper_model = whisper.load_model("base")
print("Modelo Whisper carregado com sucesso!")

# Página HTML com interface para gravação e envio do áudio
INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Anotações de Aula com FastAPI</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    h1 { margin-bottom: 0.25em; }
    .buttons, .upload-section { margin-bottom: 1em; }
    button { padding: 10px 15px; margin-right: 10px; cursor: pointer; }
    input[type="file"] { margin-right: 10px; }
    #status { font-weight: bold; margin-bottom: 1em; color: #555; }
    .section { margin-top: 20px; background-color: #f9f9f9; padding: 15px; border-radius: 4px; }
    .section h2 { margin-top: 0; margin-bottom: 0.5em; }
    .section p { white-space: pre-wrap; }
  </style>
</head>
<body>
  <h1>Anotações de Aula</h1>
  
  <!-- Seção para gravação via microfone -->
  <div class="buttons">
    <button id="btnStart">Iniciar Gravação</button>
    <button id="btnStop" disabled>Parar Gravação</button>
  </div>
  
  <!-- Seção para upload de arquivo de áudio -->
  <div class="upload-section">
    <h2>Ou envie um arquivo de áudio</h2>
    <input type="file" id="audioFile" accept="audio/*">
    <button id="btnUpload">Enviar Arquivo</button>
  </div>

  <p id="status"></p>

  <div id="transcricao" class="section" style="display:none;">
    <h2>Transcrição da Aula</h2>
    <p id="transcricaoText"></p>
  </div>

  <div id="notas" class="section" style="display:none;">
    <h2>Notas para Estudo</h2>
    <p id="notasText"></p>
  </div>

  <script>
    let mediaRecorder;
    let audioChunks = [];

    const btnStart = document.getElementById("btnStart");
    const btnStop = document.getElementById("btnStop");
    const btnUpload = document.getElementById("btnUpload");
    const audioFileInput = document.getElementById("audioFile");
    const statusEl = document.getElementById("status");

    const transcricaoEl = document.getElementById("transcricao");
    const transcricaoTextEl = document.getElementById("transcricaoText");
    const notasEl = document.getElementById("notas");
    const notasTextEl = document.getElementById("notasText");

    // Função para enviar o áudio para o servidor
    async function enviarAudio(formData) {
      statusEl.textContent = "Enviando áudio para o servidor...";
      try {
        const response = await fetch("/transcrever", {
          method: "POST",
          body: formData
        });
        const data = await response.json();
        statusEl.textContent = "Transcrição completa!";
        transcricaoEl.style.display = "block";
        transcricaoTextEl.textContent = data.transcricao.trim();
        notasEl.style.display = "block";
        notasTextEl.textContent = data.notas_estudo.trim();
      } catch (error) {
        console.error(error);
        statusEl.textContent = "Erro ao enviar áudio para o servidor.";
      }
    }

    // Lógica para gravação com microfone
    btnStart.addEventListener("click", async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.addEventListener("dataavailable", event => {
          audioChunks.push(event.data);
        });

        mediaRecorder.addEventListener("stop", async () => {
          const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
          const formData = new FormData();
          formData.append("file", audioBlob, "gravacao.wav");
          await enviarAudio(formData);
        });

        mediaRecorder.start();
        btnStart.disabled = true;
        btnStop.disabled = false;
        statusEl.textContent = "Gravando...";
      } catch (err) {
        console.error(err);
        statusEl.textContent = "Erro ao acessar o microfone.";
      }
    });

    btnStop.addEventListener("click", () => {
      mediaRecorder.stop();
      btnStart.disabled = false;
      btnStop.disabled = true;
      statusEl.textContent = "Gravação parada. Processando...";
    });

    // Lógica para upload de arquivo de áudio
    btnUpload.addEventListener("click", async () => {
      const files = audioFileInput.files;
      if (!files || files.length === 0) {
        statusEl.textContent = "Selecione um arquivo de áudio primeiro.";
        return;
      }
      const formData = new FormData();
      formData.append("file", files[0], files[0].name);
      statusEl.textContent = "Enviando arquivo para o servidor...";
      await enviarAudio(formData);
    });
  </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def index():
    """
    Endpoint principal que retorna a página HTML.
    """
    return INDEX_HTML

@app.post("/transcrever")
async def transcrever(file: UploadFile = File(...)):
    """
    Recebe o arquivo de áudio (gravado ou enviado), realiza a transcrição com Whisper
    e extrai informações úteis para os estudos usando o Ollama.
    """
    temp_filename = "temp_audio.wav"
    try:
        # Lê e salva o áudio temporariamente para processamento
        contents = await file.read()
        with open(temp_filename, "wb") as f:
            f.write(contents)

        # Realiza a transcrição com Whisper (configurado para português)
        result = whisper_model.transcribe(temp_filename, language="pt")
        texto_transcrito = result["text"].strip()

        # Cria o prompt para extrair informações úteis para o estudo
        prompt = f"""
        Você é um assistente de estudos. A partir da transcrição de uma aula, extraia e organize as informações de forma a facilitar o aprendizado. Estruture a resposta com os seguintes tópicos:

        - Tema da Aula: Qual é o tema ou assunto abordado na aula?
        - Tópicos Principais: Quais foram os tópicos mais importantes abordados na aula?
        - Conceitos e Definições: Quais conceitos e definições foram explicados?
        - Exemplos e Aplicações: Quais exemplos ou aplicações foram citados?
        - Resumo Geral: Um resumo conciso da aula.
        - Pontos para Revisão: Quais aspectos ou dúvidas precisam ser revisados ou aprofundados?

        Transcrição da Aula:
        "{texto_transcrito}"
        """

        # Envia o prompt para o modelo via Ollama e recebe as notas para estudo
        response = ollama.chat(
            model="llama3.2:3b",
            messages=[{"role": "user", "content": prompt}]
        )
        notas_estudo = response["message"]["content"].strip()

        # Retorna a transcrição e as notas extraídas
        return JSONResponse(
            content={
                "transcricao": texto_transcrito,
                "notas_estudo": notas_estudo
            },
            status_code=200
        )
    except Exception as e:
        return JSONResponse(content={"erro": str(e)}, status_code=500)
    finally:
        # Remove o arquivo temporário, se existir
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

if __name__ == "__main__":
    # Inicia o servidor na porta 8000 (acessar http://localhost:8000/)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

