#!/usr/bin/env python3
"""
Qiskit Circuit Optimization Script
Optimizes quantum circuits for execution on real hardware.
"""

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import Optimize1qGates, CommutativeCancellation
import json
import sys

def optimize_circuit(qc, optimization_level=2):
    """
    Optimize a quantum circuit for execution.
    
    optimization_level:
    - 0: No optimization
    - 1: Light optimization
    - 2: Medium optimization (default)
    - 3: Heavy optimization
    """
    simulator = AerSimulator()
    optimized = transpile(qc, simulator, optimization_level=optimization_level)
    return optimized

def analyze_circuit(qc):
    """Analyze circuit properties."""
    analysis = {
        "num_qubits": qc.num_qubits,
        "num_clbits": qc.num_clbits,
        "depth": qc.depth(),
        "size": qc.size(),
        "gate_counts": dict(qc.count_ops()),
        "two_qubit_gates": sum(1 for instr, _, _ in qc.data if len(instr.qargs) == 2)
    }
    return analysis

def compare_circuits(original, optimized):
    """Compare original and optimized circuits."""
    orig_analysis = analyze_circuit(original)
    opt_analysis = analyze_circuit(optimized)
    
    comparison = {
        "original": orig_analysis,
        "optimized": opt_analysis,
        "improvements": {
            "depth_reduction": f"{((1 - opt_analysis['depth']/orig_analysis['depth'])*100):.1f}%" if orig_analysis['depth'] > 0 else "N/A",
            "size_reduction": f"{((1 - opt_analysis['size']/orig_analysis['size'])*100):.1f}%" if orig_analysis['size'] > 0 else "N/A",
            "gate_reduction": f"{((1 - sum(opt_analysis['gate_counts'].values())/sum(orig_analysis['gate_counts'].values()))*100):.1f}%" if sum(orig_analysis['gate_counts'].values()) > 0 else "N/A"
        }
    }
    return comparison

def main():
    if len(sys.argv) < 2:
        print("Usage: optimize_circuit.py <circuit_file> [optimization_level]")
        sys.exit(1)
    
    circuit_file = sys.argv[1]
    opt_level = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    
    # Load circuit from QASM or pickle
    try:
        if circuit_file.endswith('.qasm'):
            qc = QuantumCircuit.from_qasm_file(circuit_file)
        else:
            import pickle
            with open(circuit_file, 'rb') as f:
                qc = pickle.load(f)
    except FileNotFoundError:
        print(f"Circuit file not found: {circuit_file}")
        sys.exit(1)
    
    print(f"Original Circuit:")
    print(qc)
    
    # Optimize
    optimized_qc = optimize_circuit(qc, opt_level)
    
    print(f"\nOptimized Circuit (Level {opt_level}):")
    print(optimized_qc)
    
    # Compare
    comparison = compare_circuits(qc, optimized_qc)
    print(f"\nOptimization Results:")
    print(json.dumps(comparison, indent=2))

if __name__ == "__main__":
    main()
