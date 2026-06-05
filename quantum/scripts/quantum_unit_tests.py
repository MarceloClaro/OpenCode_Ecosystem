import unittest
import numpy as np
import pennylane as qml

class TestQuantumCircuits(unittest.TestCase):
    """
    Suíte de testes de unidade para circuitos quânticos.
    Baseado na pirâmide de testes do projeto_tests_kit.
    """

    def setUp(self):
        self.dev = qml.device("default.qubit", wires=2)

    def test_bell_state_entanglement(self):
        """Teste de Unidade: Verifica se o estado de Bell gera emaranhamento correto."""
        @qml.qnode(self.dev)
        def bell_circuit():
            qml.Hadamard(wires=0)
            qml.CNOT(wires=[0, 1])
            return qml.probs(wires=[0, 1])
        
        probs = bell_circuit()
        # No estado de Bell (|00> + |11>)/sqrt(2), as probabilidades de |01> e |10> devem ser 0
        self.assertAlmostEqual(probs[1], 0.0, places=5)
        self.assertAlmostEqual(probs[2], 0.0, places=5)
        # Probabilidades de |00> e |11> devem ser ~0.5
        self.assertAlmostEqual(probs[0], 0.5, places=5)
        self.assertAlmostEqual(probs[3], 0.5, places=5)

    def test_rotation_gate(self):
        """Teste de Unidade: Verifica a precisão de uma porta de rotação RY."""
        @qml.qnode(self.dev)
        def rotation_circuit(phi):
            qml.RY(phi, wires=0)
            return qml.expval(qml.PauliZ(0))
        
        # RY(pi) deve levar |0> para |1>, então expval(Z) deve ser -1
        self.assertAlmostEqual(rotation_circuit(np.pi), -1.0, places=5)
        # RY(2*pi) deve retornar para |0>, então expval(Z) deve ser 1
        self.assertAlmostEqual(rotation_circuit(2*np.pi), 1.0, places=5)

if __name__ == "__main__":
    unittest.main()
