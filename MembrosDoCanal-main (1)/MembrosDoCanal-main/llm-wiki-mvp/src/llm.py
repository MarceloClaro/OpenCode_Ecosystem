"""Cliente Ollama — chat com streaming e embeddings.

Modelos locais têm instruction-following pior que Claude/GPT, então:
- Usamos JSON mode quando precisamos de saída estruturada
- Quebramos prompts grandes em chamadas menores
- Validamos saída programaticamente quando possível
"""
from __future__ import annotations
from typing import Iterator, Optional
import json

import ollama
from sentence_transformers import SentenceTransformer
import numpy as np

from src.config import Config


_embedding_model_cache: Optional[SentenceTransformer] = None


def get_client() -> ollama.Client:
    cfg = Config.load()
    return ollama.Client(host=cfg.ollama_host)


def list_models() -> list[str]:
    """Lista modelos disponíveis no servidor Ollama."""
    try:
        client = get_client()
        response = client.list()
        return [m["model"] for m in response.get("models", [])]
    except Exception:
        return []


def chat(
    messages: list[dict],
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    json_mode: bool = False,
) -> str:
    """Chamada simples (não-streaming) ao chat. Retorna string da resposta."""
    cfg = Config.load()
    client = get_client()
    options = {"temperature": temperature if temperature is not None else cfg.temperature}
    kwargs = {
        "model": model or cfg.model_main,
        "messages": messages,
        "options": options,
        "stream": False,
    }
    if json_mode:
        kwargs["format"] = "json"
    response = client.chat(**kwargs)
    return response["message"]["content"]


def chat_stream(
    messages: list[dict],
    model: Optional[str] = None,
    temperature: Optional[float] = None,
) -> Iterator[str]:
    """Chamada streaming. Yields chunks de texto conforme chegam."""
    cfg = Config.load()
    client = get_client()
    options = {"temperature": temperature if temperature is not None else cfg.temperature}
    response = client.chat(
        model=model or cfg.model_main,
        messages=messages,
        options=options,
        stream=True,
    )
    for chunk in response:
        content = chunk.get("message", {}).get("content", "")
        if content:
            yield content


def chat_json(messages: list[dict], schema_hint: Optional[str] = None, **kwargs) -> dict:
    """Pede saída em JSON e parseia. Tenta extrair JSON mesmo se vier com lixo ao redor."""
    if schema_hint:
        # Reforça no último user message
        if messages and messages[-1]["role"] == "user":
            messages = messages[:-1] + [{
                **messages[-1],
                "content": messages[-1]["content"] + f"\n\nResponda APENAS em JSON válido. Schema esperado:\n{schema_hint}"
            }]

    raw = chat(messages, json_mode=True, **kwargs)
    return _parse_json_loose(raw)


def _parse_json_loose(text: str) -> dict:
    """Tenta parsear JSON; se falhar, tenta extrair bloco entre primeiras chaves."""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Fallback: tenta extrair entre { e }
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start:end+1])
        except json.JSONDecodeError:
            pass
    raise ValueError(f"Falha ao parsear JSON. Resposta crua:\n{text[:500]}")


# ---------- Embeddings ----------

def get_embedding_model() -> SentenceTransformer:
    """Carrega o modelo de embeddings (lazy, em cache)."""
    global _embedding_model_cache
    if _embedding_model_cache is None:
        cfg = Config.load()
        _embedding_model_cache = SentenceTransformer(cfg.embedding_model)
    return _embedding_model_cache


def embed_text(text: str) -> np.ndarray:
    """Gera embedding de um texto. Retorna array float32."""
    model = get_embedding_model()
    vec = model.encode(text, normalize_embeddings=True)
    return vec.astype(np.float32)


def embed_batch(texts: list[str]) -> list[np.ndarray]:
    """Embeddings em batch (mais rápido)."""
    model = get_embedding_model()
    vecs = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return [v.astype(np.float32) for v in vecs]


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Similaridade cosseno. Como embeddings são normalizados, é só dot product."""
    return float(np.dot(a, b))
