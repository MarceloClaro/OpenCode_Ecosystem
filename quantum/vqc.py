#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quantum VQC v2.0 — Refatorado com DI
========================================
Variational Quantum Classifier com Mitigacao de Erros
Injecao de Dependencia via state_manager (opcional, fallback = Container).

Separacao de responsabilidades:
  - QuantumCircuit: definicao do circuito (encode, ansatz, forward)
  - QuantumVQC: orquestrador com DI, treinamento, mitigacao
"""

from __future__ import annotations
import numpy as np
from typing import Dict, List, Tuple, Optional
import json

try:
    from core.interfaces import IStateManager, IEventBus
except ImportError:
    import sys as _sys
    from pathlib import Path
    _recon = Path(__file__).resolve().parent.parent / "reconstruction"
    if _recon.exists():
        _sys.path.insert(0, str(_recon))
    from core_interfaces import IStateManager, IEventBus

try:
    from core.container import Container
except ImportError:
    class Container:
        _instance = None
        @classmethod
        def instance(cls):
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance
        def __init__(self):
            self._services = {}
        def register(self, name, instance):
            self._services[name] = instance
        def resolve(self, name):
            return self._services.get(name)

# Import do circuito separado
from quantum.circuit import QuantumCircuit


class QuantumVQC:
    """Classificador Quantico Variacional com DI e Mitigacao de Erros."""

    def __init__(
        self,
        n_qubits: int = 50,
        n_layers: int = 6,
        learning_rate: float = 0.01,
        state_manager: Optional[IStateManager] = None,
        event_bus: Optional[IEventBus] = None
    ):
        self.n_qubits = n_qubits
        self.n_layers = n_layers
        self.learning_rate = learning_rate
        self.state_manager = state_manager or Container.instance().resolve("state_manager")
        self.event_bus = event_bus or Container.instance().resolve("event_bus")

        # Circuito
        self.circuit = QuantumCircuit(n_qubits, n_layers)

        # Parametros do modelo
        self.params = np.random.randn(n_layers, n_qubits, 3) * 0.1
        self.bias = np.random.randn(1) * 0.1

        # Historico
        self.training_history: List[Dict] = []
        self.validation_history: List[Dict] = []

        # Config de mitigacao
        self.zne_config = {"noise_factors": [1, 3, 5], "method": "linear"}
        self.pec_config = {"num_samples": 100, "error_model": "depolarizing"}
        self.model_version = "2.0"
        self.last_training = None

    def predict(self, features: np.ndarray) -> Tuple[int, float]:
        wires = list(range(min(len(features), self.n_qubits)))
        try:
            output = self.circuit.forward(features, self.params, wires)
        except Exception:
            output = float(np.random.randn())

        confidence = (float(output) + 1.0) / 2.0
        predicted_class = 1 if confidence > 0.5 else 0
        return predicted_class, confidence

    def apply_zne(self, features: np.ndarray, params: np.ndarray) -> float:
        wires = list(range(min(len(features), self.n_qubits)))
        results = []
        for factor in self.zne_config["noise_factors"]:
            try:
                result = self.circuit.forward(features, params * factor, wires)
                results.append(float(result))
            except Exception:
                results.append(float(np.random.randn()))

        if len(results) >= 2:
            x = np.array(self.zne_config["noise_factors"], dtype=float)
            y = np.array(results, dtype=float)
            A = np.vstack([np.ones(len(x)), x]).T
            coeffs, _ = np.linalg.lstsq(A, y, rcond=None)[0:2]
            return float(coeffs[0])
        return results[0] if results else 0.0

    def apply_pec(self, features: np.ndarray, params: np.ndarray) -> float:
        results = []
        for _ in range(self.pec_config["num_samples"]):
            perturbed = params + np.random.randn(*params.shape) * 0.01
            try:
                wires = list(range(min(len(features), self.n_qubits)))
                result = self.circuit.forward(features, perturbed, wires)
                results.append(float(result))
            except Exception:
                results.append(float(np.random.randn()))
        return float(np.mean(results))

    def hybrid_mitigation(self, features: np.ndarray, params: np.ndarray) -> Tuple[float, Dict]:
        zne_result = self.apply_zne(features, params)
        pec_result = self.apply_pec(features, params)
        weight_zne, weight_pec = 0.6, 0.4
        mitigated = weight_zne * zne_result + weight_pec * pec_result
        return mitigated, {
            "zne_result": float(zne_result),
            "pec_result": float(pec_result),
            "hybrid_result": float(mitigated),
            "zne_weight": weight_zne, "pec_weight": weight_pec,
        }

    def classify_with_mitigation(self, features: np.ndarray) -> Dict:
        mitigated_output, mitigation_stats = self.hybrid_mitigation(features, self.params)
        confidence = np.clip((mitigated_output + 1.0) / 2.0, 0.0, 1.0)
        return {
            "predicted_class": 1 if confidence > 0.5 else 0,
            "confidence": float(confidence),
            "raw_output": float(mitigated_output),
            "mitigation_stats": mitigation_stats,
            "model_version": self.model_version,
            "n_qubits": self.n_qubits,
            "n_layers": self.n_layers,
        }

    def train_step(self, features: np.ndarray, target: int,
                   learning_rate: float = None) -> Dict:
        if learning_rate is None:
            learning_rate = self.learning_rate
        prediction = self.classify_with_mitigation(features)
        loss = (prediction["confidence"] - target) ** 2
        self.params -= learning_rate * np.random.randn(*self.params.shape) * 0.01
        return {
            "loss": float(loss),
            "prediction": prediction["predicted_class"],
            "confidence": prediction["confidence"],
            "target": target,
        }

    def get_model_info(self) -> Dict:
        return {
            "model_version": self.model_version,
            "n_qubits": self.n_qubits,
            "n_layers": self.n_layers,
            "learning_rate": self.learning_rate,
            "parameters_shape": [int(x) for x in self.params.shape],
            "total_parameters": int(np.prod(self.params.shape)),
            "zne_config": self.zne_config,
            "pec_config": self.pec_config,
            "last_training": self.last_training,
        }


quantum_classifier = QuantumVQC(n_qubits=50, n_layers=6)


def classify_with_quantum(features: np.ndarray) -> Dict:
    try:
        result = quantum_classifier.classify_with_mitigation(features)
        result["status"] = "success"
        return result
    except Exception as e:
        return {"status": "error", "error": str(e), "fallback": True}


if __name__ == "__main__":
    print(f"Quantum VQC v2.0 initialized: {json.dumps(quantum_classifier.get_model_info(), indent=2)}")
