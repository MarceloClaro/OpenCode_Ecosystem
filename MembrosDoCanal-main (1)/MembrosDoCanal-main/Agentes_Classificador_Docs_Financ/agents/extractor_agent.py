from typing import Dict, Any
from .base import Agent
from utils.extractor import extract_text_markdown

class ExtractionAgent(Agent):
    def __init__(self):
        super().__init__(name="extraction_agent", description="Extrai texto estruturado.")
    def run(self, file_path: str) -> Dict[str, Any]:
        try:
            text = extract_text_markdown(file_path)
            if not text.strip():
                return self._build_response(False, error="Nenhum texto extraído.")
            return self._build_response(True, data={"text": text})
        except Exception as e:
            return self._build_response(False, error=str(e))
