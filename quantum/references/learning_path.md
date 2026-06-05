# Quantum Computing Learning Path

Structured learning roadmap from basics to advanced quantum computing, inspired by Microsoft Quantum Katas.

## Learning Levels

### Level 1: Foundations (Beginner)
**Time**: 2-3 weeks | **Prerequisites**: None

#### 1.1 Basic Gates
Learn fundamental quantum gates and their effects.

**Topics**:
- Pauli gates (X, Y, Z)
- Hadamard gate (H)
- Phase gate (S, T)
- Measurement

**Kata-Style Exercises**:

```python
# Exercise 1.1.1: Apply X gate
# Goal: Flip qubit 0 from |0⟩ to |1⟩
from qiskit import QuantumCircuit

def apply_x_gate():
    qc = QuantumCircuit(1, 1)
    # TODO: Apply X gate to qubit 0
    qc.x(0)  # Solution
    qc.measure(0, 0)
    return qc

# Exercise 1.1.2: Create superposition
# Goal: Create equal superposition on qubit 0
def create_superposition():
    qc = QuantumCircuit(1, 1)
    # TODO: Apply H gate to qubit 0
    qc.h(0)  # Solution
    qc.measure(0, 0)
    return qc

# Exercise 1.1.3: Apply phase gate
# Goal: Apply phase gate S to qubit 0
def apply_phase_gate():
    qc = QuantumCircuit(1, 1)
    # TODO: Apply S gate to qubit 0
    qc.s(0)  # Solution
    qc.measure(0, 0)
    return qc
```

**Verification**:
```python
from qiskit_aer import AerSimulator

def verify_exercise(qc, expected_outcome):
    simulator = AerSimulator(method='statevector')
    result = simulator.run(qc).result()
    statevector = result.get_statevector(qc)
    # Check if result matches expected
    return np.allclose(statevector, expected_outcome)
```

#### 1.2 Multi-Qubit Gates
Learn entanglement and controlled operations.

**Topics**:
- CNOT (CX) gate
- Controlled-Z (CZ) gate
- SWAP gate
- Entanglement

**Kata-Style Exercises**:

```python
# Exercise 1.2.1: Create Bell state
# Goal: Create |Φ+⟩ = (|00⟩ + |11⟩)/√2
def create_bell_state():
    qc = QuantumCircuit(2, 2)
    # TODO: Create Bell state
    qc.h(0)
    qc.cx(0, 1)  # Solution
    qc.measure([0, 1], [0, 1])
    return qc

# Exercise 1.2.2: CNOT variations
# Goal: Apply CNOT with different controls/targets
def cnot_variations():
    qc = QuantumCircuit(3, 3)
    # TODO: Apply CNOT(0,1), CNOT(1,2)
    qc.cx(0, 1)
    qc.cx(1, 2)  # Solution
    qc.measure([0, 1, 2], [0, 1, 2])
    return qc
```

#### 1.3 Measurement and Collapse
Understand measurement and quantum state collapse.

**Topics**:
- Measurement basis
- State collapse
- Measurement statistics
- Partial measurement

### Level 2: Algorithms (Intermediate)
**Time**: 3-4 weeks | **Prerequisites**: Level 1

#### 2.1 Deutsch-Jozsa Algorithm
Distinguish constant from balanced functions.

**Concept**:
```
Problem: Given a function f: {0,1}ⁿ → {0,1}
- Constant: f(x) = c for all x
- Balanced: f(x) = 0 for half of inputs, 1 for other half
Determine which with minimum queries
```

**Classical**: n queries needed
**Quantum**: 1 query with Deutsch-Jozsa

**Implementation**:

```python
def deutsch_jozsa_algorithm(oracle, n_qubits):
    """
    Implement Deutsch-Jozsa algorithm
    
    Args:
        oracle: Function implementing the oracle
        n_qubits: Number of qubits
    
    Returns:
        Result: 0 if constant, 1 if balanced
    """
    qc = QuantumCircuit(n_qubits + 1, n_qubits)
    
    # Initialize ancilla to |1⟩
    qc.x(n_qubits)
    qc.h(n_qubits)
    
    # Apply Hadamard to all qubits
    for i in range(n_qubits):
        qc.h(i)
    
    # Apply oracle
    qc = qc.compose(oracle)
    
    # Apply Hadamard to input qubits
    for i in range(n_qubits):
        qc.h(i)
    
    # Measure
    qc.measure(range(n_qubits), range(n_qubits))
    
    return qc
```

#### 2.2 Grover's Algorithm
Search unsorted database.

**Concept**:
```
Problem: Find marked element in unsorted list of N items
Classical: O(N)
Quantum: O(√N)
```

**Implementation**:

```python
def grovers_algorithm(n_qubits, iterations):
    """
    Implement Grover's algorithm
    
    Args:
        n_qubits: Number of qubits
        iterations: Number of Grover iterations
    
    Returns:
        Circuit implementing Grover's algorithm
    """
    qc = QuantumCircuit(n_qubits, n_qubits)
    
    # Initialize superposition
    for i in range(n_qubits):
        qc.h(i)
    
    # Grover iterations
    for _ in range(iterations):
        # Oracle (marks target state)
        qc = apply_oracle(qc)
        
        # Diffusion operator
        qc = apply_diffusion(qc)
    
    # Measure
    qc.measure(range(n_qubits), range(n_qubits))
    
    return qc

def apply_diffusion(qc):
    """Apply diffusion operator"""
    n = qc.num_qubits
    
    # Apply Hadamard
    for i in range(n):
        qc.h(i)
    
    # Apply X
    for i in range(n):
        qc.x(i)
    
    # Multi-controlled Z
    qc.h(n-1)
    qc.mcx(list(range(n-1)), n-1)
    qc.h(n-1)
    
    # Apply X
    for i in range(n):
        qc.x(i)
    
    # Apply Hadamard
    for i in range(n):
        qc.h(i)
    
    return qc
```

