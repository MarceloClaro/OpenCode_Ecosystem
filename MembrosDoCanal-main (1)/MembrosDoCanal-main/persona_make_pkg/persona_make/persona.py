import json
import re
from typing import Any, Dict, List, Tuple
from .constants import SYSTEM_BASE, CHAT_SYSTEM_TEMPLATE, STYLE_HINTS
from .llm import call_model_resilient

def try_json_loads(raw: str) -> Dict[str, Any]:
    if not raw or not raw.strip():
        raise ValueError("Resposta vazia do modelo.")
    try:
        return json.loads(raw)
    except Exception:
        pass
    block = re.search(r"\{.*\}", raw, re.DOTALL)
    if block:
        return json.loads(block.group(0))
    raise ValueError("Não foi possível interpretar JSON.")

def validate_persona(data: Dict[str, Any]) -> List[str]:
    errs: List[str] = []
    required = ["name", "summary", "opening_disclaimer"]
    for k in required:
        if not data.get(k):
            errs.append(f"Campo obrigatório ausente: {k}")
    for arr in ["key_traits", "speaking_style", "favorite_topics", "sources", "safety_notes"]:
        if arr not in data:
            data[arr] = []
    return errs

def clickable_sources_md(data: Dict[str, Any]) -> str:
    sources = data.get("sources", []) if isinstance(data, dict) else []
    links = []
    for s in sources:
        if isinstance(s, str) and s.strip().startswith(("http://", "https://")):
            links.append(f"- [{s}]({s})")
    return "\n".join(links)

def build_messages_for_persona(subject: str, region_lang: str, style_hint: str) -> List[Dict[str, str]]:
    sys = SYSTEM_BASE + f"\nIdioma de saída: {region_lang}. Estilo preferido: {style_hint}"
    return [
        {"role": "system", "content": sys},
        {"role": "user", "content": (
            f"Construa a persona para: {subject}\n"
            "Responda SOMENTE com JSON válido, sem markdown, sem texto extra."
        )}
    ]

def build_persona(subject: str, region_lang: str, web_search: bool, style_key: str,
                  model: str) -> Tuple[str, str]:
    style_hint = STYLE_HINTS.get(style_key, STYLE_HINTS["Equilibrado"])
    messages = build_messages_for_persona(subject, region_lang, style_hint)
    return call_model_resilient(messages, preferred_model=model, use_web=web_search,
                                max_tokens=1200, effort="medium")

def build_messages_for_chat(persona_json: str, style_hint: str, user_message: str,
                            history: List[List[str]]) -> List[Dict[str, str]]:
    header = CHAT_SYSTEM_TEMPLATE.replace("{persona_json}", persona_json).replace("{style_hint}", style_hint)
    transcript = []
    for turn in history:
        if turn and turn[0]:
            transcript.append(f"Usuário: {turn[0]}")
        if turn and len(turn) > 1 and turn[1]:
            transcript.append(f"Simulação: {turn[1]}")
    transcript.append(f"Usuário: {user_message}")
    return [
        {"role": "system", "content": header},
        {"role": "user", "content": "\n".join(transcript)}
    ]

def chat_with_persona(message: str, history: List[List[str]], persona_json: str,
                      style_key: str, model: str) -> str:
    style_hint = STYLE_HINTS.get(style_key, STYLE_HINTS["Equilibrado"])
    messages = build_messages_for_chat(persona_json, style_hint, message, history)
    text, warn = call_model_resilient(messages, preferred_model=model,
                                      use_web=False, max_tokens=600, effort="minimal")
    return text or f"Não foi possível obter resposta. {warn}"
