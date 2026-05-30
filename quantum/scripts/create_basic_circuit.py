#!/usr/bin/env python3
"""
Basic Qiskit Circuit Creation Script
Creates fundamental quantum circuits for learning and prototyping.
"""

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
import json
import sys

def create_bell_state(num_qubits=2):
    """Create a Bell state (entangled state)."""
    qc = QuantumCircuit(num_qubits, num_qubits, name="Bell State")
    qc.h(0)
    for i in range(1, num_qubits):
        qc.cx(0, i)
    qc.measure(range(num_qubits), range(num_qubits))
    return qc

def create_grover_oracle(n_qubits, marked_state):
    """Create a simple Grover's algorithm oracle."""
    qc = QuantumCircuit(n_qubits, name="Grover Oracle")
    
    # Mark the target state with a phase flip
    for i, bit in enumerate(bin(marked_state)[2:].zfill(n_qubits)):
        if bit == '0':
            qc.x(i)
    
    # Multi-controlled Z gate
    if n_qubits > 1:
        qc.h(n_qubits - 1)
        qc.mct(list(range(n_qubits - 1)), n_qubits - 1)
        qc.h(n_qubits - 1)
    
    for i, bit in enumerate(bin(marked_state)[2:].zfill(n_qubits)):
        if bit == '0':
            qc.x(i)
    
    return qc

def create_superposition(num_qubits):
    """Create equal superposition of all basis states."""
    qc = QuantumCircuit(num_qubits, num_qubits, name="Superposition")
    for i in range(num_qubits):
        qc.h(i)
    qc.measure(range(num_qubits), range(num_qubits))
    return qc

def simulate_circuit(qc, shots=1024):
    """Simulate a quantum circuit and return measurement results."""
    simulator = AerSimulator()
    job = simulator.run(qc, shots=shots)
    result = job.result()
    counts = result.get_counts(qc)
    return counts

def main():
    if len(sys.argv) < 2:
        print("Usage: create_basic_circuit.py <circuit_type> [args]")
        print("Supported types: bell, superposition, grover")
        sys.exit(1)
    
    circuit_type = sys.argv[1]
    
    if circuit_type == "bell":
        num_qubits = int(sys.argv[2]) if len(sys.argv) > 2 else 2
        qc = create_bell_state(num_qubits)
    elif circuit_type == "superposition":
        num_qubits = int(sys.argv[2]) if len(sys.argv) > 2 else 3
        qc = create_superposition(num_qubits)
    elif circuit_type == "grover":
        n_qubits = int(sys.argv[2]) if len(sys.argv) > 2 else 3
        marked = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        qc = create_grover_oracle(n_qubits, marked)
    else:
        print(f"Unknown circuit type: {circuit_type}")
        sys.exit(1)
    
    # Print circuit
    print(f"Circuit: {qc.name}")
    print(qc)
    
    # Simulate if measurement gates present
    if any(instr.name == 'measure' for instr, _, _ in qc.data):
        print("\nSimulation Results (1024 shots):")
        counts = simulate_circuit(qc)
        print(json.dumps(counts, indent=2))

if __name__ == "__main__":
    main()
