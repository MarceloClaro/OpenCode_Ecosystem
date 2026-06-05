#!/usr/bin/env python3
"""
Quantum Computing Benchmarking Script

Benchmarks quantum frameworks and circuits for performance analysis.
Supports: Qiskit, Cirq, PennyLane
"""

import time
import numpy as np
import sys
from typing import Dict, List, Tuple
import json

try:
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False

try:
    import cirq
    CIRQ_AVAILABLE = True
except ImportError:
    CIRQ_AVAILABLE = False

try:
    import pennylane as qml
    PENNYLANE_AVAILABLE = True
except ImportError:
    PENNYLANE_AVAILABLE = False


class BenchmarkSuite:
    """Comprehensive benchmarking suite for quantum computing."""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.results = {}
    
    def log(self, message: str):
        """Print log message if verbose."""
        if self.verbose:
            print(message)
    
    # ==================== Qiskit Benchmarks ====================
    
    def benchmark_qiskit_bell_state(self, n_shots: int = 1024) -> Dict:
        """Benchmark Qiskit Bell state creation and simulation."""
        if not QISKIT_AVAILABLE:
            return {"error": "Qiskit not installed"}
        
        self.log("\n[Qiskit] Benchmarking Bell state...")
        
        # Create Bell state circuit
        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure([0, 1], [0, 1])
        
        # Simulate
        simulator = AerSimulator()
        
        start_time = time.time()
        job = simulator.run(qc, shots=n_shots)
        result = job.result()
        end_time = time.time()
        
        counts = result.get_counts(qc)
        execution_time = end_time - start_time
        
        self.log(f"  Execution time: {execution_time:.4f}s")
        self.log(f"  Results: {counts}")
        
        return {
            "framework": "Qiskit",
            "circuit": "Bell state",
            "shots": n_shots,
            "execution_time": execution_time,
            "qubits": 2,
            "gates": 3
        }
    
    def benchmark_qiskit_grover(self, n_qubits: int = 3) -> Dict:
        """Benchmark Qiskit Grover's algorithm."""
        if not QISKIT_AVAILABLE:
            return {"error": "Qiskit not installed"}
        
        self.log(f"\n[Qiskit] Benchmarking Grover's algorithm ({n_qubits} qubits)...")
        
        # Create Grover circuit
        qc = QuantumCircuit(n_qubits, n_qubits)
        
        # Initialize superposition
        for i in range(n_qubits):
            qc.h(i)
        
        # Oracle (mark state |111...1⟩)
        qc.x(range(n_qubits))
        qc.h(n_qubits - 1)
        qc.mct(list(range(n_qubits - 1)), n_qubits - 1)
        qc.h(n_qubits - 1)
        qc.x(range(n_qubits))
        
        # Diffusion operator
        for i in range(n_qubits):
            qc.h(i)
        for i in range(n_qubits):
            qc.x(i)
        qc.h(n_qubits - 1)
        qc.mct(list(range(n_qubits - 1)), n_qubits - 1)
        qc.h(n_qubits - 1)
        for i in range(n_qubits):
            qc.x(i)
        for i in range(n_qubits):
            qc.h(i)
        
        qc.measure(range(n_qubits), range(n_qubits))
        
        # Simulate
        simulator = AerSimulator()
        
        start_time = time.time()
        job = simulator.run(qc, shots=1024)
        result = job.result()
        end_time = time.time()
        
        counts = result.get_counts(qc)
        execution_time = end_time - start_time
        
        self.log(f"  Execution time: {execution_time:.4f}s")
        self.log(f"  Circuit depth: {qc.depth()}")
        
        return {
            "framework": "Qiskit",
            "circuit": "Grover",
            "qubits": n_qubits,
            "depth": qc.depth(),
            "gates": qc.size(),
            "execution_time": execution_time
        }
    
    def benchmark_qiskit_vqe_ansatz(self, n_qubits: int = 2, n_layers: int = 2) -> Dict:
        """Benchmark Qiskit VQE ansatz."""
        if not QISKIT_AVAILABLE:
            return {"error": "Qiskit not installed"}
        
        self.log(f"\n[Qiskit] Benchmarking VQE ansatz ({n_qubits} qubits, {n_layers} layers)...")
        
        from qiskit.circuit import Parameter
        
        # Create parameterized circuit
        params = [Parameter(f'θ{i}') for i in range(n_qubits * n_layers)]
        qc = QuantumCircuit(n_qubits)
        
        param_idx = 0
        for layer in range(n_layers):
            for qubit in range(n_qubits):
                qc.ry(params[param_idx], qubit)
                param_idx += 1
            for qubit in range(n_qubits - 1):
                qc.cx(qubit, qubit + 1)
        
        # Bind random parameters
        param_values = {p: np.random.rand() * 2 * np.pi for p in params}
        bound_qc = qc.bind_parameters(param_values)
        
        # Simulate
        simulator = AerSimulator()
        
        start_time = time.time()
        job = simulator.run(bound_qc, shots=1024)
        result = job.result()
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        self.log(f"  Execution time: {execution_time:.4f}s")
        self.log(f"  Circuit depth: {bound_qc.depth()}")
        
        return {
            "framework": "Qiskit",
            "circuit": "VQE ansatz",
            "qubits": n_qubits,
            "layers": n_layers,
            "parameters": len(params),
            "depth": bound_qc.depth(),
            "execution_time": execution_time
        }
    
    # ==================== Cirq Benchmarks ====================
    
    def benchmark_cirq_bell_state(self, n_shots: int = 1024) -> Dict:
        """Benchmark Cirq Bell state creation and simulation."""
        if not CIRQ_AVAILABLE:
            return {"error": "Cirq not installed"}
        
        self.log("\n[Cirq] Benchmarking Bell state...")
        
        # Create Bell state circuit
        q0, q1 = cirq.LineQubit.range(2)
        circuit = cirq.Circuit(
            cirq.H(q0),
            cirq.CNOT(q0, q1),
            cirq.measure(q0, q1, key='result')
        )
        
        # Simulate
        simulator = cirq.Simulator()
        
        start_time = time.time()
        result = simulator.run(circuit, repetitions=n_shots)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        self.log(f"  Execution time: {execution_time:.4f}s")
        
        return {
            "framework": "Cirq",
            "circuit": "Bell state",
            "shots": n_shots,
            "execution_time": execution_time,
            "qubits": 2,
            "gates": 3
        }
    
    def benchmark_cirq_grover(self, n_qubits: int = 3) -> Dict:
        """Benchmark Cirq Grover's algorithm."""
        if not CIRQ_AVAILABLE:
            return {"error": "Cirq not installed"}
        
        self.log(f"\n[Cirq] Benchmarking Grover's algorithm ({n_qubits} qubits)...")
        
        qubits = cirq.LineQubit.range(n_qubits)
        circuit = cirq.Circuit()
        
        # Initialize superposition
        for q in qubits:
            circuit.append(cirq.H(q))
        
        # Oracle (mark state |111...1⟩)
        circuit.append(cirq.X(qubits))
        circuit.append(cirq.H(qubits[-1]))
        circuit.append(cirq.Z(qubits[-1]))
        circuit.append(cirq.H(qubits[-1]))
        circuit.append(cirq.X(qubits))
        
        # Diffusion operator
        for q in qubits:
            circuit.append(cirq.H(q))
        for q in qubits:
            circuit.append(cirq.X(q))
        circuit.append(cirq.H(qubits[-1]))
        circuit.append(cirq.Z(qubits[-1]))
        circuit.append(cirq.H(qubits[-1]))
        for q in qubits:
            circuit.append(cirq.X(q))
        for q in qubits:
            circuit.append(cirq.H(q))
        
        circuit.append(cirq.measure(*qubits, key='result'))
        
        # Simulate
        simulator = cirq.Simulator()
        
        start_time = time.time()
        result = simulator.run(circuit, repetitions=1024)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        self.log(f"  Execution time: {execution_time:.4f}s")
        
        return {
            "framework": "Cirq",
            "circuit": "Grover",
            "qubits": n_qubits,
            "execution_time": execution_time
        }
    
    # ==================== PennyLane Benchmarks ====================
    
    def benchmark_pennylane_bell_state(self, n_shots: int = 1024) -> Dict:
        """Benchmark PennyLane Bell state creation and simulation."""
        if not PENNYLANE_AVAILABLE:
            return {"error": "PennyLane not installed"}
        
        self.log("\n[PennyLane] Benchmarking Bell state...")
        
        dev = qml.device('default.qubit', wires=2, shots=n_shots)
        
        @qml.qnode(dev)
        def bell_state():
            qml.Hadamard(wires=0)
            qml.CNOT(wires=[0, 1])
            return qml.expval(qml.PauliZ(0)), qml.expval(qml.PauliZ(1))
        
        start_time = time.time()
        result = bell_state()
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        self.log(f"  Execution time: {execution_time:.4f}s")
        
        return {
            "framework": "PennyLane",
            "circuit": "Bell state",
            "shots": n_shots,
            "execution_time": execution_time,
            "qubits": 2
        }
    
    # ==================== Comparison & Reporting ====================
    
    def run_all_benchmarks(self) -> Dict:
        """Run all available benchmarks."""
        self.log("=" * 60)
        self.log("QUANTUM COMPUTING BENCHMARKING SUITE")
        self.log("=" * 60)
        
        benchmarks = []
        
        # Qiskit benchmarks
        if QISKIT_AVAILABLE:
            benchmarks.append(self.benchmark_qiskit_bell_state())
            benchmarks.append(self.benchmark_qiskit_grover(n_qubits=3))
            benchmarks.append(self.benchmark_qiskit_vqe_ansatz(n_qubits=2, n_layers=2))
        
        # Cirq benchmarks
        if CIRQ_AVAILABLE:
            benchmarks.append(self.benchmark_cirq_bell_state())
            benchmarks.append(self.benchmark_cirq_grover(n_qubits=3))
        
        # PennyLane benchmarks
        if PENNYLANE_AVAILABLE:
            benchmarks.append(self.benchmark_pennylane_bell_state())
        
        self.results = benchmarks
        self.print_summary()
        
        return benchmarks
    
    def print_summary(self):
        """Print benchmark summary."""
        self.log("\n" + "=" * 60)
        self.log("BENCHMARK SUMMARY")
        self.log("=" * 60)
        
        if not self.results:
            self.log("No benchmarks completed.")
            return
        
        # Group by framework
        by_framework = {}
        for result in self.results:
            if "error" in result:
                continue
            fw = result["framework"]
            if fw not in by_framework:
                by_framework[fw] = []
            by_framework[fw].append(result)
        
        # Print summary table
        self.log("\nExecution Times (seconds):")
        self.log("-" * 60)
        
        for framework, results in by_framework.items():
            self.log(f"\n{framework}:")
            for result in results:
                circuit = result.get("circuit", "Unknown")
                time_ms = result["execution_time"] * 1000
                self.log(f"  {circuit:20s}: {time_ms:8.2f} ms")
        
        # Overall statistics
        self.log("\n" + "-" * 60)
        self.log("Overall Statistics:")
        
        times = [r["execution_time"] for r in self.results if "error" not in r]
        if times:
            self.log(f"  Average time: {np.mean(times)*1000:.2f} ms")
            self.log(f"  Min time: {np.min(times)*1000:.2f} ms")
            self.log(f"  Max time: {np.max(times)*1000:.2f} ms")
    
    def export_json(self, filename: str = "benchmark_results.json"):
        """Export results to JSON."""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        self.log(f"\nResults exported to {filename}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Quantum Computing Benchmarking Suite")
    parser.add_argument("--all", action="store_true", help="Run all benchmarks")
    parser.add_argument("--qiskit", action="store_true", help="Run Qiskit benchmarks")
    parser.add_argument("--cirq", action="store_true", help="Run Cirq benchmarks")
    parser.add_argument("--pennylane", action="store_true", help="Run PennyLane benchmarks")
    parser.add_argument("--export", type=str, help="Export results to JSON file")
    parser.add_argument("--quiet", action="store_true", help="Suppress output")
    
    args = parser.parse_args()
    
    # Default to all if no specific framework selected
    if not (args.qiskit or args.cirq or args.pennylane):
        args.all = True
    
    suite = BenchmarkSuite(verbose=not args.quiet)
    
    if args.all:
        suite.run_all_benchmarks()
    else:
        if args.qiskit and QISKIT_AVAILABLE:
            suite.benchmark_qiskit_bell_state()
            suite.benchmark_qiskit_grover()
            suite.benchmark_qiskit_vqe_ansatz()
        if args.cirq and CIRQ_AVAILABLE:
            suite.benchmark_cirq_bell_state()
            suite.benchmark_cirq_grover()
        if args.pennylane and PENNYLANE_AVAILABLE:
            suite.benchmark_pennylane_bell_state()
        
        suite.print_summary()
    
    if args.export:
        suite.export_json(args.export)


if __name__ == "__main__":
    main()
