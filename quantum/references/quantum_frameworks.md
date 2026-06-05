# Quantum Computing Frameworks Comparison

Complete guide to choosing and using different quantum computing frameworks: Qiskit, Cirq, PennyLane, Q#, and TensorFlow Quantum.

## Framework Overview

| Framework | Developer | Primary Use | Hardware | Maturity |
|-----------|-----------|------------|----------|----------|
| **Qiskit** | IBM | Production, research, ML | IBM, IonQ, Rigetti | Mature |
| **Cirq** | Google | NISQ algorithms | Google, IonQ | Mature |
| **PennyLane** | Xanadu | Quantum ML, optimization | Hardware-agnostic | Growing |
| **Q#** | Microsoft | Algorithm development | Azure Quantum | Mature |
| **TensorFlow Quantum** | Google + TensorFlow | Hybrid ML | Cirq backends | Growing |

---

## Qiskit (IBM)

### Strengths
- **Hardware integration**: Direct access to IBM quantum computers
- **Comprehensive ecosystem**: ML, nature, optimization, finance modules
- **Production-ready**: Used in industry and research
- **Documentation**: Extensive tutorials and textbook
- **Community**: Largest quantum computing community

### Weaknesses
- **Learning curve**: More complex API
- **Dependencies**: Heavier installation
- **Verbosity**: More code for simple tasks

### Best For
- Production quantum applications
- IBM hardware users
- Comprehensive quantum research
- Quantum machine learning

### Installation
```bash
pip install qiskit qiskit-aer qiskit-ibm-runtime
```

### Quick Example
```python
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator

# Create circuit
qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])

# Simulate
simulator = AerSimulator()
job = simulator.run(qc, shots=1024)
result = job.result()
print(result.get_counts(qc))
```

### Key Modules
- **qiskit.circuit**: Circuit construction
- **qiskit.transpiler**: Optimization and compilation
- **qiskit_aer**: High-performance simulator
- **qiskit_machine_learning**: ML algorithms
- **qiskit_nature**: Chemistry simulations
- **qiskit_optimization**: Optimization problems
- **qiskit_finance**: Financial applications

---

## Cirq (Google)

### Strengths
- **Simplicity**: Clean, Pythonic API
- **NISQ focus**: Designed for near-term devices
- **Google hardware**: Direct access to Google quantum chips
- **Lightweight**: Minimal dependencies
- **Good documentation**: Clear examples

### Weaknesses
- **Limited ML**: Less ML support than Qiskit
- **Smaller ecosystem**: Fewer pre-built algorithms
- **Community**: Smaller than Qiskit

### Best For
- Google hardware users
- NISQ algorithm development
- Lightweight quantum simulations
- Educational purposes

### Installation
```bash
pip install cirq
```

### Quick Example
```python
import cirq

q0, q1 = cirq.LineQubit.range(2)
circuit = cirq.Circuit(
    cirq.H(q0),
    cirq.CNOT(q0, q1),
    cirq.measure(q0, q1, key='result')
)

simulator = cirq.Simulator()
result = simulator.simulate(circuit, repetitions=1024)
print(result.measurements['result'])
```

### Key Features
- **LineQubit**: Simple qubit addressing
- **Circuit**: Intuitive circuit construction
- **Simulator**: Fast simulation
- **Optimization**: Circuit optimization passes
- **Devices**: Google device simulation

---

## PennyLane (Xanadu)

### Strengths
- **Hardware-agnostic**: Works with multiple backends
- **ML focus**: Excellent for quantum ML
- **Automatic differentiation**: Built-in gradient computation
- **Clean API**: Decorator-based circuit definition
- **Hybrid**: Seamless classical-quantum integration

### Weaknesses
- **Smaller community**: Fewer resources
- **Limited algorithms**: Fewer pre-built algorithms
- **Maturity**: Newer than Qiskit/Cirq

### Best For
- Quantum machine learning
- Variational algorithms
- Hybrid classical-quantum workflows
- Automatic differentiation

### Installation
```bash
pip install pennylane
```

### Quick Example
```python
import pennylane as qml
from pennylane import numpy as np

dev = qml.device('default.qubit', wires=2)

@qml.qnode(dev)
def circuit(params):
    qml.Hadamard(wires=0)
    qml.CNOT(wires=[0, 1])
    return qml.probs(wires=[0, 1])

params = np.array([0.1, 0.2])
print(circuit(params))
```

### Key Features
- **@qml.qnode**: Decorator for quantum functions
- **Automatic differentiation**: Compute gradients
- **Multiple backends**: Qiskit, Cirq, IonQ, etc.
- **Plugins**: Hardware-specific plugins
- **Optimization**: Built-in optimizers

---

## Q# (Microsoft)

