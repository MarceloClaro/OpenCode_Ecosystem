# Quantum Computing Applications

Practical applications of quantum computing across chemistry, finance, optimization, and machine learning.

## Chemistry Applications

### 1. Molecular Simulation (VQE)

**Problem**: Calculate ground state energy of molecules

**Quantum Advantage**: Exponential speedup for large molecules

**Workflow**:
1. Define molecular Hamiltonian
2. Create variational ansatz
3. Optimize parameters to minimize energy
4. Compare with classical methods

**Example: H₂ Molecule**
```python
from qiskit.circuit import ParameterVector
from qiskit.primitives import Estimator
from scipy.optimize import minimize

# Hamiltonian for H2
H2_hamiltonian = {
    'ZZ': -1.05,  # Z0 Z1 coefficient
    'Z': [0.39, 0.39],  # Z0, Z1 coefficients
    'XX': -0.01  # X0 X1 coefficient
}

# Ansatz
params = ParameterVector('θ', 3)
qc = QuantumCircuit(2)
qc.x(0)  # Hartree-Fock initial state
qc.ry(params[0], 0)
qc.cx(0, 1)
qc.ry(params[1], 1)

# Optimize
def cost_fn(p):
    bound_qc = qc.bind_parameters(dict(zip(params, p)))
    estimator = Estimator()
    result = estimator.run(bound_qc, H2_hamiltonian).result()
    return result.values[0]

result = minimize(cost_fn, x0=[0, 0, 0], method='COBYLA')
print(f"Ground state energy: {result.fun:.6f}")
```

**Current Status**: NISQ-era demonstrations on 2-4 qubits
**Timeline**: Practical advantage in 5-10 years (with error correction)

### 2. Drug Discovery

**Problem**: Simulate protein-drug interactions

**Quantum Advantage**: Simulate quantum effects in biological systems

**Workflow**:
1. Map protein structure to quantum circuit
2. Simulate molecular interactions
3. Calculate binding energies
4. Identify promising drug candidates

**Applications**:
- Enzyme catalysis
- Protein folding
- Drug-protein binding
- Reaction mechanisms

### 3. Materials Science

**Problem**: Design new materials with desired properties

**Quantum Advantage**: Simulate electronic structure of materials

**Workflow**:
1. Define material Hamiltonian
2. Calculate band structure
3. Predict properties (conductivity, magnetism)
4. Optimize composition

**Examples**:
- Superconductors
- Semiconductors
- Catalysts
- Battery materials

---

## Finance Applications

### 1. Option Pricing

**Problem**: Calculate fair price of financial derivatives

**Quantum Advantage**: Amplitude estimation for probability computation

**Workflow**:
1. Encode stock price distribution
2. Define payoff function
3. Use quantum amplitude estimation
4. Extract probability

**Example: European Call Option**
```python
# Stock price: S0 = $100, Strike = $110, Rate = 5%
# Payoff: max(S_T - K, 0)

# Quantum circuit encodes price distribution
n_qubits = 3  # 8 possible prices
qc = QuantumCircuit(n_qubits, n_qubits)

# Encode uniform distribution
for i in range(n_qubits):
    qc.h(i)

# Oracle: Mark profitable states
# States |101⟩, |110⟩, |111⟩ correspond to S > K
for i in range(n_qubits):
    qc.z(i)

# Measure
qc.measure(range(n_qubits), range(n_qubits))

# Simulate and extract probability
simulator = AerSimulator()
job = simulator.run(qc, shots=1024)
result = job.result()
counts = result.get_counts(qc)

# Probability of profit
prob_profit = sum(v for k, v in counts.items() if k.count('1') >= 2) / 1024
option_price = prob_profit * 100  # Simplified
```

**Quantum Speedup**: O(1/ε) vs O(1/ε²) for classical Monte Carlo

### 2. Portfolio Optimization

**Problem**: Allocate assets to maximize return and minimize risk

**Quantum Advantage**: QAOA for combinatorial optimization

**Workflow**:
1. Define objective function (return - risk)
2. Create QAOA circuit
3. Optimize parameters
4. Extract optimal allocation

