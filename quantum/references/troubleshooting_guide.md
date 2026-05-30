# Quantum Computing Troubleshooting & Debugging Guide

Comprehensive guide for diagnosing and fixing common quantum computing issues.

## Installation & Setup Issues

### Issue: Qiskit Installation Fails

**Symptoms**: `pip install qiskit` fails with dependency errors

**Diagnosis**:
```bash
# Check Python version
python --version  # Should be 3.8+

# Check pip version
pip --version  # Should be recent

# Try verbose installation
pip install -v qiskit
```

**Solutions**:

1. **Update pip, setuptools, wheel**
```bash
pip install --upgrade pip setuptools wheel
pip install qiskit
```

2. **Use virtual environment**
```bash
python -m venv quantum_env
source quantum_env/bin/activate  # Linux/Mac
quantum_env\Scripts\activate  # Windows
pip install qiskit
```

3. **Install specific version**
```bash
pip install qiskit==0.43.0  # Stable version
```

4. **Check system dependencies**
```bash
# Ubuntu/Debian
sudo apt-get install build-essential python3-dev

# macOS
brew install python3
```

### Issue: ImportError: No module named 'qiskit'

**Symptoms**: `ImportError: No module named 'qiskit'` when running code

**Solutions**:

1. **Verify installation**
```bash
python -c "import qiskit; print(qiskit.__version__)"
```

2. **Check Python path**
```bash
python -c "import sys; print(sys.path)"
```

3. **Reinstall in correct environment**
```bash
which python  # Verify correct Python
pip install qiskit
```

### Issue: Qiskit-Aer Installation Fails

**Symptoms**: `pip install qiskit-aer` fails on compilation

**Solutions**:

1. **Install pre-built wheels**
```bash
pip install qiskit-aer --only-binary :all:
```

2. **Install build dependencies**
```bash
# Ubuntu/Debian
sudo apt-get install cmake build-essential

# macOS
brew install cmake
```

3. **Use conda instead**
```bash
conda install -c conda-forge qiskit-aer
```

---

## Circuit Construction Issues

### Issue: "Qubit Index Out of Bounds"

**Symptoms**: `IndexError: qubit index out of bounds`

**Example**:
```python
qc = QuantumCircuit(2)  # Only 2 qubits (0, 1)
qc.h(2)  # ERROR: qubit 2 doesn't exist
```

**Solution**:
```python
qc = QuantumCircuit(3)  # Need 3 qubits (0, 1, 2)
qc.h(2)  # Now OK
```

### Issue: "Classical Bit Index Out of Bounds"

**Symptoms**: `IndexError: classical bit index out of bounds`

**Example**:
```python
qc = QuantumCircuit(2, 1)  # 2 qubits, 1 classical bit
qc.measure(0, 1)  # ERROR: classical bit 1 doesn't exist
```

**Solution**:
```python
qc = QuantumCircuit(2, 2)  # 2 qubits, 2 classical bits
qc.measure([0, 1], [0, 1])  # Now OK
```

### Issue: "Duplicate Parameter Names"

**Symptoms**: `ValueError: Duplicate parameter names`

**Example**:
```python
from qiskit.circuit import Parameter

theta = Parameter('θ')
qc = QuantumCircuit(1)
qc.ry(theta, 0)
qc.rz(theta, 0)  # OK: same parameter
qc.ry(theta, 0)  # ERROR: duplicate in binding
```

**Solution**:
```python
# Use different parameters
theta1 = Parameter('θ1')
theta2 = Parameter('θ2')
qc.ry(theta1, 0)
qc.rz(theta2, 0)
```

### Issue: "Invalid Gate Parameters"

**Symptoms**: `ValueError: Invalid parameter value`

**Example**:
```python
qc = QuantumCircuit(1)
qc.ry("invalid", 0)  # ERROR: parameter must be numeric
```

**Solution**:
```python
import numpy as np
qc.ry(np.pi/4, 0)  # Use numeric value
```

---

## Simulation Issues

### Issue: "Simulator Not Found"

**Symptoms**: `QiskitError: No simulator backend found`

**Solutions**:

1. **Install Aer simulator**
```bash
pip install qiskit-aer
```

2. **Use available simulators**
```python
from qiskit import Aer

# List available simulators
print(Aer.backends())

# Use specific simulator
simulator = Aer.get_backend('qasm_simulator')
```

3. **Check backend availability**
```python
from qiskit_aer import AerSimulator

simulator = AerSimulator()
print(simulator.configuration())
```

### Issue: "Out of Memory During Simulation"

**Symptoms**: `MemoryError` or slow simulation with many qubits

**Causes**:
- State vector grows exponentially: 2^n amplitudes
- 20 qubits = 1 MB, 30 qubits = 1 GB

**Solutions**:

1. **Use statevector_simulator for small circuits**
```python
from qiskit_aer import AerSimulator

# For < 20 qubits
simulator = AerSimulator(method='statevector')
```

2. **Use qasm_simulator for larger circuits**
```python
# For > 20 qubits
simulator = AerSimulator(method='qasm')
```

