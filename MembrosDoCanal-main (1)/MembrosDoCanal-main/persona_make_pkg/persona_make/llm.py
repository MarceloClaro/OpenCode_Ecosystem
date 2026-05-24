import os
import json
from typing import Dict, List, Tuple
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Defina OPENAI_API_KEY no .env")

client = OpenAI(api_key=OPENAI_API_KEY)

SUPPORTED_MODELS = ["gpt-5", "gpt-5-mini", "gpt-5-nano"]

def _extract_text_from_response(resp) -> str:
    # 1) Caminho direto (OpenAI Responses API recente)
    txt = getattr(resp, "output_text", None)
    if isinstance(txt, str) and txt.strip():
        return txt.strip()

    # 2) Serialização em dict
    import json as _json
    d = None
    for attr in ("model_dump", "to_dict"):
        try:
            if hasattr(resp, attr):
                d = getattr(resp, attr)()
                break
        except Exception:
            pass
    if d is None:
        try:
            if hasattr(resp, "model_dump_json"):
                d = _json.loads(resp.model_dump_json())
        except Exception:
            pass

    # 3) Tenta extrair do formato padrão: output -> [ { content: [ { type, text:{value} } ] } ]
    def _from_output_list(dd):
        parts = []
        out = dd.get("output")
        if isinstance(out, list):
            for item in out:
                content = item.get("content")
                if isinstance(content, list):
                    for c in content:
                        t = c.get("text")
                        if isinstance(t, dict) and isinstance(t.get("value"), str):
                            parts.append(t["value"])
        return "\n".join(parts).strip() if parts else ""

    if isinstance(d, dict):
        text = _from_output_list(d)
        if text:
            return text

        # Alguns SDKs encaixotam em d["response"]["output"]
        resp_obj = d.get("response")
        if isinstance(resp_obj, dict):
            text = _from_output_list(resp_obj)
            if text:
                return text

    # 4) Último recurso: procura qualquer string grande no dict (evita falsos negativos)
    if isinstance(d, dict):
        for k in ("content", "message", "text"):
            v = d.get(k)
            if isinstance(v, str) and len(v.strip()) > 0:
                return v.strip()

    return ""


def _once_nonstream(messages: List[Dict[str, str]], *, model: str,
                    use_tools: bool, max_tokens: int, effort: str) -> Tuple[str, str]:
    tools = [{"type": "web_search_preview"}] if use_tools else None
    try:
        kwargs = {"model": model, "input": messages, "max_output_tokens": max_tokens}
        if tools:
            kwargs["tools"] = tools
        if model.startswith("gpt-5") or "reasoning" in model:
            kwargs["reasoning"] = {"effort": effort}
        resp = client.responses.create(**kwargs)
        text = _extract_text_from_response(resp)
        if text:
            return text, ""
        return "", f"[erro] modelo não retornou texto (model={model})."
    except Exception as e:
        return "", f"[erro] chamada falhou (model={model}, tools={use_tools}): {e}"

def call_model_resilient(messages: List[Dict[str, str]], *,
                         preferred_model: str = "gpt-5",
                         use_web: bool = False,
                         max_tokens: int = 1000,
                         effort: str = "medium") -> Tuple[str, str]:
    # 1) tenta modelo escolhido
    text, warn = _once_nonstream(messages, model=preferred_model,
                                 use_tools=use_web, max_tokens=max_tokens, effort=effort)
    if text:
        return text, warn
    # 2) tenta novamente sem web
    text2, warn2 = _once_nonstream(messages, model=preferred_model,
                                   use_tools=False, max_tokens=max_tokens, effort=effort)
    if text2:
    # já temos resposta; não precisa poluir a UI com warn
    # w = "\n".join([m for m in [warn, warn2, "[aviso] fallback: sem web_search_preview"] if m]).strip()
        return text2, ""
  
    # 3) fallback progressivo
    for fb in ("gpt-5-mini", "gpt-5-nano"):
        text3, warn3 = _once_nonstream(messages, model=fb, use_tools=False,
                                    max_tokens=max_tokens, effort="minimal")
        if text3:
            # Antes:
            # w = "\n".join([m for m in [warn, warn2, warn3, f"[aviso] fallback de modelo: {fb}"] if m]).strip()
            # return text3, w
            # Agora (não polui a UI com aviso quando já temos resposta):
            return text3, ""

