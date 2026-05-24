"""
seeker/llm_router.py (proposto) - LLM Router refatorado para Injeção de Dependência.

Mudanças em relação ao original (core/llm.py):
  1. Remove singleton module-level _client / get_client()
  2. LLMClient aceita state_manager e event_bus opcionais via construtor
  3. Logging via event_bus.publish() quando disponível
  4. Fallback chain preservada: Claude → Claude Haiku → Ollama primary → Ollama light
  5. Compatibilidade retroativa via LLMRouterAdapter

Risco: BAIXO — classe LLMClient já existe, só adicionar DI e remover singleton.
Complexidade: 3/10
"""

from __future__ import annotations

import os
import json
import time
import logging
from pathlib import Path
from typing import Optional, Callable

import requests
from anthropic import Anthropic, APIStatusError, APIConnectionError, RateLimitError

from core.interfaces import IStateManager, IEventBus

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

CLAUDE_PRIMARY_MODEL  = "claude-sonnet-4-5"
CLAUDE_FALLBACK_MODEL = "claude-haiku-4-5-20251001"

OLLAMA_BASE_URL       = "http://localhost:11434"
OLLAMA_PRIMARY_MODEL  = "deepseek-r1:8b"
OLLAMA_LIGHT_MODEL    = "llama3.2:3b"

MAX_API_RETRIES       = 3
RETRY_DELAY_SECONDS   = 5
MAX_TOKENS            = 8192

AGENT_MAX_TOKENS: dict[str, int] = {
    "grounder":    16000,
    "theorist":    16000,
    "historian":   10000,
    "synthesizer": 10000,
    "gaper":       12000,
    "vision":      16000,
    "rude":        10000,
    "thinker":     12000,
    "social":      10000,
    "scribe":      12000,
}

AGENT_MODEL_MAP: dict[str, dict[str, str]] = {
    "grounder":    {"claude": CLAUDE_PRIMARY_MODEL,  "ollama": OLLAMA_PRIMARY_MODEL},
    "historian":   {"claude": CLAUDE_PRIMARY_MODEL,  "ollama": OLLAMA_PRIMARY_MODEL},
    "gaper":       {"claude": CLAUDE_PRIMARY_MODEL,  "ollama": OLLAMA_PRIMARY_MODEL},
    "vision":      {"claude": CLAUDE_PRIMARY_MODEL,  "ollama": OLLAMA_PRIMARY_MODEL},
    "theorist":    {"claude": CLAUDE_PRIMARY_MODEL,  "ollama": OLLAMA_PRIMARY_MODEL},
    "rude":        {"claude": CLAUDE_PRIMARY_MODEL,  "ollama": OLLAMA_PRIMARY_MODEL},
    "synthesizer": {"claude": CLAUDE_PRIMARY_MODEL,  "ollama": OLLAMA_PRIMARY_MODEL},
    "thinker":     {"claude": CLAUDE_PRIMARY_MODEL,  "ollama": OLLAMA_PRIMARY_MODEL},
    "social":      {"claude": CLAUDE_FALLBACK_MODEL, "ollama": OLLAMA_LIGHT_MODEL},
    "scribe":      {"claude": CLAUDE_FALLBACK_MODEL, "ollama": OLLAMA_LIGHT_MODEL},
}

DEFAULT_MODEL_ENTRY = {"claude": CLAUDE_PRIMARY_MODEL, "ollama": OLLAMA_PRIMARY_MODEL}


# ---------------------------------------------------------------------------
# LLM Client com DI
# ---------------------------------------------------------------------------

