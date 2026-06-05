# Quantum Machine Learning (QML)

Quantum machine learning combines quantum computing with machine learning algorithms. This reference covers core concepts, algorithms, and implementation patterns.

## Core Concepts

### Quantum States as Data
- **Classical data**: Encoded into quantum states via feature maps
- **Quantum advantage**: Access to exponentially large Hilbert space
- **Measurement**: Collapse quantum state to classical output

### Feature Maps
Feature maps encode classical data into quantum states. Key properties:

| Map Type | Encoding | Complexity | Use Case |
|----------|----------|-----------|----------|
| **Angle** | RY(x_i) on qubit i | O(n) gates | Simple, interpretable |
| **Amplitude** | Data in amplitudes | O(log n) qubits | Dense encoding |
| **IQP** | Polynomial interactions | O(n²) gates | Expressive, entangled |
| **ZZ** | ZZ interactions | O(n²) gates | Classification |
| **Basis** | Binary in computational basis | O(n) gates | Discrete data |

### Quantum Kernels
Quantum kernels compute similarity between data points:

```
K(x, x') = |⟨ψ(x)|ψ(x')⟩|²
```

Where |ψ(x)⟩ is the quantum state encoding x.

**Properties**:
- Always positive semi-definite
- Symmetric: K(x, x') = K(x', x)
- Diagonal: K(x, x) = 1 (for normalized states)
- Captures quantum advantage through entanglement

## Quantum Algorithms for ML

### 1. Quantum Support Vector Machine (QSVM)

**Concept**: Use quantum kernel to compute similarity matrix for SVM.

**Workflow**:
1. Encode training data using feature map
2. Compute quantum kernel matrix K
3. Train classical SVM with kernel K
4. Classify new points using quantum kernel

**Advantages**:
- Potentially exponential speedup for kernel computation
- Access to high-dimensional feature space
- Can capture non-linear patterns

**Implementation**:
```python
from quantum_classifier import QuantumKernel
import numpy as np

# Create kernel
qkernel = QuantumKernel(n_qubits=2, feature_map='angle')

# Compute kernel matrix
X_train = np.array([[0.5, 0.5], [1.0, 1.0], [2.0, 2.0]])
K = qkernel.compute_kernel_matrix(X_train)

# Use with classical SVM
from sklearn.svm import SVC
svm = SVC(kernel='precomputed')
svm.fit(K, y_train)
```

**Challenges**:
- Barren plateaus: Gradients vanish in high dimensions
- Noise: Current hardware has high error rates
- Scalability: Kernel computation grows with data size

---

### 2. Quantum Neural Networks (QNN)

**Concept**: Parameterized quantum circuits trained with classical optimization.

**Architecture**:
```
Input → Feature Encoding → Variational Ansatz → Measurement → Output
```

**Components**:

1. **Feature Encoding**: Map classical input to quantum state
2. **Variational Ansatz**: Trainable quantum circuit with parameters θ
3. **Measurement**: Extract classical output (expectation value or probability)

**Ansatz Design**:
```python
# Typical pattern: alternating rotation and entanglement layers
for layer in range(n_layers):
    # Rotation layer
    for qubit in range(n_qubits):
        circuit.ry(params[idx], qubit)
        idx += 1
    
    # Entanglement layer
    for i in range(n_qubits - 1):
        circuit.cx(i, i + 1)
    
    # Another rotation layer
    for qubit in range(n_qubits):
        circuit.rz(params[idx], qubit)
        idx += 1
```

**Training**:
```python
from scipy.optimize import minimize

def cost_function(params):
    predictions = [qnn.predict(x, params) for x in X_train]
    loss = np.mean((predictions - y_train)**2)
    return loss

result = minimize(cost_function, x0=initial_params, method='COBYLA')
```

**Advantages**:
- Flexible architecture
- Can express complex decision boundaries
- Hybrid classical-quantum approach

**Challenges**:
- Barren plateaus: Training becomes difficult
- Vanishing gradients: Hard to optimize
- Limited expressivity: May not learn complex patterns

---

### 3. Quantum Principal Component Analysis (qPCA)

**Concept**: Use quantum computer to find principal components of data.

**Quantum advantage**: Potential exponential speedup for high-dimensional data.

**Algorithm**:
1. Encode data into quantum states
2. Apply quantum phase estimation
3. Extract eigenvalues (principal components)
4. Classically process results

---

### 4. Quantum Generative Models

**Variational Quantum Boltzmann Machine (VQBM)**:
- Generative model using quantum circuits
- Learn probability distribution of training data
- Sample new data points

**Quantum Autoencoder**:
- Compress high-dimensional data to low-dimensional latent space
- Quantum encoder + classical decoder
- Useful for feature extraction

---

## Feature Map Comparison

### Angle Encoding
```python
# Simplest encoding: RY(x_i) on qubit i
for i, xi in enumerate(x):
    circuit.ry(xi, i)
```

**Pros**: Simple, fast, interpretable
**Cons**: Limited expressivity, shallow feature space

### Amplitude Encoding
```python
# Encode data in amplitudes
circuit.initialize(x / np.linalg.norm(x), qubits)
```

**Pros**: Exponential compression, dense encoding
**Cons**: Requires normalized data, initialization overhead

### IQP Encoding
```python
# Instantaneous Quantum Polynomial
for rep in range(reps):
    for i in range(n_qubits):
        circuit.h(i)
        circuit.ry(x[i], i)
    for i in range(n_qubits - 1):
        circuit.cx(i, i + 1)
```

**Pros**: Highly expressive, creates entanglement
**Cons**: More gates, deeper circuits, noisier

