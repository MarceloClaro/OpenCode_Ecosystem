import pennylane as qml
import numpy as np

def zne_mitigation(circuit_func, params, noise_strengths=[0.01, 0.05, 0.1]):
    """
    Demonstra a técnica de Zero Noise Extrapolation (ZNE) 
    para mitigar ruído em simulações quânticas.
    """
    results = []
    
    for strength in noise_strengths:
        # Definir dispositivo com ruído
        dev_noisy = qml.device("default.mixed", wires=2)
        
        @qml.qnode(dev_noisy)
        def noisy_circuit(p):
            circuit_func(p)
            # Aplicar ruído de despolarização
            for i in range(2):
                qml.DepolarizingChannel(strength, wires=i)
            return qml.expval(qml.PauliZ(0))
        
        results.append(noisy_circuit(params))
    
    # Extrapolação linear simples para ruído zero
    coeffs = np.polyfit(noise_strengths, results, 1)
    mitigated_val = coeffs[1] # Intercepto em x=0
    
    return mitigated_val, results

def example_circuit(params):
    qml.Hadamard(wires=0)
    qml.CNOT(wires=[0, 1])
    qml.RY(params[0], wires=0)

if __name__ == "__main__":
    params = [0.5]
    mitigated, noisy_vals = zne_mitigation(example_circuit, params)
    print(f"Valores ruidosos: {noisy_vals}")
    print(f"Valor mitigado (ZNE): {mitigated:.4f}")