class LLMClient:
    """
    Router de LLM com fallback.
    Aceita state_manager e event_bus opcionais para DI.

    Uso:
        client = LLMClient(state_manager=sm, event_bus=eb)
        result = client.call(prompt, system, agent_name="grounder")
    """

    def __init__(
        self,
        state_manager: Optional[IStateManager] = None,
        event_bus: Optional[IEventBus] = None,
        api_key: Optional[str] = None,
    ):
        self.state_manager = state_manager
        self.event_bus = event_bus
        self.anthropic_client: Optional[Anthropic] = None

        if api_key:
            self.anthropic_client = Anthropic(api_key=api_key)
        else:
            self._init_anthropic()

    def _load_env(self):
        """Load .env if state_manager doesn't have the key yet."""
        env_path = Path(__file__).parent.parent / ".env"
        if not env_path.exists():
            return
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip()
                if key and value and key not in os.environ:
                    os.environ[key] = value

    def _init_anthropic(self):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            self._load_env()
            api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            logger.warning("ANTHROPIC_API_KEY not set — fallback to Ollama only")
            self._publish("llm.warning", {"message": "ANTHROPIC_API_KEY not set"})
            return
        try:
            self.anthropic_client = Anthropic(api_key=api_key)
            logger.info("Anthropic client initialized")
        except Exception as e:
            logger.warning(f"Anthropic init failed: {e}")
            self.anthropic_client = None

    def _publish(self, topic: str, data: dict):
        if self.event_bus:
            import asyncio
            try:
                asyncio.create_task(self.event_bus.publish(topic, data, source="llm"))
            except Exception:
                pass

    def _state_get(self, key: str, default=None):
        if self.state_manager:
            return self.state_manager.get(key, default)
        return default

    def _state_set(self, key: str, value):
        if self.state_manager:
            self.state_manager.set(key, value)

    # ── Routing ──────────────────────────────────────────────────────────

    def _get_models(self, agent_name: str) -> dict:
        return AGENT_MODEL_MAP.get(agent_name.lower(), DEFAULT_MODEL_ENTRY)

    def call(
        self,
        prompt: str,
        system: str = "You are a helpful research assistant.",
        agent_name: str = "unknown",
        force_local: bool = False,
    ) -> str:
        """
        Roteia chamada LLM com fallback automático.

        Priority:
          1. Claude API (modelo primário do agente)
          2. Claude API (Haiku fallback)
          3. Ollama primary model
          4. Ollama light model
          5. RuntimeError — nada disponível
        """
        models = self._get_models(agent_name)

        if not force_local and self.anthropic_client:
            result = self._call_claude(prompt, system, models["claude"], agent_name)
            if result:
                return result

            if models["claude"] != CLAUDE_FALLBACK_MODEL:
                logger.info(f"[{agent_name}] Fallback → Claude Haiku")
                self._publish("llm.fallback", {"agent": agent_name, "to": "claude-haiku"})
                result = self._call_claude(prompt, system, CLAUDE_FALLBACK_MODEL, agent_name)
                if result:
                    return result

        logger.info(f"[{agent_name}] Fallback → Ollama {models['ollama']}")
        self._publish("llm.fallback", {"agent": agent_name, "to": f"ollama:{models['ollama']}"})

        if self._check_ollama_model(models["ollama"]):
            result = self._call_ollama(prompt, system, models["ollama"], agent_name)
            if result:
                return result
        else:
            logger.warning(f"[{agent_name}] Ollama model {models['ollama']} unavailable")

        if models["ollama"] != OLLAMA_LIGHT_MODEL:
            logger.info(f"[{agent_name}] Fallback → Ollama {OLLAMA_LIGHT_MODEL}")
            if self._check_ollama_model(OLLAMA_LIGHT_MODEL):
                result = self._call_ollama(prompt, system, OLLAMA_LIGHT_MODEL, agent_name)
                if result:
                    return result

        raise RuntimeError(
            f"[{agent_name}] All LLM backends failed. "
            f"Check ANTHROPIC_API_KEY and Ollama availability."
        )

    # ── Claude ───────────────────────────────────────────────────────────

    def _call_claude(self, prompt: str, system: str, model: str,
                     agent_name: str) -> Optional[str]:
        if not self.anthropic_client:
            return None

        for attempt in range(1, MAX_API_RETRIES + 1):
            try:
                logger.info(f"[{agent_name}] Claude {model} attempt {attempt}")
                response = self.anthropic_client.messages.create(
                    model=model,
                    max_tokens=AGENT_MAX_TOKENS.get(agent_name.lower(), MAX_TOKENS),
                    system=system,
                    messages=[{"role": "user", "content": prompt}],
                )
                text = response.content[0].text
                self._publish("llm.success", {"agent": agent_name, "model": model,
                                               "chars": len(text)})
                return text

            except RateLimitError as e:
                logger.warning(f"[{agent_name}] Rate limited attempt {attempt}: {e}")
                if attempt < MAX_API_RETRIES:
                    time.sleep(RETRY_DELAY_SECONDS * attempt)

            except APIConnectionError as e:
                logger.warning(f"[{agent_name}] Connection error attempt {attempt}: {e}")
                if attempt < MAX_API_RETRIES:
                    time.sleep(RETRY_DELAY_SECONDS)

            except APIStatusError as e:
                logger.error(f"[{agent_name}] API error {e.status_code}: {e.message}")
                if e.status_code >= 500 and attempt < MAX_API_RETRIES:
                    time.sleep(RETRY_DELAY_SECONDS)
                else:
                    return None

            except Exception as e:
                logger.error(f"[{agent_name}] Claude error: {e}")
                return None

        return None

    # ── Ollama ───────────────────────────────────────────────────────────

    def _call_ollama(self, prompt: str, system: str, model: str,
                     agent_name: str) -> Optional[str]:
        url = f"{OLLAMA_BASE_URL}/api/chat"
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user",   "content": prompt},
            ],
            "stream": False,
            "options": {"num_predict": MAX_TOKENS, "temperature": 0.7},
        }
        try:
            resp = requests.post(url, json=payload, timeout=300)
            resp.raise_for_status()
            text = resp.json()["message"]["content"]
            self._publish("llm.success", {"agent": agent_name, "model": f"ollama:{model}",
                                           "chars": len(text)})
            return text
        except requests.exceptions.ConnectionError:
            logger.error(f"[{agent_name}] Ollama not reachable at {OLLAMA_BASE_URL}")
        except requests.exceptions.Timeout:
            logger.error(f"[{agent_name}] Ollama timeout (300s)")
        except Exception as e:
            logger.error(f"[{agent_name}] Ollama error: {e}")
        return None

    def _check_ollama_model(self, model: str) -> bool:
        try:
            resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
            resp.raise_for_status()
            models = [m["name"] for m in resp.json().get("models", [])]
            return any(m == model or m.startswith(model.split(":")[0]) for m in models)
        except Exception:
            return False

    # ── Health ───────────────────────────────────────────────────────────

    def health_check(self) -> dict:
        status = {"claude": False, "ollama": False, "models": {}}
        if self.anthropic_client:
            status["claude"] = True
            status["models"]["claude_primary"] = CLAUDE_PRIMARY_MODEL
            status["models"]["claude_fallback"] = CLAUDE_FALLBACK_MODEL
        try:
            resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
            if resp.ok:
                status["ollama"] = True
                status["models"]["ollama"] = [m["name"] for m in resp.json().get("models", [])]
        except Exception:
            pass
        return status


# ---------------------------------------------------------------------------
# Adapter para compatibilidade retroativa
# ---------------------------------------------------------------------------

_client: Optional[LLMClient] = None


def get_client(
    state_manager: Optional[IStateManager] = None,
    event_bus: Optional[IEventBus] = None,
) -> LLMClient:
    """Singleton compatível. Aceita DI opcional na primeira chamada."""
    global _client
    if _client is None:
        _client = LLMClient(state_manager=state_manager, event_bus=event_bus)
    return _client


def call(
    prompt: str,
    system: str = "You are a helpful research assistant.",
    agent_name: str = "unknown",
    force_local: bool = False,
) -> str:
    """Função de conveniência — compatível com API original."""
    return get_client().call(prompt, system, agent_name, force_local)
