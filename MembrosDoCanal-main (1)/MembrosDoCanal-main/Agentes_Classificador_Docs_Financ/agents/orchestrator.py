import os
from typing import Dict, Any
from .extractor_agent import ExtractionAgent
from .classifier_agent import ClassificationAgent
from .validation_agent import ValidationAgent
from .persistence_agent import PersistenceAgent

class OrchestratorAgent:
    def __init__(self):
        self.extractor, self.classifier, self.validator, self.persistence = (
            ExtractionAgent(), ClassificationAgent(), ValidationAgent(), PersistenceAgent()
        )
    def process_document(self, uploaded_file) -> Dict[str, Any]:
        os.makedirs("uploads", exist_ok=True)
        path = os.path.join("uploads", uploaded_file.name)
        with open(path, "wb") as f: f.write(uploaded_file.getvalue())
        ext = self.extractor.run(file_path=path)
        if not ext["success"]: return {"success": False, "step": "extraction", "error": ext["error"]}
        text = ext["data"]["text"]
        cls = self.classifier.run(text=text)
        if not cls["success"]: return {"success": False, "step": "classification", "error": cls["error"]}
        val = self.validator.run(text=text, category=cls["data"]["category"], confidence=cls["data"]["confidence"])
        self.persistence.save(uploaded_file.name, cls["data"]["category"], cls["data"]["confidence"], text)
        return {"success": True, "file": uploaded_file.name, "category": cls["data"]["category"],
                "confidence": cls["data"]["confidence"], "validation": val["data"], "text": text}
    def get_history(self) -> Dict[str, Any]:
        return self.persistence.list_history()