3. **Reduce circuit depth**
```python
# Optimize circuit before simulation
from qiskit.transpiler import passes

pass_manager = passes.PassManager([
    passes.RemoveResetInZeroState(),
    passes.RemoveBarriers(),
    passes.CommutationAnalysis(),
    passes.CommutativeCancel()
])

optimized_qc = pass_manager.run(qc)
```

4. **Use GPU acceleration**
```python
simulator = AerSimulator(device='GPU')
```

### Issue: "Simulation Takes Too Long"

**Symptoms**: Simulation hangs or takes minutes

**Solutions**:

1. **Reduce shot count**
```python
job = simulator.run(qc, shots=100)  # Instead of 10000
```

2. **Increase simulator precision**
```python
simulator = AerSimulator(precision='single')  # Float32
```

3. **Use approximation methods**
```python
simulator = AerSimulator(method='density_matrix')
```

4. **Parallelize simulations**
```python
from concurrent.futures import ThreadPoolExecutor

def simulate_circuit(circuit):
    simulator = AerSimulator()
    job = simulator.run(circuit, shots=1024)
    return job.result()

circuits = [create_circuit(i) for i in range(10)]
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(simulate_circuit, circuits))
```

---

## Parameter & Optimization Issues

### Issue: "Optimization Doesn't Converge"

**Symptoms**: Cost function doesn't decrease, or increases

**Causes**:
- Learning rate too high
- Bad initial parameters
- Barren plateau
- Local minima

**Solutions**:

1. **Reduce learning rate**
```python
from scipy.optimize import minimize

result = minimize(cost_fn, x0, method='COBYLA', 
                 options={'maxiter': 1000, 'tol': 1e-6})
```

2. **Better initialization**
```python
import numpy as np

# Random initialization
x0 = np.random.rand(n_params) * 2 * np.pi

# Or use known good values
x0 = np.ones(n_params) * 0.1
```

3. **Detect barren plateau**
```python
# Check gradient magnitude
def check_barren_plateau(cost_fn, params, eps=1e-5):
    gradients = []
    for i in range(len(params)):
        params_plus = params.copy()
        params_plus[i] += eps
        grad = (cost_fn(params_plus) - cost_fn(params)) / eps
        gradients.append(abs(grad))
    
    avg_gradient = np.mean(gradients)
    print(f"Average gradient: {avg_gradient:.6f}")
    
    if avg_gradient < 1e-6:
        print("WARNING: Barren plateau detected!")
    
    return avg_gradient
```

4. **Use different optimizer**
```python
from scipy.optimize import minimize

# Try different methods
methods = ['COBYLA', 'SLSQP', 'L-BFGS-B']
for method in methods:
    result = minimize(cost_fn, x0, method=method)
    print(f"{method}: {result.fun:.6f}")
```

### Issue: "Parameter Binding Fails"

**Symptoms**: `ValueError: Cannot bind parameters`

**Example**:
```python
from qiskit.circuit import Parameter

theta = Parameter('θ')
qc = QuantumCircuit(1)
qc.ry(theta, 0)

# ERROR: Missing parameter
bound_qc = qc.bind_parameters({})
```

**Solution**:
```python
# Provide all parameters
bound_qc = qc.bind_parameters({theta: 0.5})
```

---

## Measurement Issues

### Issue: "Measurement Results Unexpected"

**Symptoms**: Measurement results don't match expected distribution

**Diagnosis**:

1. **Check circuit before measurement**
```python
print(qc)  # Visualize circuit

# Check statevector
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector

sv = Statevector.from_instruction(qc)
print(sv)  # Print quantum state
```

2. **Verify measurement basis**
```python
# Measure in Z basis (default)
qc.measure(range(n_qubits), range(n_qubits))

# Measure in X basis
qc.h(range(n_qubits))
qc.measure(range(n_qubits), range(n_qubits))

# Measure in Y basis
qc.rx(np.pi/2, range(n_qubits))
qc.measure(range(n_qubits), range(n_qubits))
```

### Issue: "Measurement Errors"

**Symptoms**: Results deviate from ideal due to hardware noise

**Solutions**:

1. **Use error mitigation**
```python
from qiskit_aer.noise import NoiseModel

# Create noise model
noise_model = NoiseModel.from_backend(backend)

# Simulate with noise
simulator = AerSimulator(noise_model=noise_model)
job = simulator.run(qc, shots=1024)
```

2. **Calibrate measurements**
```python
# Measure calibration matrix
def measure_calibration_matrix(backend, n_qubits):
    calib_matrix = np.zeros((2**n_qubits, 2**n_qubits))
    
    for i in range(2**n_qubits):
        # Prepare state |i⟩
        qc = QuantumCircuit(n_qubits, n_qubits)
        # ... state preparation code ...
        qc.measure(range(n_qubits), range(n_qubits))
        
        # Execute and get results
        job = backend.run(qc, shots=1024)
        result = job.result()
        counts = result.get_counts(qc)
        
        # Fill calibration matrix
        for j, count in counts.items():
            calib_matrix[i, int(j, 2)] = count / 1024
    
    return calib_matrix
```

