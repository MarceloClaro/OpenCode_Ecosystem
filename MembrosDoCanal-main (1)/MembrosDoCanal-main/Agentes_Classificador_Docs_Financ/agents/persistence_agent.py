from typing import Dict, Any
from .base import Agent
from utils.database import save_classification, get_all_classifications

class PersistenceAgent(Agent):
    def __init__(self):
        super().__init__(name="persistence_agent", description="Salva e recupera histórico.")
    def save(self, filename: str, category: str, confidence: float, text: str) -> Dict[str, Any]:
        try:
            save_classification(filename, category, confidence, text)
            return self._build_response(True, data={"filename": filename})
        except Exception as e:
            return self._build_response(False, error=str(e))
    def list_history(self) -> Dict[str, Any]:
        try:
            rows = get_all_classifications()
            return self._build_response(True, data={"rows": rows})
        except Exception as e:
            return self._build_response(False, error=str(e))
    def run(self, **kwargs) -> Dict[str, Any]:
        return self.list_history()
