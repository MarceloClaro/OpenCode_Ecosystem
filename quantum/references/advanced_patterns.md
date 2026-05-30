# Advanced Quantum Computing Patterns

Production-ready patterns for building sophisticated quantum applications.

## Pattern 1: Hybrid Quantum-Classical Optimization

**Use Case**: Variational algorithms (VQE, QAOA)

**Architecture**:
```
Classical Optimizer → Quantum Circuit → Measurement → Cost Function → Update Parameters
```

**Implementation**:

```python
from scipy.optimize import minimize
from qiskit.primitives import Estimator
from qiskit.circuit import ParameterVector

class HybridOptimizer:
    def __init__(self, ansatz, hamiltonian, backend=None):
        self.ansatz = ansatz
        self.hamiltonian = hamiltonian
        self.backend = backend or Estimator()
        self.iteration = 0
        self.history = []
    
    def cost_function(self, params):
        """Evaluate cost for given parameters"""
        # Bind parameters
        bound_circuit = self.ansatz.bind_parameters(
            dict(zip(self.ansatz.parameters, params))
        )
        
        # Estimate expectation value
        job = self.backend.run(bound_circuit, self.hamiltonian)
        result = job.result()
        cost = result.values[0]
        
        # Track history
        self.history.append(cost)
        self.iteration += 1
        
        if self.iteration % 10 == 0:
            print(f"Iteration {self.iteration}: Cost = {cost:.6f}")
        
        return cost
    
    def optimize(self, initial_params, method='COBYLA', maxiter=1000):
        """Run optimization"""
        result = minimize(
            self.cost_function,
            initial_params,
            method=method,
            options={'maxiter': maxiter}
        )
        return result

# Usage
ansatz = create_ansatz(n_qubits=2, n_layers=2)
hamiltonian = create_hamiltonian()
optimizer = HybridOptimizer(ansatz, hamiltonian)

initial_params = np.random.rand(len(ansatz.parameters))
result = optimizer.optimize(initial_params)

print(f"Optimal parameters: {result.x}")
print(f"Minimum cost: {result.fun:.6f}")
```

**Best Practices**:
- Use stateless cost functions for parallelization
- Implement callback for monitoring convergence
- Use gradient-based optimizers when possible
- Batch parameter updates for efficiency

---

## Pattern 2: Circuit Composition and Reusability

**Use Case**: Building complex circuits from components

**Architecture**:
```
Component 1 → Component 2 → Component 3 → Measurement
```

**Implementation**:

```python
class QuantumComponent:
    """Base class for reusable quantum components"""
    
    def __init__(self, name, n_qubits, n_params=0):
        self.name = name
        self.n_qubits = n_qubits
        self.n_params = n_params
        self.circuit = None
    
    def build(self, params=None):
        """Build the component circuit"""
        raise NotImplementedError
    
    def compose_with(self, other):
        """Compose with another component"""
        combined = QuantumCircuit(
            self.n_qubits + other.n_qubits
        )
        combined.append(self.circuit, range(self.n_qubits))
        combined.append(other.circuit, range(other.n_qubits))
        return combined

class FeatureMap(QuantumComponent):
    """Encode classical data into quantum state"""
    
    def __init__(self, n_qubits, data):
        super().__init__('FeatureMap', n_qubits)
        self.data = data
    
    def build(self, params=None):
        qc = QuantumCircuit(self.n_qubits)
        for i, x in enumerate(self.data):
            qc.ry(x, i)
        self.circuit = qc
        return qc

class Ansatz(QuantumComponent):
    """Parameterized quantum circuit"""
    
    def __init__(self, n_qubits, n_layers):
        super().__init__('Ansatz', n_qubits, n_params=n_qubits*n_layers*2)
        self.n_layers = n_layers
    
    def build(self, params):
        qc = QuantumCircuit(self.n_qubits)
        idx = 0
        
        for layer in range(self.n_layers):
            # Rotation layer
            for i in range(self.n_qubits):
                qc.ry(params[idx], i)
                idx += 1
            
            # Entanglement layer
            for i in range(self.n_qubits - 1):
                qc.cx(i, i + 1)
            
            # Another rotation layer
            for i in range(self.n_qubits):
                qc.rz(params[idx], i)
                idx += 1
        
        self.circuit = qc
        return qc

# Usage
feature_map = FeatureMap(2, [0.5, 0.3])
ansatz = Ansatz(2, 2)

feature_map.build()
ansatz.build(np.random.rand(8))

# Compose
full_circuit = QuantumCircuit(2)
full_circuit.append(feature_map.circuit, [0, 1])
full_circuit.append(ansatz.circuit, [0, 1])
```

