# Quantum Algorithms Reference

## Fundamental Algorithms

### Deutsch-Jozsa Algorithm
**Purpose**: Determine if a function is constant or balanced with a single query.

**Qubits Required**: n + 1 (n input qubits + 1 ancilla)

**Key Steps**:
1. Initialize n+1 qubits in |0⟩
2. Apply Hadamard to all qubits
3. Apply oracle U_f
4. Apply Hadamard to first n qubits
5. Measure first n qubits

**Classical vs Quantum**: Requires 2^(n-1)+1 classical queries vs 1 quantum query

---

### Grover's Algorithm
**Purpose**: Search unsorted database in O(√N) time.

**Qubits Required**: log₂(N) + 1 (where N is database size)

**Key Components**:
- Oracle: Marks target state with phase flip
- Diffusion operator: Amplifies amplitude of marked state
- Iteration count: ≈ π/4 × √N

**Complexity**: O(√N) queries vs O(N) classical

---

### Shor's Algorithm
**Purpose**: Factor large integers in polynomial time.

**Qubits Required**: 2n + 3 (where n is number of bits in integer)

**Key Phases**:
1. Classical: Reduce factoring to order-finding
2. Quantum: Find order using quantum period-finding
3. Classical: Extract factors from order

**Significance**: Breaks RSA encryption; demonstrates quantum advantage

---

### Variational Quantum Eigensolver (VQE)
**Purpose**: Find ground state energy of quantum systems.

**Approach**: Hybrid classical-quantum algorithm

**Steps**:
1. Prepare parameterized quantum circuit (ansatz)
2. Measure expectation value ⟨ψ|H|ψ⟩
3. Classical optimizer adjusts parameters
4. Repeat until convergence

**Applications**: Chemistry, materials science, optimization

---

### Quantum Approximate Optimization Algorithm (QAOA)
**Purpose**: Solve combinatorial optimization problems.

**Structure**:
- Problem Hamiltonian: Encodes objective function
- Mixer Hamiltonian: Explores solution space
- Parameterized circuit: Alternates between problem and mixer

**Applications**: MaxCut, graph coloring, scheduling

---

## Quantum Transforms

### Quantum Fourier Transform (QFT)
**Purpose**: Quantum analog of classical Fourier transform.

**Complexity**: O(n²) gates vs O(n log n) classical FFT

**Components**:
- Controlled phase rotations
- Hadamard gates
- Swap gates

**Used In**: Shor's algorithm, phase estimation

---

### Amplitude Amplification
**Purpose**: Increase probability of desired measurement outcome.

**Mechanism**: Iterative application of oracle and diffusion operator

**Generalization**: Grover's algorithm is special case with uniform superposition

---

## Quantum Error Correction

### Surface Code
**Purpose**: Protect quantum information from decoherence.

**Logical Qubits**: Encoded in 2D array of physical qubits

**Error Threshold**: ~1% physical error rate

**Overhead**: ~1000 physical qubits per logical qubit

---

### Stabilizer Codes
**Purpose**: Detect and correct errors using stabilizer operators.

**Examples**:
- Shor code: 9 qubits → 1 logical qubit
- Steane code: 7 qubits → 1 logical qubit
- Surface code: 2D lattice

---

## Quantum Machine Learning

### Quantum Neural Networks
**Architecture**: Parameterized quantum circuits with classical optimization

**Layers**:
- Data encoding layer
- Variational layer (trainable)
- Measurement/output layer

**Advantage**: Potentially exponential speedup for certain problems

---

### Quantum Support Vector Machine (QSVM)
**Purpose**: Classify data using quantum kernel methods.

**Kernel**: Computed using quantum circuit

**Advantage**: Access to high-dimensional feature space

---

## Implementation Patterns in Qiskit

### Basic Circuit Creation
```python
from qiskit import QuantumCircuit
qc = QuantumCircuit(3, 3)  # 3 qubits, 3 classical bits
qc.h(0)                     # Hadamard on qubit 0
qc.cx(0, 1)                 # CNOT: control=0, target=1
qc.measure([0,1,2], [0,1,2])
```

### Parameterized Circuits
```python
from qiskit.circuit import Parameter
theta = Parameter('θ')
qc = QuantumCircuit(1)
qc.ry(theta, 0)
```

### Custom Gates
```python
custom_gate = qc.to_gate()
larger_qc = QuantumCircuit(5)
larger_qc.append(custom_gate, [0,1,2])
```

---

## Complexity Classes

| Algorithm | Problem | Classical | Quantum | Speedup |
|-----------|---------|-----------|---------|---------|
| Deutsch-Jozsa | Function type | O(2^n) | O(1) | Exponential |
| Grover | Search | O(N) | O(√N) | Quadratic |
| Shor | Factoring | O(exp(n)) | O(n³) | Exponential |
| HHL | Linear systems | O(N³) | O(log N) | Exponential |
| VQE | Eigenvalues | O(exp(n)) | O(poly(n)) | Exponential |

---

## When to Use Each Algorithm

**Deutsch-Jozsa**: Educational; demonstrates quantum advantage for specific problem

**Grover**: Database search, constraint satisfaction problems

**Shor**: Cryptanalysis, large integer factoring

**VQE**: Chemistry simulations, ground state energy

**QAOA**: Combinatorial optimization, MaxCut problems

**Quantum ML**: Pattern recognition, classification with quantum advantage

---

## References
- Nielsen & Chuang: "Quantum Computation and Quantum Information"
- Qiskit Textbook: https://qiskit.org/textbook
- IBM Quantum Experience: https://quantum.ibm.com
