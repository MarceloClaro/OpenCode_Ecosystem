"""
LLMClient — Cliente LLM unificado para o pipeline ANP.

Inspirado por LLMClient em BettaFish QueryEngine/llms/base.py.
Abstrai chamadas a modelos de linguagem com fallback offline,
streaming e gerenciamento de erros.

Modos de operação:
  1. OpenAI-compatible: Usa openai.ChatCompletion (API key e endpoint configuráveis).
  2. Offline/fallback: Retorna respostas template-based quando sem LLM.
"""

import json
import os
from typing import Any, Dict, List, Optional, Union
from datetime import datetime


class LLMClient:
    """Cliente LLM unificado com fallback offline.

    Attributes:
        model_name: Nome do modelo (ex: gpt-4o, deepseek-chat, qwen3).
        api_key: Chave da API (lê de env var se não informada).
        base_url: URL base da API (para provedores alternativos).
        temperature: Temperatura do modelo (default 0.3 para consistência).
        max_tokens: Máximo de tokens por chamada.
        offline_fallback: Se True, usa respostas template em vez de
                          chamar API quando sem conexão.
    """

    def __init__(
        self,
        model_name: str = "gpt-4o",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 4096,
        offline_fallback: bool = True,
    ):
        self.model_name = model_name
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.base_url = base_url or os.environ.get(
            "OPENAI_BASE_URL",
            "https://api.openai.com/v1",
        )
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.offline_fallback = offline_fallback
        self._client = None  # Lazy init

    def _ensure_client(self):
        """Inicializa o cliente OpenAI sob demanda."""
        if self._client is not None:
            return
        try:
            from openai import OpenAI
            self._client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
            )
        except ImportError:
            self._client = None  # Sem openai instalado

    def invoke(
        self,
        system_prompt: str,
        user_message: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Chamada síncrona ao LLM.

        Args:
            system_prompt: Instrução do sistema.
            user_message: Mensagem do usuário.
            temperature: Temperatura (default: self.temperature).
            max_tokens: Máx tokens (default: self.max_tokens).

        Returns:
            Resposta textual do modelo.
        """
        self._ensure_client()

        if self._client and self.api_key:
            try:
                resp = self._client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message},
                    ],
                    temperature=temperature or self.temperature,
                    max_tokens=max_tokens or self.max_tokens,
                )
                return resp.choices[0].message.content or ""
            except Exception as e:
                if not self.offline_fallback:
                    raise
                return self._fallback(system_prompt, user_message, str(e))
        else:
            return self._fallback(system_prompt, user_message)

    def invoke_json(
        self,
        system_prompt: str,
        user_message: str,
        temperature: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Chamada LLM esperando resposta JSON.

        Tenta fazer parse da resposta como JSON; se falhar,
        retorna dicionário vazio.
        """
        raw = self.invoke(
            system_prompt=system_prompt,
            user_message=user_message,
            temperature=temperature or self.temperature,
        )
        # Tenta extrair bloco JSON ```json ... ```
        import re
        json_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", raw, re.DOTALL)
        content = json_match.group(1) if json_match else raw.strip()

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {"error": "failed to parse JSON", "raw": raw[:500]}

    def get_model_info(self) -> str:
        """Retorna descrição do modelo/config atual."""
        return (
            f"{self.model_name} @ {self.base_url} "
            f"(temp={self.temperature}, max={self.max_tokens})"
        )

    # ── Fallback offline ───────────────────────────────────────────────

    def _fallback(
        self,
        system_prompt: str,
        user_message: str,
        error: str = "",
    ) -> str:
        """Resposta template quando LLM não disponível."""
        return json.dumps(
            {
                "fallback": True,
                "model": self.model_name,
                "error": error or "no LLM client available",
                "note": "Resposta template — substitua por chamada LLM real.",
                "system_prompt_preview": system_prompt[:200],
                "user_message_preview": user_message[:200],
                "timestamp": datetime.now().isoformat(),
            },
            ensure_ascii=False,
        )

    def __repr__(self) -> str:
        return f"LLMClient(model={self.model_name}, online={self._client is not None})"
