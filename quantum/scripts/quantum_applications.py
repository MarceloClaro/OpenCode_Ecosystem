#!/usr/bin/env python3
"""
Quantum Applications
Practical examples in Chemistry, Finance, and Optimization
"""

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit import Parameter, ParameterVector
from qiskit_aer import AerSimulator
import sys
import json

class QuantumChemistry:
    """Quantum chemistry applications"""
    
    @staticmethod
    def h2_molecule():
        """
        Simulate H2 molecule ground state using VQE ansatz
        Simple example of quantum chemistry
        """
        print("=== H2 Molecule Ground State ===\n")
        
        # Create ansatz for H2
        n_qubits = 2
        qc = QuantumCircuit(n_qubits, name='H2_Ansatz')
        
        # Prepare initial state (Hartree-Fock)
        qc.x(0)  # Put qubit 0 in |1⟩
        
        # Variational layer
        theta = Parameter('θ')
        qc.ry(theta, 0)
        qc.cx(0, 1)
        qc.ry(theta, 1)
        
        print("H2 Ansatz Circuit:")
        print(qc)
        
        # Bind parameter for simulation
        bound_qc = qc.bind_parameters({theta: 0.5})
        
        # Simulate
        simulator = AerSimulator(method='statevector')
        job = simulator.run(bound_qc)
        result = job.result()
        statevector = result.get_statevector(bound_qc)
        
        print(f"\nStatevector: {statevector}")
        print(f"Probabilities: {np.abs(statevector)**2}")
        
        return qc
    
    @staticmethod
    def molecular_hamiltonian():
        """
        Describe molecular Hamiltonian for quantum simulation
        H = Σ h_ij Z_i Z_j + Σ h_i Z_i
        """
        print("\n=== Molecular Hamiltonian ===\n")
        
        # Example: H2 molecule Hamiltonian (simplified)
        # H = -1.05 Z_0 Z_1 + 0.39 Z_0 + 0.39 Z_1 - 0.01 X_0 X_1
        
        hamiltonian = {
            'ZZ_terms': [(-1.05, (0, 1))],  # Z_0 Z_1 coefficient
            'Z_terms': [(0.39, 0), (0.39, 1)],  # Z_i coefficients
            'XX_terms': [(-0.01, (0, 1))]  # X_0 X_1 coefficient
        }
        
        print("H2 Hamiltonian:")
        print("H = -1.05 Z₀Z₁ + 0.39 Z₀ + 0.39 Z₁ - 0.01 X₀X₁\n")
        
        print("Hamiltonian structure:")
        print(json.dumps(hamiltonian, indent=2))
        
        return hamiltonian


class QuantumFinance:
    """Quantum finance applications"""
    
    @staticmethod
    def option_pricing():
        """
        Quantum amplitude estimation for option pricing
        Estimate probability of stock price exceeding strike price
        """
        print("\n=== Quantum Option Pricing ===\n")
        
        # Create circuit for option pricing
        n_qubits = 3
        qc = QuantumCircuit(n_qubits, n_qubits, name='OptionPricing')
        
        # Encode stock price distribution
        # Assume uniform distribution over 3 qubits
        for i in range(n_qubits):
            qc.h(i)
        
        # Oracle: Mark states where price > strike
        # Example: Mark states |101⟩, |110⟩, |111⟩ (prices 5, 6, 7)
        # This is a simplified oracle
        for i in range(n_qubits):
            qc.z(i)
        
        qc.measure(range(n_qubits), range(n_qubits))
        
        print("Option Pricing Circuit:")
        print(qc)
        
        # Simulate
        simulator = AerSimulator()
        job = simulator.run(qc, shots=1024)
        result = job.result()
        counts = result.get_counts(qc)
        
        print("\nMeasurement Results (1024 shots):")
        print(json.dumps(counts, indent=2))
        
        # Calculate probability
        favorable_outcomes = sum(v for k, v in counts.items() if k.count('1') >= 2)
        probability = favorable_outcomes / 1024
        print(f"\nProbability (price > strike): {probability:.4f}")
        
        return qc
    
    @staticmethod
    def portfolio_optimization():
        """
        Quantum portfolio optimization using QAOA
        Maximize return while minimizing risk
        """
        print("\n=== Quantum Portfolio Optimization ===\n")
        
        # Portfolio: 3 assets
        n_assets = 3
        qc = QuantumCircuit(n_assets, name='PortfolioOpt')
        
        # Initialize superposition
        for i in range(n_assets):
            qc.h(i)
        
        # Cost Hamiltonian: Maximize return
        # H_C = -0.5 Z_0 - 0.3 Z_1 - 0.4 Z_2
        gamma = Parameter('γ')
        for i in range(n_assets):
            qc.rz(2 * gamma * [0.5, 0.3, 0.4][i], i)
        
        # Mixer Hamiltonian: Explore solution space
        # H_M = X_0 + X_1 + X_2
        beta = Parameter('β')
        for i in range(n_assets):
            qc.rx(2 * beta, i)
        
        print("Portfolio Optimization Circuit (QAOA):")
        print(qc)
        
        print("\nAsset Weights: [0.5, 0.3, 0.4]")
        print("Objective: Maximize weighted return")
        
        return qc