#### 2.3 Quantum Fourier Transform (QFT)
Transform quantum states to frequency domain.

**Concept**:
```
QFT: |x⟩ → (1/√N) Σₖ e^(2πikx/N) |k⟩
Classical FFT: O(N log N)
Quantum QFT: O((log N)²)
```

#### 2.4 Phase Estimation
Estimate eigenvalue of unitary operator.

**Applications**:
- Shor's algorithm
- Quantum chemistry (VQE)
- Quantum simulation

### Level 3: Advanced Topics (Advanced)
**Time**: 4-6 weeks | **Prerequisites**: Level 2

#### 3.1 Quantum Error Correction
Protect quantum information from noise.

**Topics**:
- Bit-flip code
- Phase-flip code
- Surface code
- Stabilizer codes

**Kata-Style Exercise**:

```python
def bit_flip_code():
    """
    Implement 3-qubit bit-flip code
    Protects against single bit-flip errors
    """
    qc = QuantumCircuit(3, 3)
    
    # Encode: |ψ⟩ → |ψψψ⟩
    qc.cx(0, 1)
    qc.cx(0, 2)
    
    # Simulate error (bit flip on qubit 1)
    # qc.x(1)
    
    # Syndrome measurement
    qc.cx(0, 1)
    qc.cx(1, 2)
    qc.measure([1, 2], [0, 1])
    
    # Error correction based on syndrome
    # If syndrome = 01: error on qubit 1
    # If syndrome = 11: error on qubit 2
    
    return qc
```

#### 3.2 Variational Quantum Algorithms
Hybrid classical-quantum optimization.

**Topics**:
- VQE (Variational Quantum Eigensolver)
- QAOA (Quantum Approximate Optimization)
- QNN (Quantum Neural Networks)

#### 3.3 Quantum Simulation
Simulate quantum systems.

**Applications**:
- Molecular simulation
- Condensed matter physics
- Quantum chemistry

#### 3.4 Quantum Machine Learning
Quantum algorithms for ML.

**Topics**:
- Quantum kernels
- Quantum neural networks
- Quantum autoencoders
- Quantum GANs

---

## Kata-Style Exercise Template

```python
class QuantumKata:
    """Template for kata-style quantum exercises"""
    
    def __init__(self, name, difficulty, time_estimate):
        self.name = name
        self.difficulty = difficulty  # Beginner, Intermediate, Advanced
        self.time_estimate = time_estimate  # minutes
        self.exercises = []
    
    def add_exercise(self, title, description, starter_code, solution, verification_fn):
        """Add exercise to kata"""
        exercise = {
            'title': title,
            'description': description,
            'starter_code': starter_code,
            'solution': solution,
            'verification': verification_fn
        }
        self.exercises.append(exercise)
    
    def verify_solution(self, exercise_idx, user_circuit):
        """Verify user's solution"""
        exercise = self.exercises[exercise_idx]
        return exercise['verification'](user_circuit)
    
    def get_hint(self, exercise_idx):
        """Get hint for exercise"""
        # Return partial solution or guidance
        pass
    
    def get_solution(self, exercise_idx):
        """Get full solution"""
        return self.exercises[exercise_idx]['solution']
```

---

## Learning Progression

### Week 1-2: Foundations
- [ ] Basic gates (X, Y, Z, H, S, T)
- [ ] Multi-qubit gates (CNOT, CZ, SWAP)
- [ ] Measurement and collapse
- [ ] Bell states and entanglement

### Week 3-4: First Algorithms
- [ ] Deutsch-Jozsa algorithm
- [ ] Grover's algorithm
- [ ] Quantum Fourier Transform
- [ ] Simple oracles

### Week 5-6: Variational Algorithms
- [ ] VQE for molecular simulation
- [ ] QAOA for optimization
- [ ] Parameter optimization
- [ ] Hybrid workflows

### Week 7-8: Advanced Topics
- [ ] Quantum error correction
- [ ] Quantum machine learning
- [ ] Quantum simulation
- [ ] Production considerations

---

## Recommended Resources

### Official Katas
- Microsoft Quantum Katas: https://github.com/microsoft/QuantumKatas
- Qiskit Textbook: https://qiskit.org/textbook
- PennyLane Demos: https://pennylane.ai/qml/demos/

### Interactive Platforms
- IBM Quantum Composer: https://quantum.ibm.com/
- Google Cirq Colab: https://colab.research.google.com/
- Xanadu PennyLane: https://pennylane.ai/

### Books
- "Quantum Computation and Quantum Information" - Nielsen & Chuang
- "Programming Quantum Computers" - Aaronson et al.
- "Quantum Computing in Action" - Hidary

---

## Self-Assessment

### After Level 1 (Foundations)
- [ ] Can create basic quantum circuits
- [ ] Understand superposition and entanglement
- [ ] Can measure quantum states
- [ ] Familiar with common gates

### After Level 2 (Algorithms)
- [ ] Can implement Deutsch-Jozsa
- [ ] Can implement Grover's algorithm
- [ ] Understand quantum advantage
- [ ] Can design simple oracles

### After Level 3 (Advanced)
- [ ] Can implement VQE
- [ ] Can implement QAOA
- [ ] Understand error correction basics
- [ ] Can build quantum ML models

---

## Tips for Success

1. **Practice regularly**: Spend 1-2 hours per day
2. **Understand concepts**: Don't just memorize code
3. **Experiment**: Modify exercises and see what happens
4. **Build intuition**: Visualize quantum states
5. **Debug systematically**: Use simulators to debug
6. **Join community**: Learn from others
7. **Build projects**: Apply knowledge to real problems
