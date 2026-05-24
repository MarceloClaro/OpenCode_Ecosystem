from typing import Dict, Any
from .base import Agent
from utils.classifier import classify_with_llama

class ClassificationAgent(Agent):
    def __init__(self):
        super().__init__(name="classification_agent", description="Classifica documentos via LLM.")
    def run(self, text: str) -> Dict[str, Any]:
        try:
            category, confidence = classify_with_llama(text)
            return self._build_response(True, data={"category": category, "confidence": float(confidence)})
        except Exception as e:
            return self._build_response(False, error=str(e))