**Best Practices**:
- Use object-oriented design for reusability
- Implement parameter binding properly
- Document component interfaces
- Test components independently

---

## Pattern 3: Error Mitigation

**Use Case**: Reduce effects of noise on NISQ devices

**Techniques**:
1. **Zero Noise Extrapolation (ZNE)**
2. **Probabilistic Error Cancellation (PEC)**
3. **Measurement Error Mitigation**

**Implementation**:

```python
from qiskit_aer.noise import NoiseModel
from qiskit_aer import AerSimulator

class ErrorMitigation:
    """Error mitigation techniques for NISQ devices"""
    
    @staticmethod
    def zero_noise_extrapolation(circuit, backend, noise_factors=[1, 2, 3]):
        """
        Zero Noise Extrapolation
        Amplify noise, extrapolate to zero noise
        """
        results = []
        
        for factor in noise_factors:
            # Amplify noise by inserting identity gates
            amplified_qc = ErrorMitigation._amplify_noise(circuit, factor)
            
            # Execute
            job = backend.run(amplified_qc, shots=1024)
            result = job.result()
            counts = result.get_counts(amplified_qc)
            
            # Extract expectation value
            exp_val = ErrorMitigation._counts_to_expectation(counts)
            results.append((factor, exp_val))
        
        # Extrapolate to zero noise
        factors = np.array([r[0] for r in results])
        values = np.array([r[1] for r in results])
        
        # Linear fit: E(λ) = a + b*λ
        coeffs = np.polyfit(factors, values, 1)
        zero_noise_value = coeffs[1]  # Intercept
        
        return zero_noise_value
    
    @staticmethod
    def _amplify_noise(circuit, factor):
        """Amplify noise by inserting identity gates"""
        amplified = circuit.copy()
        for _ in range(factor - 1):
            for i in range(circuit.num_qubits):
                amplified.id(i)
        return amplified
    
    @staticmethod
    def measurement_error_mitigation(counts, calibration_matrix):
        """
        Mitigate measurement errors using calibration matrix
        """
        # Invert calibration matrix
        inv_calib = np.linalg.inv(calibration_matrix)
        
        # Convert counts to probability vector
        total_shots = sum(counts.values())
        prob_vector = np.array([
            counts.get(format(i, f'0{len(counts.keys())}b'), 0) / total_shots
            for i in range(2**len(list(counts.keys())[0]))
        ])
        
        # Apply inverse calibration
        mitigated_probs = inv_calib @ prob_vector
        
        # Ensure valid probabilities
        mitigated_probs = np.maximum(mitigated_probs, 0)
        mitigated_probs /= np.sum(mitigated_probs)
        
        return mitigated_probs
    
    @staticmethod
    def _counts_to_expectation(counts):
        """Convert measurement counts to expectation value"""
        total = sum(counts.values())
        exp_val = 0
        for bitstring, count in counts.items():
            # Assume Z measurement
            parity = (-1) ** bitstring.count('1')
            exp_val += parity * count / total
        return exp_val

# Usage
circuit = create_circuit()
backend = AerSimulator(noise_model=NoiseModel.from_backend(real_backend))

# Zero noise extrapolation
mitigated_value = ErrorMitigation.zero_noise_extrapolation(circuit, backend)
print(f"Mitigated value: {mitigated_value:.6f}")
```

**Best Practices**:
- Use multiple noise factors for ZNE
- Calibrate measurement errors regularly
- Combine multiple mitigation techniques
- Validate on known results

---

## Pattern 4: Distributed Quantum Simulation

**Use Case**: Simulate large quantum systems

**Architecture**:
```
Problem → Decompose → Parallel Simulation → Combine Results
```

**Implementation**:

```python
from concurrent.futures import ThreadPoolExecutor
import multiprocessing as mp

class DistributedSimulator:
    """Distribute quantum simulation across multiple cores"""
    
    def __init__(self, n_workers=None):
        self.n_workers = n_workers or mp.cpu_count()
        self.executor = ThreadPoolExecutor(max_workers=self.n_workers)
    
    def simulate_ensemble(self, circuits, shots=1024):
        """
        Simulate ensemble of circuits in parallel
        """
        futures = []
        for circuit in circuits:
            future = self.executor.submit(
                self._simulate_single,
                circuit,
                shots
            )
            futures.append(future)
        
        results = [f.result() for f in futures]
        return results
    
    @staticmethod
    def _simulate_single(circuit, shots):
        """Simulate single circuit"""
        simulator = AerSimulator()
        job = simulator.run(circuit, shots=shots)
        result = job.result()
        return result.get_counts(circuit)
    
    def parameter_sweep(self, circuit_factory, param_values, shots=1024):
        """
        Sweep parameters in parallel
        """
        circuits = [
            circuit_factory(params)
            for params in param_values
        ]
        
        return self.simulate_ensemble(circuits, shots)

# Usage
def circuit_factory(params):
    qc = QuantumCircuit(2)
    qc.ry(params[0], 0)
    qc.cx(0, 1)
    qc.ry(params[1], 1)
    qc.measure_all()
    return qc

simulator = DistributedSimulator(n_workers=4)
param_values = np.random.rand(100, 2)

results = simulator.parameter_sweep(circuit_factory, param_values)
print(f"Simulated {len(results)} circuits in parallel")
```

**Best Practices**:
- Use thread pools for I/O-bound tasks
- Use process pools for CPU-bound tasks
- Batch circuits for efficiency
- Monitor resource usage

---

## Pattern 5: Quantum State Tomography

**Use Case**: Characterize quantum states experimentally

**Implementation**:

```python
class QuantumStateTomography:
    """Reconstruct quantum state from measurements"""
    
    @staticmethod
    def measure_in_basis(circuit, basis='Z', qubit=0, shots=1024):
        """
        Measure in specified basis
        basis: 'Z', 'X', or 'Y'
        """
        qc = circuit.copy()
        
        # Rotate to measurement basis
        if basis == 'X':
            qc.h(qubit)
        elif basis == 'Y':
            qc.rx(np.pi/2, qubit)
        
        # Measure
        qc.measure(qubit, 0)
        
        # Simulate
        simulator = AerSimulator()
        job = simulator.run(qc, shots=shots)
        result = job.result()
        counts = result.get_counts(qc)
        
        # Calculate expectation value
        exp_val = (counts.get('0', 0) - counts.get('1', 0)) / shots
        return exp_val
    
    @staticmethod
    def tomography_single_qubit(circuit, qubit=0, shots=1024):
        """
        Perform single-qubit tomography
        Returns: [⟨X⟩, ⟨Y⟩, ⟨Z⟩]
        """
        exp_x = QuantumStateTomography.measure_in_basis(
            circuit, 'X', qubit, shots
        )
        exp_y = QuantumStateTomography.measure_in_basis(
            circuit, 'Y', qubit, shots
        )
        exp_z = QuantumStateTomography.measure_in_basis(
            circuit, 'Z', qubit, shots
        )
        
        return np.array([exp_x, exp_y, exp_z])
    
    @staticmethod
    def reconstruct_density_matrix(expectations):
        """
        Reconstruct density matrix from Pauli expectations
        ρ = (I + ⟨X⟩X + ⟨Y⟩Y + ⟨Z⟩Z) / 2
        """
        exp_x, exp_y, exp_z = expectations
        
        pauli_x = np.array([[0, 1], [1, 0]])
        pauli_y = np.array([[0, -1j], [1j, 0]])
        pauli_z = np.array([[1, 0], [0, -1]])
        identity = np.eye(2)
        
        rho = (identity + exp_x*pauli_x + exp_y*pauli_y + exp_z*pauli_z) / 2
        return rho

# Usage
circuit = create_circuit()
expectations = QuantumStateTomography.tomography_single_qubit(circuit)
rho = QuantumStateTomography.reconstruct_density_matrix(expectations)

print(f"Density matrix:\n{rho}")
print(f"Purity: {np.trace(rho @ rho).real:.6f}")
```