**Example**:
```python
# Assets: Tech (0.5), Finance (0.3), Healthcare (0.4)
# Objective: Maximize weighted return

n_assets = 3
qc = QuantumCircuit(n_assets)

# Initial superposition
for i in range(n_assets):
    qc.h(i)

# Cost Hamiltonian: Maximize return
gamma = Parameter('γ')
weights = [0.5, 0.3, 0.4]
for i in range(n_assets):
    qc.rz(2 * gamma * weights[i], i)

# Mixer Hamiltonian: Explore space
beta = Parameter('β')
for i in range(n_assets):
    qc.rx(2 * beta, i)

# Optimal parameters (approximate)
gamma_opt ≈ 0.628
beta_opt ≈ 0.785
```

**Current Status**: Demonstrations on 3-5 assets
**Advantage**: Potential speedup for 10+ assets

### 3. Risk Analysis

**Problem**: Estimate Value at Risk (VaR) for portfolio

**Quantum Advantage**: Amplitude estimation for tail probabilities

**Workflow**:
1. Encode loss distribution
2. Define risk threshold
3. Estimate probability of exceeding threshold
4. Calculate VaR

---

## Optimization Applications

### 1. MaxCut Problem

**Problem**: Partition graph vertices to maximize edge cuts

**Quantum Advantage**: QAOA for combinatorial optimization

**Workflow**:
1. Define graph and edges
2. Create QAOA circuit
3. Optimize parameters
4. Extract partition

**Example**:
```python
# Graph: 4 vertices, edges: (0,1), (1,2), (2,3), (3,0), (0,2)
edges = [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)]
n_qubits = 4

qc = QuantumCircuit(n_qubits)

# Initial superposition
for i in range(n_qubits):
    qc.h(i)

# Cost Hamiltonian
gamma = Parameter('γ')
for u, v in edges:
    qc.rzz(2 * gamma, u, v)

# Mixer Hamiltonian
beta = Parameter('β')
for i in range(n_qubits):
    qc.rx(2 * beta, i)

# Optimal partition: {0, 2} and {1, 3}
# Cuts 4 out of 5 edges
```

**Classical Complexity**: NP-hard
**Quantum Advantage**: Potential polynomial speedup

### 2. Traveling Salesman Problem (TSP)

**Problem**: Find shortest route visiting all cities

**Quantum Advantage**: Grover search + QAOA hybrid

**Workflow**:
1. Encode cities and distances
2. Create quantum circuit
3. Search for optimal route
4. Extract solution

**Example**:
```python
# 4 cities, 24 possible routes
# Classical: O(n!) = O(24)
# Quantum: O(√n!) ≈ O(5) with Grover

# Distance matrix
distances = np.array([
    [0, 10, 15, 20],
    [10, 0, 35, 25],
    [15, 35, 0, 30],
    [20, 25, 30, 0]
])

# Quantum circuit encodes routes
# Oracle marks routes below threshold
# Grover amplifies good solutions
```

**Current Status**: Demonstrations on 4-5 cities
**Advantage**: Exponential speedup for 10+ cities

### 3. Constraint Satisfaction (SAT)

**Problem**: Find variable assignments satisfying constraints

**Quantum Advantage**: Grover search for solution space

**Workflow**:
1. Encode constraints as oracle
2. Create Grover circuit
3. Apply amplitude amplification
4. Measure solution

**Example**:
```python
# 3-SAT problem: (x0 OR x1 OR ¬x2) AND (¬x0 OR x1 OR x2)
# Find assignment satisfying both clauses

n_qubits = 3
qc = QuantumCircuit(n_qubits)

# Initial superposition
for i in range(n_qubits):
    qc.h(i)

# Oracle: Mark satisfying assignments
# (Implementation depends on specific clauses)

# Grover amplification (2-3 iterations)
```

---

## Machine Learning Applications

### 1. Quantum Classification

**Problem**: Classify data using quantum features

**Quantum Advantage**: Access to high-dimensional feature space

**Workflow**:
1. Encode data into quantum state
2. Apply variational ansatz
3. Measure output
4. Train parameters

**Example**:
```python
# Binary classification: Iris dataset (2 features)
from quantum_classifier import QuantumNeuralNetwork

# Create QNN
qnn = QuantumNeuralNetwork(n_qubits=2, n_layers=2)
params = qnn.initialize_params()

# Training data
X_train = np.array([[0.5, 0.5], [1.0, 1.0], [2.0, 2.0]])
y_train = np.array([0, 0, 1])

# Train
def cost_fn(p):
    predictions = [qnn.predict(x, p) for x in X_train]
    return np.mean((np.array(predictions) - y_train)**2)

result = minimize(cost_fn, params, method='COBYLA')

# Predict
predictions = [qnn.predict(x, result.x) for x in X_test]
```

