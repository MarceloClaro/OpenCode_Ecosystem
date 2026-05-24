from abc import ABC, abstractmethod
from typing import Any, Dict

class Agent(ABC):
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description

    @abstractmethod
    def run(self, **kwargs) -> Any:
        raise NotImplementedError

    def _build_response(self, success: bool, data: Any = None, error: str = "") -> Dict[str, Any]:
        return {"agent": self.name, "success": success, "data": data, "error": error}
