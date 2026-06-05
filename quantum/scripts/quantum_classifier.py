#!/usr/bin/env python3
"""
Quantum Machine Learning Classifier
Implements Quantum Support Vector Machine (QSVM) and Quantum Neural Networks (QNN)
"""

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit import ParameterVector, Parameter
from qiskit_aer import AerSimulator
from qiskit.primitives import Sampler, Estimator
from qiskit.quantum_info import Statevector
import json
import sys

class QuantumKernel:
    """Compute quantum kernel for QSVM"""
    
    def __init__(self, n_qubits=2, feature_map='angle'):
        self.n_qubits = n_qubits
        self.feature_map = feature_map
        self.simulator = AerSimulator()
    
    def create_feature_map(self, x):
        """Create feature map circuit for input data point x"""
        qc = QuantumCircuit(self.n_qubits, name='FeatureMap')
        
        if self.feature_map == 'angle':
            # Angle encoding: RY rotations based on features
            for i, xi in enumerate(x[:self.n_qubits]):
                qc.ry(xi, i)
        
        elif self.feature_map == 'amplitude':
            # Amplitude encoding: encode in amplitudes
            # Normalize data
            x_norm = x / np.linalg.norm(x)
            # Create state vector
            statevector = np.zeros(2**self.n_qubits)
            for i, val in enumerate(x_norm[:min(len(x_norm), 2**self.n_qubits)]):
                statevector[i] = val
            statevector = statevector / np.linalg.norm(statevector)
            qc = QuantumCircuit(self.n_qubits)
            qc.initialize(statevector, range(self.n_qubits))
        
        elif self.feature_map == 'iqp':
            # IQP (Instantaneous Quantum Polynomial) encoding
            for i in range(self.n_qubits):
                qc.h(i)
                qc.ry(x[i % len(x)], i)
            
            for i in range(self.n_qubits - 1):
                qc.cx(i, i + 1)
                qc.ry(x[(i + 1) % len(x)], i + 1)
        
        return qc
    
    def compute_kernel(self, x1, x2):
        """Compute kernel value K(x1, x2) = |<x1|x2>|^2"""
        # Create circuit: U(x1)† U(x2)
        qc = QuantumCircuit(self.n_qubits)
        
        # Apply feature map for x2
        fm_x2 = self.create_feature_map(x2)
        qc.append(fm_x2, range(self.n_qubits))
        
        # Apply inverse of feature map for x1
        fm_x1 = self.create_feature_map(x1)
        qc_inv = fm_x1.inverse()
        qc.append(qc_inv, range(self.n_qubits))
        
        # Measure probability of |0...0⟩ state
        qc.measure_all()
        
        job = self.simulator.run(qc, shots=1024)
        result = job.result()
        counts = result.get_counts(qc)
        
        # Kernel value is probability of measuring all zeros
        all_zeros = '0' * self.n_qubits
        kernel_value = counts.get(all_zeros, 0) / 1024
        
        return kernel_value
    
    def compute_kernel_matrix(self, X):
        """Compute kernel matrix for dataset X"""
        n_samples = len(X)
        K = np.zeros((n_samples, n_samples))
        
        for i in range(n_samples):
            for j in range(i, n_samples):
                K[i, j] = self.compute_kernel(X[i], X[j])
                K[j, i] = K[i, j]
        
        return K