class QuantumOptimization:
    """Quantum optimization applications"""
    
    @staticmethod
    def maxcut_problem():
        """
        MaxCut problem: Partition graph vertices to maximize edge cuts
        Classic QAOA application
        """
        print("\n=== MaxCut Problem (QAOA) ===\n")
        
        # Graph: 4 vertices, edges: (0,1), (1,2), (2,3), (3,0), (0,2)
        n_qubits = 4
        edges = [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)]
        
        print("Graph:")
        print("Vertices: 0, 1, 2, 3")
        print(f"Edges: {edges}")
        print("Objective: Partition vertices to maximize edge cuts\n")
        
        # QAOA circuit
        qc = QuantumCircuit(n_qubits, name='MaxCut')
        
        # Initial superposition
        for i in range(n_qubits):
            qc.h(i)
        
        # Cost Hamiltonian (p=1 layer)
        gamma = Parameter('γ')
        for u, v in edges:
            qc.rzz(2 * gamma, u, v)
        
        # Mixer Hamiltonian
        beta = Parameter('β')
        for i in range(n_qubits):
            qc.rx(2 * beta, i)
        
        print("QAOA Circuit (p=1):")
        print(qc)
        
        # Optimal parameters (approximate)
        print("\nOptimal parameters (approximate):")
        print(f"γ ≈ 0.628 (cost angle)")
        print(f"β ≈ 0.785 (mixer angle)")
        
        return qc
    
    @staticmethod
    def traveling_salesman():
        """
        Traveling Salesman Problem (TSP) using quantum annealing concept
        Find shortest route visiting all cities
        """
        print("\n=== Traveling Salesman Problem ===\n")
        
        # 4 cities
        n_cities = 4
        n_qubits = n_cities * n_cities  # Binary encoding
        
        print(f"Problem: Find shortest route for {n_cities} cities")
        print(f"Qubits needed: {n_qubits} (binary encoding)")
        print(f"Classical complexity: O({n_cities}!)")
        print(f"Quantum advantage: Potential exponential speedup\n")
        
        # Distance matrix (example)
        distances = np.array([
            [0, 10, 15, 20],
            [10, 0, 35, 25],
            [15, 35, 0, 30],
            [20, 25, 30, 0]
        ])
        
        print("Distance Matrix:")
        print(distances)
        
        # Classical solution (brute force for small instance)
        from itertools import permutations
        
        min_distance = float('inf')
        best_route = None
        
        for perm in permutations(range(1, n_cities)):
            route = [0] + list(perm) + [0]
            distance = sum(distances[route[i], route[i+1]] for i in range(len(route)-1))
            if distance < min_distance:
                min_distance = distance
                best_route = route
        
        print(f"\nClassical Solution:")
        print(f"Best route: {best_route}")
        print(f"Total distance: {min_distance}")
        
        return distances


class QuantumMachineLearning:
    """Quantum machine learning applications"""
    
    @staticmethod
    def quantum_classifier_demo():
        """
        Quantum classifier for binary classification
        Using feature map + variational ansatz
        """
        print("\n=== Quantum Binary Classifier ===\n")
        
        # Create classifier circuit
        n_qubits = 2
        qc = QuantumCircuit(n_qubits, 1, name='QuantumClassifier')
        
        # Feature encoding (example: x = [0.5, 0.3])
        x = [0.5, 0.3]
        for i, xi in enumerate(x):
            qc.ry(xi, i)
        
        # Variational ansatz
        theta = Parameter('θ')
        qc.ry(theta, 0)
        qc.cx(0, 1)
        qc.ry(theta, 1)
        
        # Measurement
        qc.measure(0, 0)
        
        print("Quantum Classifier Circuit:")
        print(qc)
        
        print("\nFeature encoding: x = [0.5, 0.3]")
        print("Ansatz: Parameterized RY-CNOT-RY")
        print("Output: Probability of measuring |1⟩")
        
        # Simulate for different parameter values
        simulator = AerSimulator()
        
        print("\nPredictions for different parameters:")
        for theta_val in [0, np.pi/4, np.pi/2, 3*np.pi/4, np.pi]:
            bound_qc = qc.bind_parameters({theta: theta_val})
            job = simulator.run(bound_qc, shots=1024)
            result = job.result()
            counts = result.get_counts(bound_qc)
            prob_1 = counts.get('1', 0) / 1024
            print(f"  θ = {theta_val:.4f}: P(|1⟩) = {prob_1:.4f}")
        
        return qc


def main():
    if len(sys.argv) < 2:
        print("Usage: quantum_applications.py <domain>")
        print("Domains: chemistry, finance, optimization, ml, all")
        sys.exit(1)
    
    domain = sys.argv[1]
    
    if domain == 'chemistry':
        QuantumChemistry.h2_molecule()
        QuantumChemistry.molecular_hamiltonian()
    
    elif domain == 'finance':
        QuantumFinance.option_pricing()
        QuantumFinance.portfolio_optimization()
    
    elif domain == 'optimization':
        QuantumOptimization.maxcut_problem()
        QuantumOptimization.traveling_salesman()
    
    elif domain == 'ml':
        QuantumMachineLearning.quantum_classifier_demo()
    
    elif domain == 'all':
        print("=" * 60)
        print("QUANTUM APPLICATIONS ACROSS DOMAINS")
        print("=" * 60)
        
        print("\n1. CHEMISTRY")
        print("-" * 60)
        QuantumChemistry.h2_molecule()
        QuantumChemistry.molecular_hamiltonian()
        
        print("\n2. FINANCE")
        print("-" * 60)
        QuantumFinance.option_pricing()
        QuantumFinance.portfolio_optimization()
        
        print("\n3. OPTIMIZATION")
        print("-" * 60)
        QuantumOptimization.maxcut_problem()
        QuantumOptimization.traveling_salesman()
        
        print("\n4. MACHINE LEARNING")
        print("-" * 60)
        QuantumMachineLearning.quantum_classifier_demo()
    
    else:
        print(f"Unknown domain: {domain}")
        sys.exit(1)


if __name__ == "__main__":
    main()
