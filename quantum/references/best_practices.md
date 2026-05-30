# Qiskit Best Practices

## Circuit Design

### 1. Qubit Mapping
- **Minimize two-qubit gates**: Reduces circuit depth and errors
- **Respect hardware topology**: Arrange qubits to match device connectivity
- **Use layout_method in transpile()**: Automatic optimization

```python
from qiskit import transpile
optimized = transpile(qc, backend, layout_method='sabre')
```

### 2. Gate Optimization
- **Use native gates**: Match backend's gate set
- **Combine single-qubit rotations**: Reduces gate count
- **Commute gates**: Reorder for better optimization

```python
from qiskit.transpiler.passes import Optimize1qGates
pass_manager = PassManager([Optimize1qGates()])
optimized = pass_manager.run(qc)
```

### 3. Circuit Depth
- **Minimize depth**: Critical for NISQ devices (high error rates)
- **Target depth < 100 gates**: For current hardware
- **Use parallel gates**: Execute independent operations simultaneously

---

## Error Mitigation

### 1. Measurement Error Mitigation
**Problem**: Measurement errors dominate on current hardware

**Solution**: Calibrate measurement errors and apply correction

```python
from qiskit_aer.primitives import Sampler
from qiskit_aer.primitives import EstimatorV2
# Use error mitigation options
sampler = Sampler(options={"seed_simulator": 42})
```

### 2. Zero Noise Extrapolation
**Concept**: Run at different noise levels and extrapolate to zero noise

```python
# Requires multiple transpilation levels
results = []
for level in [0, 1, 2, 3]:
    qc_opt = transpile(qc, backend, optimization_level=level)
    result = execute(qc_opt, backend).result()
    results.append(result)
```

### 3. Dynamical Decoupling
**Purpose**: Reduce decoherence during idle periods

```python
from qiskit.transpiler.passes import DynamicalDecoupling
from qiskit.circuit.library import XGate
dd_pass = DynamicalDecoupling(qubits=[0, 1], sequence=[XGate()])
```

---

## Simulation vs Hardware

### Local Simulation
**Advantages**: Fast, no queue, unlimited shots
**Disadvantages**: No noise, unrealistic results

```python
from qiskit_aer import AerSimulator
simulator = AerSimulator()
job = simulator.run(qc, shots=1024)
```

### Noisy Simulation
**Advantages**: Realistic error modeling
**Disadvantages**: Slower, requires noise model

```python
from qiskit_aer.noise import NoiseModel
noise_model = NoiseModel.from_backend(backend)
simulator = AerSimulator(noise_model=noise_model)
```

### Real Hardware
**Advantages**: Actual quantum device
**Disadvantages**: Queue time, limited shots, high error rates

```python
from qiskit_ibm_runtime import QiskitRuntimeService
service = QiskitRuntimeService()
backend = service.backend('ibm_kyoto')
```

---

## Parameterized Circuits

### 1. Creating Parameterized Circuits
```python
from qiskit.circuit import Parameter
theta = Parameter('θ')
phi = Parameter('φ')

qc = QuantumCircuit(2)
qc.ry(theta, 0)
qc.cx(0, 1)
qc.rz(phi, 1)
```

### 2. Binding Parameters
```python
# Bind single values
bound_qc = qc.bind_parameters({theta: 0.5, phi: 1.0})

# Bind multiple values (for VQE optimization)
import numpy as np
param_values = np.linspace(0, 2*np.pi, 100)
circuits = [qc.bind_parameters({theta: val}) for val in param_values]
```

---

## Performance Optimization

### 1. Batch Execution
```python
# Submit multiple circuits at once
circuits = [qc1, qc2, qc3, ...]
job = backend.run(circuits, shots=1024)
```

### 2. Caching Results
```python
import pickle
# Save results
with open('results.pkl', 'wb') as f:
    pickle.dump(result, f)

# Load results
with open('results.pkl', 'rb') as f:
    result = pickle.load(f)
```

### 3. Parallel Execution
```python
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(run_circuit, qc) for qc in circuits]
    results = [f.result() for f in futures]
```

---

## Debugging

### 1. Circuit Visualization
```python
# ASCII representation
print(qc)

# LaTeX/PNG (requires matplotlib)
qc.draw(output='mpl')

# Interactive visualization
qc.draw(output='text')
```

### 2. Statevector Inspection
```python
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector

simulator = AerSimulator(method='statevector')
result = simulator.run(qc).result()
statevector = result.get_statevector(qc)
print(statevector)
```

### 3. Unitary Matrix
```python
from qiskit.quantum_info import Operator
operator = Operator(qc)
print(operator.data)  # Unitary matrix
```

---

## Common Pitfalls

### 1. Forgetting Measurements
```python
# ❌ Wrong: No measurements
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)

# ✅ Correct: Include measurements
qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])
```

### 2. Incorrect Qubit Ordering
```python
# ❌ Easy to confuse
qc.cx(0, 1)  # Control=0, Target=1

# ✅ Be explicit
qc.cx(control_qubit=0, target_qubit=1)
```

### 3. Ignoring Hardware Connectivity
```python
# ❌ May fail on hardware
qc.cx(0, 5)  # Qubits 0 and 5 not connected

# ✅ Transpile handles this
optimized = transpile(qc, backend)
```

---

## Reproducibility

### 1. Set Seeds
```python
from qiskit_aer import AerSimulator
import numpy as np

np.random.seed(42)
simulator = AerSimulator(seed_simulator=42)
```

### 2. Save Circuits
```python
# QASM format
qc.qasm(formatted=True)

# Pickle
import pickle
with open('circuit.pkl', 'wb') as f:
    pickle.dump(qc, f)
```

### 3. Document Parameters
```python
# Include metadata
qc.metadata = {
    'algorithm': 'VQE',
    'ansatz': 'RealAmplitudes',
    'parameters': {'theta': 0.5, 'phi': 1.0}
}
```

---

## Resource Management

### 1. Memory Efficiency
- **Limit shots**: Reduce memory usage
- **Use sparse representation**: For large circuits
- **Stream results**: Process incrementally

### 2. Execution Time
- **Transpile once**: Reuse optimized circuit
- **Batch circuits**: Reduce overhead
- **Use primitives**: Sampler/Estimator for efficiency

### 3. Quota Management
- **Monitor usage**: Track API calls
- **Cache results**: Avoid redundant executions
- **Use simulators**: For development

---

## Advanced Topics

### 1. Custom Transpiler Passes
```python
from qiskit.transpiler.basepasses import TransformationPass
from qiskit.circuit import QuantumCircuit

class CustomPass(TransformationPass):
    def run(self, dag):
        # Modify DAG
        return dag
```

### 2. Pulse-Level Programming
```python
from qiskit import pulse
with pulse.build(backend) as schedule:
    pulse.play(pulse.Gaussian(...), pulse.drive_channel(0))
```

### 3. Dynamic Circuits
```python
# Conditional operations based on measurement
qc = QuantumCircuit(2, 1)
qc.h(0)
qc.measure(0, 0)
qc.cx(0, 1).c_if(0, 1)  # CNOT if measurement result is 1
```

---

## References
- Qiskit Documentation: https://qiskit.org/documentation/
- Qiskit Textbook: https://qiskit.org/textbook
- IBM Quantum Composer: https://quantum.ibm.com/composer
- GitHub Issues: https://github.com/Qiskit/qiskit/issues