**Best Practices**:
- Use multiple shots for accurate estimation
- Implement confidence intervals
- Validate with known states
- Handle measurement noise

---

## Pattern 6: Quantum Circuit Caching

**Use Case**: Optimize repeated simulations

**Implementation**:

```python
from functools import lru_cache
import hashlib

class CircuitCache:
    """Cache quantum circuit results"""
    
    def __init__(self, max_size=1000):
        self.cache = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
    
    @staticmethod
    def circuit_hash(circuit):
        """Generate hash of circuit"""
        circuit_str = str(circuit)
        return hashlib.md5(circuit_str.encode()).hexdigest()
    
    def get(self, circuit):
        """Get cached result"""
        key = self.circuit_hash(circuit)
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None
    
    def put(self, circuit, result):
        """Cache result"""
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            self.cache.pop(next(iter(self.cache)))
        
        key = self.circuit_hash(circuit)
        self.cache[key] = result
    
    def hit_rate(self):
        """Calculate cache hit rate"""
        total = self.hits + self.misses
        if total == 0:
            return 0
        return self.hits / total

# Usage
cache = CircuitCache(max_size=1000)

for i in range(100):
    circuit = create_circuit(params=i % 10)
    
    # Check cache
    cached_result = cache.get(circuit)
    if cached_result is not None:
        result = cached_result
    else:
        # Simulate
        simulator = AerSimulator()
        job = simulator.run(circuit, shots=1024)
        result = job.result()
        cache.put(circuit, result)

print(f"Cache hit rate: {cache.hit_rate():.2%}")
```

---

## Pattern 7: Quantum Circuit Benchmarking

**Use Case**: Evaluate circuit performance

**Implementation**:

```python
import time

class CircuitBenchmark:
    """Benchmark quantum circuits"""
    
    @staticmethod
    def measure_depth(circuit):
        """Measure circuit depth"""
        return circuit.depth()
    
    @staticmethod
    def measure_gate_count(circuit):
        """Count gates by type"""
        gate_counts = {}
        for instruction, qargs, cargs in circuit.data:
            gate_name = instruction.name
            gate_counts[gate_name] = gate_counts.get(gate_name, 0) + 1
        return gate_counts
    
    @staticmethod
    def measure_two_qubit_gates(circuit):
        """Count two-qubit gates"""
        count = 0
        for instruction, qargs, cargs in circuit.data:
            if len(qargs) == 2:
                count += 1
        return count
    
    @staticmethod
    def benchmark_simulation(circuit, shots=1024, n_trials=10):
        """Benchmark simulation time"""
        simulator = AerSimulator()
        times = []
        
        for _ in range(n_trials):
            start = time.time()
            job = simulator.run(circuit, shots=shots)
            result = job.result()
            end = time.time()
            times.append(end - start)
        
        return {
            'mean': np.mean(times),
            'std': np.std(times),
            'min': np.min(times),
            'max': np.max(times)
        }
    
    @staticmethod
    def generate_report(circuit):
        """Generate comprehensive benchmark report"""
        report = {
            'depth': CircuitBenchmark.measure_depth(circuit),
            'gates': CircuitBenchmark.measure_gate_count(circuit),
            'two_qubit_gates': CircuitBenchmark.measure_two_qubit_gates(circuit),
            'simulation_time': CircuitBenchmark.benchmark_simulation(circuit)
        }
        return report

# Usage
circuit = create_circuit()
report = CircuitBenchmark.generate_report(circuit)

print("Circuit Benchmark Report")
print(f"Depth: {report['depth']}")
print(f"Gates: {report['gates']}")
print(f"Two-qubit gates: {report['two_qubit_gates']}")
print(f"Simulation time: {report['simulation_time']['mean']:.6f}s ± {report['simulation_time']['std']:.6f}s")
```

---

## Key Takeaways

1. **Hybrid Optimization**: Combine quantum and classical processing
2. **Reusability**: Use component-based design
3. **Error Mitigation**: Reduce noise effects
4. **Parallelization**: Distribute simulations
5. **Characterization**: Understand quantum states
6. **Caching**: Optimize repeated simulations
7. **Benchmarking**: Measure performance

These patterns enable building robust, efficient quantum applications.