### ZZ Feature Map
```python
# ZZ interactions for classification
for i in range(n_qubits):
    circuit.ry(x[i], i)
for i in range(n_qubits - 1):
    circuit.rzz(x[i] * x[i + 1], i, i + 1)
```

**Pros**: Good for classification, captures interactions
**Cons**: Requires feature scaling

---

## Barren Plateaus Problem

**Issue**: Gradients vanish in high-dimensional parameter spaces, making training impossible.

**Manifestation**:
```
∂L/∂θ ≈ 0 everywhere → No gradient signal for optimization
```

**Causes**:
- Random initialization in high dimensions
- Overly expressive ansätze
- Poor feature map design

**Solutions**:
1. **Careful initialization**: Start near solution
2. **Shallow circuits**: Reduce parameter count
3. **Problem-inspired ansätze**: Design circuits for specific problems
4. **Layerwise training**: Train layers sequentially
5. **Quantum natural gradient**: Use better optimization methods

---

## Quantum Advantage in ML

### When Quantum Helps
1. **High-dimensional data**: Exponential Hilbert space
2. **Non-linear patterns**: Quantum kernels capture complex relationships
3. **Specific problem structures**: Tailored quantum algorithms

### Current Limitations (NISQ Era)
1. **Noise**: Error rates limit circuit depth
2. **Scalability**: Few qubits available
3. **Barren plateaus**: Training is difficult
4. **Measurement overhead**: Extracting classical info is expensive

### Realistic Expectations
- **Near-term**: Hybrid algorithms, small datasets
- **Medium-term**: Quantum-enhanced classical ML
- **Long-term**: Quantum-dominant algorithms (with error correction)

---

## Implementation Patterns

### Pattern 1: Quantum Kernel SVM
```python
# 1. Create quantum kernel
qkernel = QuantumKernel(n_qubits=4, feature_map='iqp')

# 2. Compute kernel matrix for training data
K_train = qkernel.compute_kernel_matrix(X_train)

# 3. Train SVM with quantum kernel
from sklearn.svm import SVC
svm = SVC(kernel='precomputed')
svm.fit(K_train, y_train)

# 4. Predict on test data
K_test = np.array([
    [qkernel.compute_kernel(x_test, x_train_i) 
     for x_train_i in X_train]
])
predictions = svm.predict(K_test)
```

### Pattern 2: Variational Quantum Classifier
```python
# 1. Initialize QNN
qnn = QuantumNeuralNetwork(n_qubits=3, n_layers=2)
params = qnn.initialize_params()

# 2. Define cost function
def cost_fn(params):
    predictions = [qnn.predict(x, params) for x in X_train]
    return np.mean((predictions - y_train)**2)

# 3. Optimize parameters
from scipy.optimize import minimize
result = minimize(cost_fn, params, method='COBYLA')

# 4. Make predictions
trained_params = result.x
predictions = [qnn.predict(x, trained_params) for x in X_test]
```

### Pattern 3: Hybrid Quantum-Classical
```python
# Quantum part: feature extraction
qnn_encoder = QuantumNeuralNetwork(n_qubits=4, n_layers=1)
encoded_features = [qnn_encoder.predict(x, params) for x in X]

# Classical part: classification
from sklearn.ensemble import RandomForestClassifier
clf = RandomForestClassifier()
clf.fit(encoded_features, y_train)
```

---

## Benchmarking QML

### Metrics
1. **Accuracy**: Classification accuracy on test set
2. **Training time**: Wall-clock time for optimization
3. **Quantum resources**: Number of qubits, circuit depth, gates
4. **Classical overhead**: Time for kernel computation

### Comparison Baseline
Always compare against:
- Classical ML (SVM, neural networks)
- Classical kernel methods
- Random classifier (baseline)

### Realistic Expectations
- Current NISQ devices: Comparable to classical, not better
- Advantage on specific problems: Possible with careful design
- Scaling: Quantum advantage emerges with larger systems (10+ years)

---

## Debugging QML

### Common Issues

**1. Poor Accuracy**
- Check feature map expressivity
- Verify data normalization
- Increase circuit depth
- Try different optimization methods

**2. Training Doesn't Converge**
- Barren plateau: Redesign ansatz
- Bad initialization: Use problem-inspired starting point
- Learning rate too high: Reduce step size

**3. Kernel Matrix Not Positive Definite**
- Numerical errors: Use higher precision
- Noise: Increase shots
- Feature map issue: Try different encoding

**4. Slow Execution**
- Reduce circuit depth
- Batch kernel computations
- Use simulators for development

---

## Resources

### Official Documentation
- Qiskit ML: https://qiskit-machine-learning.readthedocs.io/
- IBM Quantum: https://quantum.ibm.com/
- Qiskit Textbook (ML chapter): https://qiskit.org/textbook

### Papers
- "Quantum Machine Learning" - Schuld & Killoran (2022)
- "Barren plateaus in quantum neural network training landscapes" - McClean et al. (2018)
- "Quantum kernels using compact supposition" - Havlíček et al. (2019)

### Courses
- IBM Quantum Learning
- Coursera: Quantum Machine Learning
- MIT OpenCourseWare: Quantum Computing

---

## Key Takeaways

1. **Feature maps** are crucial: Choice significantly impacts performance
2. **Quantum kernels** offer potential advantage for similarity computation
3. **Barren plateaus** are real: Careful ansatz design is essential
4. **Hybrid approach** is practical: Combine quantum + classical strengths
5. **Realistic expectations**: Current systems are NISQ-era, not yet advantageous
6. **Problem-specific design**: Generic approaches often fail; tailor to problem
7. **Benchmarking matters**: Always compare against classical baselines
