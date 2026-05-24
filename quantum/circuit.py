#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quantum Circuit — Circuitos Puros (sem DI)
=============================================
Separado do QuantumVQC para responsabilidade unica.
Contem apenas logica de circuito quantico (encode, ansatz, forward).
Nao tem dependencia com core/ ou Container.
"""

from __future__ import annotations
import numpy as np
from typing import List, Tuple, Optional
import pennylane as qml


class QuantumCircuit:
    """Circuito quantico puro — sem estado, sem DI, testavel isoladamente."""

    def __init__(self, n_qubits: int = 50, n_layers: int = 6):
        self.n_qubits = n_qubits
        self.n_layers = n_layers
        self.dev = qml.device("default.qubit", wires=n_qubits)

    def encode_features(self, features: np.ndarray, wires: List[int]) -> None:
        norm = np.linalg.norm(features)
        if norm > 0:
            features = features / norm
        for i, wire in enumerate(wires[:len(features)]):
            angle = np.arcsin(np.clip(features[i], -1, 1))
            qml.RY(angle, wires=wire)

    def ansatz(self, params: np.ndarray, wires: List[int]) -> None:
        for layer in range(self.n_layers):
            for i, wire in enumerate(wires):
                if i < len(params[layer]):
                    qml.RX(params[layer][i][0], wires=wire)
                    qml.RY(params[layer][i][1], wires=wire)
                    qml.RZ(params[layer][i][2], wires=wire)
            for i in range(len(wires) - 1):
                qml.CNOT(wires=[wires[i], wires[i + 1]])
            if len(wires) > 1:
                qml.CNOT(wires=[wires[-1], wires[0]])

    @qml.qnode(device=None)
    def _circuit_qnode(self, features: np.ndarray, params: np.ndarray,
                       wires: List[int]) -> float:
        self.encode_features(features, wires)
        self.ansatz(params, wires)
        return qml.expval(qml.PauliZ(wires[0]))

    def forward(self, features: np.ndarray, params: np.ndarray,
                wires: List[int]) -> float:
        qnode = qml.QNode(self._circuit_qnode, self.dev)
        return float(qnode(features, params, wires))
