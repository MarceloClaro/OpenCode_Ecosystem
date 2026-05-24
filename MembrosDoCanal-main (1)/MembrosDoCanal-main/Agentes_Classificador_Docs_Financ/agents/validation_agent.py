from typing import Dict, Any
from .base import Agent

class ValidationAgent(Agent):
    def __init__(self, min_confidence: float = 0.65, min_chars: int = 200):
        super().__init__(name="validation_agent", description="Valida resultados.")
        self.min_confidence, self.min_chars = min_confidence, min_chars
    def run(self, text: str, category: str, confidence: float) -> Dict[str, Any]:
        issues = []
        if len(text.strip()) < self.min_chars: issues.append("Texto curto.")
        if confidence < self.min_confidence: issues.append("Confiança baixa.")
        return self._build_response(True, data={"issues": issues, "needs_human_review": bool(issues)})