### Strengths
- **Strong type system**: Compile-time error checking
- **Resource estimation**: Predict quantum resource requirements
- **Azure integration**: Cloud quantum computing
- **Algorithm development**: Good for algorithm research
- **Documentation**: Comprehensive learning resources

### Weaknesses
- **Not Python**: Different language paradigm
- **Smaller community**: Fewer resources than Qiskit
- **Limited ML**: Less ML support
- **Learning curve**: New language to learn

### Best For
- Microsoft Azure Quantum users
- Algorithm development
- Resource estimation
- Educational purposes

### Installation
```bash
dotnet add package Microsoft.Quantum.SDK
```

### Quick Example
```qsharp
namespace QuantumProgram {
    open Microsoft.Quantum.Intrinsic;
    
    operation BellState() : (Result, Result) {
        use q0 = Qubit();
        use q1 = Qubit();
        
        H(q0);
        CNOT(q0, q1);
        
        let r0 = M(q0);
        let r1 = M(q1);
        
        Reset(q0);
        Reset(q1);
        
        return (r0, r1);
    }
}
```

### Key Features
- **Type system**: Strong typing
- **Resource estimation**: Predict requirements
- **IonQ integration**: Access to IonQ hardware
- **QIR**: Quantum Intermediate Representation
- **Debugging**: Built-in debugging tools

---

## TensorFlow Quantum (Google)

### Strengths
- **TensorFlow integration**: Seamless ML workflow
- **Hybrid models**: Easy classical-quantum combinations
- **GPU acceleration**: Leverage GPU for classical parts
- **Scalability**: Train on large datasets
- **Production-ready**: Google-backed

### Weaknesses
- **Cirq-based**: Limited to Cirq backends
- **Requires TensorFlow**: Learning curve
- **Less mature**: Newer than Qiskit
- **Limited algorithms**: Fewer pre-built algorithms

### Best For
- Quantum machine learning
- Hybrid classical-quantum models
- TensorFlow users
- Production ML systems

### Installation
```bash
pip install tensorflow-quantum
```

### Quick Example
```python
import tensorflow_quantum as tfq
import tensorflow as tf
import cirq

q0, q1 = cirq.LineQubit.range(2)
circuit = cirq.Circuit(
    cirq.H(q0),
    cirq.CNOT(q0, q1)
)

# Convert to TFQ
circuit_tensor = tfq.convert_to_tensor([circuit])

# Use in TensorFlow model
model = tf.keras.Sequential([
    tfq.layers.PQC(circuit, operators=[cirq.Z(q0)])
])
```

### Key Features
- **PQC layer**: Parameterized quantum circuit layer
- **Hybrid models**: Combine quantum + classical
- **Gradient computation**: Automatic differentiation
- **GPU support**: Leverage GPU acceleration
- **Scalability**: Train on large datasets

---

## Framework Comparison Table

### Installation Size
| Framework | Size | Dependencies |
|-----------|------|--------------|
| Qiskit | ~500MB | Heavy |
| Cirq | ~100MB | Light |
| PennyLane | ~50MB | Light |
| Q# | ~200MB | Moderate |
| TensorFlow Quantum | ~200MB | Heavy (TensorFlow) |

### Learning Curve
| Framework | Difficulty | Time to First Circuit |
|-----------|-----------|----------------------|
| Qiskit | Moderate-High | 30 min |
| Cirq | Low-Moderate | 10 min |
| PennyLane | Low | 15 min |
| Q# | Moderate | 20 min |
| TensorFlow Quantum | Moderate-High | 30 min |

### Community & Support
| Framework | Community Size | Documentation | Stack Overflow |
|-----------|----------------|---------------|-----------------|
| Qiskit | Very Large | Excellent | Extensive |
| Cirq | Large | Good | Moderate |
| PennyLane | Growing | Good | Growing |
| Q# | Moderate | Excellent | Moderate |
| TensorFlow Quantum | Moderate | Good | Moderate |

### Hardware Support
| Framework | Hardware | Integration |
|-----------|----------|-------------|
| Qiskit | IBM, IonQ, Rigetti | Direct API |
| Cirq | Google, IonQ | Direct API |
| PennyLane | Multiple | Plugin system |
| Q# | Azure Quantum | Cloud service |
| TensorFlow Quantum | Cirq backends | Cirq-based |

---

## Choosing a Framework

### Decision Tree

**Q1: Do you need ML?**
- **Yes** → Consider PennyLane or TensorFlow Quantum
- **No** → Continue to Q2

**Q2: Which hardware?**
- **IBM** → Qiskit
- **Google** → Cirq or TensorFlow Quantum
- **Microsoft** → Q#
- **Multiple** → PennyLane

**Q3: Priority?**
- **Production** → Qiskit
- **Simplicity** → Cirq
- **ML** → PennyLane or TensorFlow Quantum
- **Learning** → Cirq or PennyLane