class QuantumNeuralNetwork:
    """Quantum Neural Network for classification"""
    
    def __init__(self, n_qubits=2, n_layers=2):
        self.n_qubits = n_qubits
        self.n_layers = n_layers
        self.simulator = AerSimulator()
        self.params = None
    
    def create_ansatz(self, params):
        """Create parameterized quantum circuit (ansatz)"""
        qc = QuantumCircuit(self.n_qubits, name='QNN_Ansatz')
        
        param_idx = 0
        for layer in range(self.n_layers):
            # RY rotations
            for i in range(self.n_qubits):
                qc.ry(params[param_idx], i)
                param_idx += 1
            
            # Entangling layer (CNOT ladder)
            for i in range(self.n_qubits - 1):
                qc.cx(i, i + 1)
            
            # RZ rotations
            for i in range(self.n_qubits):
                qc.rz(params[param_idx], i)
                param_idx += 1
        
        return qc
    
    def create_circuit(self, x, params):
        """Create full circuit: feature map + ansatz + measurement"""
        qc = QuantumCircuit(self.n_qubits, 1, name='QNN')
        
        # Feature encoding
        for i, xi in enumerate(x[:self.n_qubits]):
            qc.ry(xi, i)
        
        # Ansatz
        ansatz = self.create_ansatz(params)
        qc.append(ansatz, range(self.n_qubits))
        
        # Measurement of first qubit
        qc.measure(0, 0)
        
        return qc
    
    def predict(self, x, params):
        """Predict output for input x"""
        qc = self.create_circuit(x, params)
        
        job = self.simulator.run(qc, shots=1024)
        result = job.result()
        counts = result.get_counts(qc)
        
        # Probability of measuring |1⟩
        prob_1 = counts.get('1', 0) / 1024
        
        return prob_1
    
    def initialize_params(self):
        """Initialize random parameters"""
        n_params = self.n_layers * 2 * self.n_qubits
        self.params = np.random.uniform(0, 2*np.pi, n_params)
        return self.params


def main():
    if len(sys.argv) < 2:
        print("Usage: quantum_classifier.py <mode> [args]")
        print("Modes: qsvm, qnn, kernel_demo")
        sys.exit(1)
    
    mode = sys.argv[1]
    
    if mode == 'qsvm':
        print("=== Quantum Support Vector Machine (QSVM) ===\n")
        
        # Generate simple dataset
        np.random.seed(42)
        n_samples = 4
        n_features = 2
        X = np.random.uniform(-np.pi, np.pi, (n_samples, n_features))
        
        print(f"Dataset shape: {X.shape}")
        print(f"Sample data:\n{X}\n")
        
        # Compute kernel matrix
        qkernel = QuantumKernel(n_qubits=2, feature_map='angle')
        print("Computing quantum kernel matrix...")
        K = qkernel.compute_kernel_matrix(X)
        
        print("\nQuantum Kernel Matrix:")
        print(K)
        print("\nKernel properties:")
        print(f"  - Symmetric: {np.allclose(K, K.T)}")
        print(f"  - Diagonal: {np.allclose(np.diag(np.diag(K)), K)}")
        print(f"  - Trace: {np.trace(K):.4f}")
    
    elif mode == 'qnn':
        print("=== Quantum Neural Network (QNN) ===\n")
        
        # Create QNN
        qnn = QuantumNeuralNetwork(n_qubits=2, n_layers=2)
        params = qnn.initialize_params()
        
        print(f"QNN initialized with {len(params)} parameters")
        print(f"Parameters: {params}\n")
        
        # Test predictions
        test_inputs = [
            np.array([0.5, 0.5]),
            np.array([1.0, 1.0]),
            np.array([2.0, 0.5])
        ]
        
        print("Predictions:")
        for x in test_inputs:
            pred = qnn.predict(x, params)
            print(f"  Input {x} → Output: {pred:.4f}")
    
    elif mode == 'kernel_demo':
        print("=== Quantum Kernel Computation ===\n")
        
        # Simple demo
        qkernel = QuantumKernel(n_qubits=2, feature_map='angle')
        
        x1 = np.array([0.5, 0.5])
        x2 = np.array([0.5, 0.5])
        x3 = np.array([2.0, 2.0])
        
        print(f"Computing kernels...")
        k11 = qkernel.compute_kernel(x1, x1)
        k12 = qkernel.compute_kernel(x1, x2)
        k13 = qkernel.compute_kernel(x1, x3)
        
        print(f"K(x1, x1) = {k11:.4f}")
        print(f"K(x1, x2) = {k12:.4f}")
        print(f"K(x1, x3) = {k13:.4f}")
        
        print("\nObservations:")
        print(f"  - K(x1, x1) should be 1.0 (or close)")
        print(f"  - K(x1, x2) = K(x1, x1) since x1 == x2")
        print(f"  - K(x1, x3) should be smaller (different inputs)")
    
    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)


if __name__ == "__main__":
    main()
