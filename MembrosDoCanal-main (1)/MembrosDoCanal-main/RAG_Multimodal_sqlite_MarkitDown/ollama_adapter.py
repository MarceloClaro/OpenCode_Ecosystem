import base64
import io
from PIL import Image
import requests

# Classes auxiliares para simular a resposta estilo OpenAI
class _MockChoice:
    def __init__(self, content):
        self.message = type("obj", (object,), {"content": content})()

class _MockResponse:
    def __init__(self, content):
        self.choices = [_MockChoice(content)]

class OllamaAdapterMarkItDown:
    def __init__(
        self,
        model_name: str,
        base_url: str = "http://localhost:11434",
        connect_timeout: float = 3.0,
        read_timeout: float = 180.0,
        max_side: int = 1600,  # limita dimensão da imagem
    ):
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.timeout = (connect_timeout, read_timeout)
        self.max_side = max_side

        # Para compatibilidade com chamadas tipo client.chat.completions.create(...)
        self.chat = self
        self.completions = self

    # ---- utilidades ----
    def _ensure_ollama_alive(self):
        try:
            # /api/tags é leve e confirma que o daemon respondeu
            requests.get(f"{self.base_url}/api/tags", timeout=self.timeout)
        except requests.RequestException as e:
            raise RuntimeError(
                f"Ollama não respondeu em {self.base_url}. "
                f"Verifique se o daemon está rodando (ex.: `ollama serve`). Detalhes: {e}"
            )

    def _fetch_or_decode_image(self, url_or_data: str) -> bytes:
        # data URL?
        if url_or_data.startswith("data:image"):
            try:
                _, encoded = url_or_data.split(",", 1)
                return base64.b64decode(encoded)
            except Exception as e:
                raise ValueError(f"Data URL de imagem inválida: {e}")

        # http(s)
        if url_or_data.startswith("http://") or url_or_data.startswith("https://"):
            try:
                resp = requests.get(url_or_data, timeout=self.timeout)
                resp.raise_for_status()
                return resp.content
            except requests.RequestException as e:
                raise RuntimeError(f"Falha ao baixar a imagem por URL: {e}")

        raise ValueError("Formato de imagem não suportado (use data:URL ou http(s)://).")

    def _shrink_and_encode_jpeg(self, raw_bytes: bytes) -> str:
        # Reduz o tamanho (se necessário) e re-encode em JPEG de qualidade moderada
        img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
        w, h = img.size
        scale = 1.0
        if max(w, h) > self.max_side:
            scale = self.max_side / float(max(w, h))
            nw, nh = int(w * scale), int(h * scale)
            img = img.resize((nw, nh), Image.LANCZOS)

        buff = io.BytesIO()
        img.save(buff, format="JPEG", quality=85, optimize=True)
        return base64.b64encode(buff.getvalue()).decode("utf-8")

    # ---- API simulada ----
    def create(self, model, messages, **kwargs):
        """
        Espera:
        messages = [{
          "role": "user",
          "content": [
             {"type":"text","text":"descreva a imagem"},
             {"type":"image_url","image_url":{"url":"data:image/png;base64,..."}}
          ]
        }]
        """
        # 1) Sanidade & health-check
        self._ensure_ollama_alive()

        # 2) Extrai prompt e imagem
        prompt = ""
        image_url = None
        if not messages or "content" not in messages[0]:
            raise ValueError("Mensagens no formato inesperado (faltou 'content').")

        for part in messages[0]["content"]:
            if part.get("type") == "text":
                prompt = part.get("text", "")
            elif part.get("type") == "image_url":
                image_url = part.get("image_url", {}).get("url")

        if not image_url:
            raise ValueError("Imagem não fornecida (faltou 'image_url').")

        # 3) Obtém bytes da imagem (data: ou http(s))
        raw = self._fetch_or_decode_image(image_url)
        # 4) Reduz/comprime e converte para base64
        img_b64 = self._shrink_and_encode_jpeg(raw)

        # 5) Chamada ao Ollama com timeouts
        try:
            resp = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "images": [img_b64],
                    "stream": False,
                },
                timeout=self.timeout,
            )
            resp.raise_for_status()
        except requests.Timeout:
            raise TimeoutError(
                "Tempo esgotado ao aguardar resposta do Ollama. "
                "Considere reduzir a imagem, usar um modelo menor ou aumentar o timeout."
            )
        except requests.RequestException as e:
            raise RuntimeError(f"Erro ao chamar Ollama: {e}")

        data = resp.json()
        result_text = (data.get("response") or "").strip()
        if not result_text and data.get("done") is True:
            # Alguns modelos podem retornar vazio se o prompt for ruim
            result_text = "(Sem saída do modelo — verifique o prompt e o modelo VLM.)"

        return _MockResponse(content=result_text)