---

## Hardware Execution Issues

### Issue: "Backend Not Available"

**Symptoms**: `IBMBackendError: No backend available`

**Solutions**:

1. **Check backend status**
```python
from qiskit_ibm_runtime import QiskitRuntimeService

service = QiskitRuntimeService()
backends = service.backends()
for backend in backends:
    print(f"{backend.name}: {backend.status()}")
```

2. **Use simulator instead**
```python
from qiskit_aer import AerSimulator

simulator = AerSimulator()
job = simulator.run(qc, shots=1024)
```

3. **Check queue time**
```python
backend = service.backend('ibm_nairobi')
print(f"Queue time: {backend.queue_time()} seconds")
```

### Issue: "Job Timeout"

**Symptoms**: Job execution takes too long or times out

**Solutions**:

1. **Reduce circuit complexity**
```python
# Simplify circuit
qc = qc.decompose()  # Decompose to basic gates
```

2. **Increase timeout**
```python
job = backend.run(qc, shots=1024, timeout=3600)  # 1 hour
```

3. **Check job status**
```python
job_id = "job_id_here"
job = backend.retrieve_job(job_id)
print(job.status())
```

---

## Debugging Techniques

### Technique 1: Circuit Visualization

```python
# ASCII visualization
print(qc)

# Matplotlib visualization
qc.draw(output='mpl', filename='circuit.png')

# LaTeX visualization
qc.draw(output='latex', filename='circuit.pdf')
```

### Technique 2: Statevector Inspection

```python
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector

# Get statevector
sv = Statevector.from_instruction(qc)
print(sv)

# Or simulate and extract
simulator = AerSimulator(method='statevector')
job = simulator.run(qc)
result = job.result()
statevector = result.get_statevector(qc)
print(statevector)
```

### Technique 3: Unitary Matrix Inspection

```python
from qiskit.quantum_info import Operator

# Get unitary matrix
U = Operator(qc)
print(U.data)

# Verify unitarity
print(np.allclose(U.data @ U.data.conj().T, np.eye(2**n_qubits)))
```

### Technique 4: Logging & Debugging

```python
import logging

# Enable Qiskit logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('qiskit')
logger.setLevel(logging.DEBUG)

# Run with debug output
job = simulator.run(qc, shots=1024)
```

### Technique 5: Step-by-Step Execution

```python
# Build circuit incrementally
qc = QuantumCircuit(2, 2)

# Step 1: Add gates
qc.h(0)
print("After Hadamard:", qc)

# Step 2: Check statevector
sv = Statevector.from_instruction(qc)
print("Statevector:", sv)

# Step 3: Add more gates
qc.cx(0, 1)
print("After CNOT:", qc)

# Step 4: Measure
qc.measure([0, 1], [0, 1])
print("Final circuit:", qc)

# Step 5: Simulate
simulator = AerSimulator()
job = simulator.run(qc, shots=1024)
result = job.result()
print("Results:", result.get_counts(qc))
```

---

## Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `IndexError: qubit index out of bounds` | Accessing non-existent qubit | Increase circuit size |
| `ValueError: Duplicate parameter names` | Same parameter name used twice | Use unique parameter names |
| `QiskitError: No simulator backend found` | Aer not installed | `pip install qiskit-aer` |
| `MemoryError` | Too many qubits for state vector | Use qasm simulator or reduce qubits |
| `IBMBackendError: No backend available` | Backend offline or overloaded | Use simulator or wait |
| `ValueError: Cannot bind parameters` | Missing parameter values | Provide all parameter values |
| `TranspilerError: Unable to translate` | Circuit incompatible with backend | Optimize or use different backend |

---

## Performance Optimization

### Quick Optimization Checklist

- [ ] Use `qasm_simulator` for > 20 qubits
- [ ] Reduce shot count for development
- [ ] Optimize circuit depth before execution
- [ ] Use parameter binding instead of rebuilding circuits
- [ ] Batch multiple circuits for execution
- [ ] Cache results when possible
- [ ] Use GPU acceleration if available
- [ ] Profile code to find bottlenecks

### Profiling Example

```python
import time
import cProfile
import pstats

def profile_simulation():
    cProfile.run('simulate_circuit()', 'profile_stats')
    
    stats = pstats.Stats('profile_stats')
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # Top 10 functions

profile_simulation()
```

---

## Getting Help

### Resources
- **[Qiskit Documentation](https://qiskit.org/documentation/)** - Official docs
- **[Stack Overflow](https://stackoverflow.com/questions/tagged/qiskit)** - Q&A
- **[GitHub Issues](https://github.com/Qiskit/qiskit/issues)** - Bug reports
- **[Qiskit Slack](https://qiskit.slack.com/)** - Community chat

### Effective Bug Reports
Include:
1. Minimal reproducible example
2. Full error traceback
3. Qiskit version: `qiskit.__version__`
4. Python version: `python --version`
5. Operating system
6. Expected vs actual behavior

This guide covers the most common issues and debugging techniques for quantum computing with Qiskit.