**Quantum Advantage**: Potential exponential separation for specific datasets

### 2. Quantum Kernel Methods

**Problem**: Compute similarity between data points

**Quantum Advantage**: Kernel computation in high-dimensional space

**Workflow**:
1. Define feature map
2. Compute kernel matrix
3. Train classical SVM
4. Classify new data

**Example**:
```python
from quantum_classifier import QuantumKernel
from sklearn.svm import SVC

# Create quantum kernel
qkernel = QuantumKernel(n_qubits=3, feature_map='iqp')

# Compute kernel matrix
K = qkernel.compute_kernel_matrix(X_train)

# Train SVM
svm = SVC(kernel='precomputed')
svm.fit(K, y_train)

# Predict
K_test = np.array([
    [qkernel.compute_kernel(x_test, x) for x in X_train]
])
predictions = svm.predict(K_test)
```

**Quantum Advantage**: Exponential feature space for certain datasets

### 3. Quantum Generative Models

**Problem**: Generate new data samples

**Quantum Advantage**: Sampling from complex distributions

**Workflow**:
1. Define generative circuit
2. Train parameters
3. Sample from distribution
4. Generate new data

**Applications**:
- Image generation
- Data augmentation
- Anomaly detection
- Feature extraction

---

## Quantum Advantage Analysis

### When Quantum Helps

| Problem | Classical | Quantum | Advantage |
|---------|-----------|---------|-----------|
| Molecular simulation | Exponential | Polynomial | Exponential |
| Unstructured search | O(n) | O(√n) | Quadratic |
| Factoring | Exponential | Polynomial | Exponential |
| Optimization (QAOA) | NP-hard | Heuristic | Problem-dependent |
| ML (certain kernels) | Exponential | Polynomial | Exponential |

### Current Limitations (NISQ Era)

1. **Noise**: Error rates 0.1-1% per gate
2. **Depth**: Limited to 100-1000 gates
3. **Qubits**: 50-1000 qubits available
4. **Coherence**: Microseconds to milliseconds

### Realistic Expectations

- **Near-term (2024-2026)**: Hybrid algorithms, small instances
- **Medium-term (2026-2030)**: Quantum advantage on specific problems
- **Long-term (2030+)**: Quantum-dominant algorithms (with error correction)

---

## Implementation Patterns

### Pattern 1: VQE for Chemistry
```python
# 1. Define Hamiltonian
H = create_hamiltonian(molecule)

# 2. Create ansatz
ansatz = create_ansatz(n_qubits, n_layers)

# 3. Define cost function
def cost_fn(params):
    bound_qc = ansatz.bind_parameters(params)
    estimator = Estimator()
    result = estimator.run(bound_qc, H).result()
    return result.values[0]

# 4. Optimize
result = minimize(cost_fn, x0=initial_params, method='COBYLA')
```

### Pattern 2: QAOA for Optimization
```python
# 1. Define problem
problem = define_optimization_problem()

# 2. Create QAOA circuit
qaoa = QAOA(problem, p=1)

# 3. Optimize parameters
result = qaoa.optimize()

# 4. Extract solution
solution = qaoa.extract_solution(result)
```

### Pattern 3: Quantum ML
```python
# 1. Encode data
encoded_qc = encode_data(X_train)

# 2. Create ansatz
ansatz = create_ansatz(n_qubits, n_layers)

# 3. Combine
full_circuit = encoded_qc + ansatz

# 4. Train
model = QuantumNeuralNetwork(full_circuit)
model.train(X_train, y_train)
```

---

## Resources

### Tutorials
- Qiskit Nature: Molecular simulation
- Qiskit Finance: Portfolio optimization
- Qiskit Optimization: Combinatorial problems
- Qiskit Machine Learning: Quantum ML

### Papers
- "Quantum algorithms for supervised learning" - Schuld et al.
- "QAOA: Performance, mechanism, and implementation" - Cerezo et al.
- "Barren plateaus in quantum neural network training landscapes" - McClean et al.

### Benchmarks
- QAOA benchmark suite
- Quantum ML benchmark
- Molecular simulation benchmarks

---

## Key Takeaways

1. **Chemistry**: VQE for molecular simulation
2. **Finance**: Amplitude estimation for pricing
3. **Optimization**: QAOA for combinatorial problems
4. **ML**: Quantum kernels and variational circuits
5. **Current**: NISQ-era demonstrations
6. **Future**: Quantum advantage with error correction
