#!/usr/bin/env python3
"""
Quantum Feature Maps and Embeddings
Demonstrates different encoding strategies for classical data into quantum states
"""

import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector
import json
import sys

class QuantumFeatureMap:
    """Collection of quantum feature map encodings"""
    
    @staticmethod
    def angle_encoding(x, n_qubits=None):
        """
        Angle Encoding: Encode each feature as rotation angle
        x_i → RY(x_i) on qubit i
        """
        if n_qubits is None:
            n_qubits = len(x)
        
        qc = QuantumCircuit(n_qubits, name='AngleEncoding')
        for i in range(min(len(x), n_qubits)):
            qc.ry(x[i], i)
        
        return qc
    
    @staticmethod
    def amplitude_encoding(x, n_qubits=None):
        """
        Amplitude Encoding: Encode data in amplitudes of quantum state
        Requires: len(x) = 2^n_qubits and ||x|| = 1
        """
        # Normalize
        x_norm = np.array(x) / np.linalg.norm(x)
        
        # Pad to 2^n_qubits
        if n_qubits is None:
            n_qubits = int(np.ceil(np.log2(len(x_norm))))
        
        target_size = 2**n_qubits
        if len(x_norm) < target_size:
            x_norm = np.pad(x_norm, (0, target_size - len(x_norm)))
        
        qc = QuantumCircuit(n_qubits, name='AmplitudeEncoding')
        qc.initialize(x_norm, range(n_qubits))
        
        return qc
    
    @staticmethod
    def iqp_encoding(x, n_qubits=None, reps=1):
        """
        IQP (Instantaneous Quantum Polynomial) Encoding
        Creates highly expressive feature map with entanglement
        """
        if n_qubits is None:
            n_qubits = len(x)
        
        qc = QuantumCircuit(n_qubits, name='IQPEncoding')
        
        for rep in range(reps):
            # Hadamard layer
            for i in range(n_qubits):
                qc.h(i)
            
            # Rotation layer
            for i in range(n_qubits):
                qc.ry(x[i % len(x)], i)
            
            # Entangling layer
            for i in range(n_qubits - 1):
                qc.cx(i, i + 1)
            
            # Final rotations
            for i in range(n_qubits):
                qc.ry(x[(i + 1) % len(x)], i)
        
        return qc
    
    @staticmethod
    def zz_feature_map(x, n_qubits=None, reps=1):
        """
        ZZ Feature Map: Encodes features using ZZ interactions
        Useful for classification tasks
        """
        if n_qubits is None:
            n_qubits = len(x)
        
        qc = QuantumCircuit(n_qubits, name='ZZFeatureMap')
        
        for rep in range(reps):
            # Single qubit rotations
            for i in range(n_qubits):
                qc.ry(x[i % len(x)], i)
            
            # ZZ interactions
            for i in range(n_qubits - 1):
                qc.rzz(x[i] * x[i + 1], i, i + 1)
        
        return qc
    
    @staticmethod
    def basis_encoding(x, n_qubits=None):
        """
        Basis Encoding: Encode binary data directly in computational basis
        x_i ∈ {0, 1} → |x_0 x_1 ... x_n⟩
        """
        if n_qubits is None:
            n_qubits = len(x)
        
        qc = QuantumCircuit(n_qubits, name='BasisEncoding')
        
        for i in range(min(len(x), n_qubits)):
            if x[i] > 0.5:  # Threshold at 0.5
                qc.x(i)
        
        return qc


class FeatureMapAnalyzer:
    """Analyze and compare feature maps"""
    
    def __init__(self):
        self.simulator = AerSimulator(method='statevector')
    
    def get_statevector(self, qc):
        """Get statevector of circuit"""
        job = self.simulator.run(qc)
        result = job.result()
        return result.get_statevector(qc)
    
    def compute_kernel(self, qc1, qc2):
        """Compute kernel K(qc1, qc2) = |<ψ1|ψ2>|^2"""
        sv1 = self.get_statevector(qc1)
        sv2 = self.get_statevector(qc2)
        
        # Inner product
        inner_product = np.abs(np.dot(sv1.conj(), sv2))**2
        
        return inner_product
    
    def analyze_encoding(self, encoding_name, x, n_qubits=2):
        """Analyze a specific encoding"""
        print(f"\n=== {encoding_name} ===")
        print(f"Input: {x}")
        print(f"Qubits: {n_qubits}\n")
        
        if encoding_name == 'Angle':
            qc = QuantumFeatureMap.angle_encoding(x, n_qubits)
        elif encoding_name == 'Amplitude':
            qc = QuantumFeatureMap.amplitude_encoding(x, n_qubits)
        elif encoding_name == 'IQP':
            qc = QuantumFeatureMap.iqp_encoding(x, n_qubits)
        elif encoding_name == 'ZZ':
            qc = QuantumFeatureMap.zz_feature_map(x, n_qubits)
        elif encoding_name == 'Basis':
            qc = QuantumFeatureMap.basis_encoding(x, n_qubits)
        else:
            return
        
        print("Circuit:")
        print(qc)
        
        # Get statevector
        sv = self.get_statevector(qc)
        print(f"\nStatevector (first 5 amplitudes):")
        for i, amp in enumerate(sv[:5]):
            print(f"  |{i:0{n_qubits}b}⟩: {amp:.4f}")
        
        print(f"\nStatevector norm: {np.linalg.norm(sv):.4f}")


def main():
    if len(sys.argv) < 2:
        print("Usage: quantum_embeddings.py <mode> [args]")
        print("Modes: compare, analyze, kernel_matrix")
        sys.exit(1)
    
    mode = sys.argv[1]
    analyzer = FeatureMapAnalyzer()
    
    if mode == 'compare':
        print("=== Comparing Feature Map Encodings ===\n")
        
        x = np.array([0.5, 1.0])
        n_qubits = 2
        
        encodings = ['Angle', 'Amplitude', 'IQP', 'ZZ', 'Basis']
        
        for encoding in encodings:
            analyzer.analyze_encoding(encoding, x, n_qubits)
    
    elif mode == 'analyze':
        encoding = sys.argv[2] if len(sys.argv) > 2 else 'Angle'
        x = np.array([0.5, 1.0, 0.3])
        n_qubits = 3
        
        analyzer.analyze_encoding(encoding, x, n_qubits)
    
    elif mode == 'kernel_matrix':
        print("=== Kernel Matrix Comparison ===\n")
        
        # Generate dataset
        np.random.seed(42)
        X = np.array([
            [0.5, 0.5],
            [0.5, 0.5],
            [2.0, 2.0],
            [2.0, 2.0]
        ])
        
        encodings = ['Angle', 'IQP', 'ZZ']
        
        for encoding_name in encodings:
            print(f"\n{encoding_name} Encoding Kernel Matrix:")
            
            circuits = []
            if encoding_name == 'Angle':
                circuits = [QuantumFeatureMap.angle_encoding(x, 2) for x in X]
            elif encoding_name == 'IQP':
                circuits = [QuantumFeatureMap.iqp_encoding(x, 2) for x in X]
            elif encoding_name == 'ZZ':
                circuits = [QuantumFeatureMap.zz_feature_map(x, 2) for x in X]
            
            K = np.zeros((len(X), len(X)))
            for i in range(len(X)):
                for j in range(i, len(X)):
                    K[i, j] = analyzer.compute_kernel(circuits[i], circuits[j])
                    K[j, i] = K[i, j]
            
            print(K)
            print(f"Diagonal: {np.diag(K)}")
    
    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)


if __name__ == "__main__":
    main()