### Recommendation Matrix

| Use Case | Framework | Reason |
|----------|-----------|--------|
| IBM hardware | Qiskit | Native integration |
| Google hardware | Cirq | Native integration |
| Quantum ML | PennyLane | Best ML support |
| Hybrid ML | TensorFlow Quantum | TensorFlow integration |
| Algorithm R&D | Qiskit or Cirq | Comprehensive tools |
| Learning | Cirq or PennyLane | Simple API |
| Production | Qiskit | Mature, supported |
| Azure Quantum | Q# | Native integration |

---

## Interoperability

### Converting Between Frameworks

**Qiskit → Cirq**
```python
from qiskit import QuantumCircuit
import cirq

# Create Qiskit circuit
qiskit_qc = QuantumCircuit(2)
qiskit_qc.h(0)

# Convert to Cirq (manual)
q0, q1 = cirq.LineQubit.range(2)
cirq_circuit = cirq.Circuit(cirq.H(q0))
```

**Cirq → PennyLane**
```python
import cirq
import pennylane as qml

# Create Cirq circuit
q0, q1 = cirq.LineQubit.range(2)
cirq_circuit = cirq.Circuit(cirq.H(q0))

# Use with PennyLane device
dev = qml.device('cirq.simulator', wires=2)
```

### Common Patterns

All frameworks support:
- Quantum gates (H, X, Y, Z, RX, RY, RZ, CNOT, etc.)
- Measurements
- Parameterized circuits
- Simulation
- Transpilation/optimization

---

## Performance Comparison

### Simulation Speed (Bell State, 1000 shots)
- Qiskit Aer: ~50ms
- Cirq: ~30ms
- PennyLane: ~40ms
- TensorFlow Quantum: ~100ms (includes TensorFlow overhead)

### Scalability
- **Qiskit**: Up to 30 qubits (Aer)
- **Cirq**: Up to 25 qubits
- **PennyLane**: Up to 20 qubits (backend-dependent)
- **TensorFlow Quantum**: Up to 20 qubits

### Memory Usage
- **Qiskit**: ~8GB for 30 qubits
- **Cirq**: ~4GB for 25 qubits
- **PennyLane**: ~2GB for 20 qubits
- **TensorFlow Quantum**: ~6GB for 20 qubits

---

## Hybrid Workflows

### Qiskit + PennyLane
```python
# Use Qiskit for circuit, PennyLane for ML
import pennylane as qml
from pennylane_qiskit import QiskitDevice

dev = QiskitDevice(device='qasm_simulator', wires=2)

@qml.qnode(dev)
def circuit(params):
    qml.RY(params[0], wires=0)
    qml.CNOT(wires=[0, 1])
    return qml.expval(qml.PauliZ(0))
```

### Cirq + TensorFlow Quantum
```python
import tensorflow_quantum as tfq
import cirq
import tensorflow as tf

q0, q1 = cirq.LineQubit.range(2)
circuit = cirq.Circuit(cirq.H(q0), cirq.CNOT(q0, q1))

# Use in TensorFlow model
model = tf.keras.Sequential([
    tfq.layers.PQC(circuit, [cirq.Z(q0)])
])
```

---

## Resources

### Official Documentation
- Qiskit: https://qiskit.org/documentation/
- Cirq: https://quantumai.google/cirq
- PennyLane: https://pennylane.ai/
- Q#: https://learn.microsoft.com/en-us/azure/quantum/
- TensorFlow Quantum: https://www.tensorflow.org/quantum

### Tutorials
- Qiskit Textbook: https://qiskit.org/textbook
- Cirq Tutorials: https://quantumai.google/cirq/tutorials
- PennyLane Demos: https://pennylane.ai/qml/demos/
- Q# Learning Path: https://learn.microsoft.com/en-us/training/paths/quantum-computing-fundamentals/

### Community
- Qiskit Community: https://qiskit.org/community
- Cirq Community: https://github.com/quantumlib/Cirq
- PennyLane Discourse: https://discuss.pennylane.ai/
- Q# Community: https://github.com/microsoft/QuantumKatas

---

## Key Takeaways

1. **Qiskit**: Best for production and IBM hardware
2. **Cirq**: Best for simplicity and Google hardware
3. **PennyLane**: Best for quantum ML and variational algorithms
4. **Q#**: Best for Microsoft Azure and algorithm development
5. **TensorFlow Quantum**: Best for hybrid ML workflows

Choose based on:
- **Hardware preference**: IBM → Qiskit, Google → Cirq
- **Use case**: ML → PennyLane, Production → Qiskit
- **Learning style**: Simple → Cirq, Comprehensive → Qiskit
- **Ecosystem**: ML → TensorFlow Quantum, Algorithms → Qiskit
