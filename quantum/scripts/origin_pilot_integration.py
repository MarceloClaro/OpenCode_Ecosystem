#!/usr/bin/env python3
"""
Origin Pilot Integration Script
Integração com Origin Pilot - SO Quântico Chinês Open-Source

Este script demonstra como usar Origin Pilot com o skill de computação quântica.
"""

import sys
import subprocess
from pathlib import Path

def print_header(title):
    """Imprimir cabeçalho formatado."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def print_section(title):
    """Imprimir seção formatada."""
    print(f"\n{'─'*70}")
    print(f"  {title}")
    print(f"{'─'*70}\n")

def check_origin_pilot_installed():
    """Verificar se Origin Pilot está instalado."""
    try:
        import origin_pilot
        print(f"✓ Origin Pilot instalado: v{origin_pilot.__version__}")
        return True
    except ImportError:
        print("✗ Origin Pilot não está instalado")
        return False

def install_origin_pilot():
    """Instalar Origin Pilot."""
    print_section("Instalando Origin Pilot")
    
    print("Clonando repositório...")
    subprocess.run([
        "git", "clone", 
        "https://github.com/origin-quantum/origin-pilot"
    ], check=True)
    
    print("\nInstalando dependências...")
    subprocess.run([
        "pip", "install", "-r", 
        "origin-pilot/requirements.txt"
    ], check=True)
    
    print("\nInstalando Origin Pilot...")
    subprocess.run([
        "pip", "install", "-e", "origin-pilot"
    ], check=True)
    
    print("\n✓ Origin Pilot instalado com sucesso!")

def demo_basic_circuit():
    """Demonstração: Circuito quântico básico com Origin Pilot."""
    print_section("Demonstração 1: Circuito Quântico Básico")
    
    try:
        from origin_pilot import QuantumCircuit, QuantumKernel
        
        print("Criando circuito quântico...")
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure_all()
        
        print("Circuito criado:")
        print(qc)
        
        print("\nExecutando circuito...")
        kernel = QuantumKernel()
        result = kernel.run(qc, shots=1000)
        
        print("\nResultados:")
        counts = result.get_counts()
        for state, count in sorted(counts.items()):
            print(f"  {state}: {count} ({count/10:.1f}%)")
        
        return True
    except Exception as e:
        print(f"✗ Erro: {e}")
        return False

def demo_vqe():
    """Demonstração: Variational Quantum Eigensolver (VQE)."""
    print_section("Demonstração 2: Variational Quantum Eigensolver (VQE)")
    
    try:
        from origin_pilot import VQE, QuantumCircuit
        from origin_pilot.ansatz import RealAmplitudes
        import numpy as np
        
        print("Definindo Hamiltonian...")
        H = np.array([[1, 0], [0, -1]])
        
        print("Criando ansatz...")
        ansatz = RealAmplitudes(n_qubits=2, reps=1)
        
        print("Criando VQE...")
        vqe = VQE(ansatz, H)
        
        print("Otimizando...")
        result = vqe.run()
        
        print(f"\nEnergia mínima encontrada: {result.eigenvalue:.6f}")
        print(f"Parâmetros ótimos: {result.x}")
        
        return True
    except Exception as e:
        print(f"✗ Erro: {e}")
        return False

def demo_quantum_classifier():
    """Demonstração: Classificador Quântico."""
    print_section("Demonstração 3: Classificador Quântico")
    
    try:
        from origin_pilot import QuantumClassifier
        from origin_pilot.feature_maps import AngleEncoding
        import numpy as np
        
        print("Gerando dados de treinamento...")
        X_train = np.array([
            [0.5, 0.5],
            [1.0, 1.0],
            [0.2, 0.8],
            [0.9, 0.1]
        ])
        y_train = np.array([0, 1, 0, 1])
        
        print("Criando feature map...")
        feature_map = AngleEncoding(n_qubits=2)
        
        print("Criando classificador...")
        classifier = QuantumClassifier(feature_map)
        
        print("Treinando...")
        classifier.fit(X_train, y_train)
        
        print("Fazendo predições...")
        predictions = classifier.predict(X_train)
        
        print("\nPredições:")
        for i, (pred, true) in enumerate(zip(predictions, y_train)):
            match = "✓" if pred == true else "✗"
            print(f"  Amostra {i}: Predito={pred}, Real={true} {match}")
        
        accuracy = np.mean(predictions == y_train)
        print(f"\nAcurácia: {accuracy*100:.1f}%")
        
        return True
    except Exception as e:
        print(f"✗ Erro: {e}")
        return False

def demo_task_scheduler():
    """Demonstração: Escalonador de Tarefas."""
    print_section("Demonstração 4: Escalonador de Tarefas")
    
    try:
        from origin_pilot import TaskScheduler, QuantumCircuit
        
        print("Criando escalonador...")
        scheduler = TaskScheduler()
        
        print("Criando múltiplas tarefas...")
        task_ids = []
        for i in range(3):
            qc = QuantumCircuit(2)
            qc.h(0)
            qc.rx(i * 0.1, 1)
            qc.measure_all()
            
            task_id = scheduler.add_task(qc, priority=i)
            task_ids.append(task_id)
            print(f"  Tarefa {i+1} adicionada (ID: {task_id})")
        
        print("\nExecutando todas as tarefas...")
        results = scheduler.run()
        
        print("\nResultados:")
        for i, result in enumerate(results):
            counts = result.get_counts()
            print(f"  Tarefa {i+1}: {counts}")
        
        return True
    except Exception as e:
        print(f"✗ Erro: {e}")
        return False

def compare_frameworks():
    """Comparar Origin Pilot com outros frameworks."""
    print_section("Comparação: Origin Pilot vs Outros Frameworks")
    
    comparison = """
    ┌─────────────────────┬──────────────┬────────┬────────┬────────────┐
    │ Aspecto             │ Origin Pilot │ Qiskit │ Cirq   │ PennyLane  │
    ├─────────────────────┼──────────────┼────────┼────────┼────────────┤
    │ Tipo                │ SO Quântico  │ Fwk    │ Fwk    │ Fwk        │
    │ Origem              │ China        │ IBM    │ Google │ Xanadu     │
    │ Open-Source         │ ✓            │ ✓      │ ✓      │ ✓          │
    │ Gerenciamento Qubits│ ✓ (Nativo)   │ ✗      │ ✗      │ ✗          │
    │ Escalonamento       │ ✓ (Nativo)   │ ✗      │ ✗      │ ✗          │
    │ Integração IA       │ ✓ (Nativo)   │ ✗      │ ✗      │ ✓          │
    │ Multi-Plataforma    │ ✓            │ ✓      │ ✓      │ ✓          │
    │ Comunidade          │ Emergente    │ Grande │ Grande │ Média      │
    │ Documentação        │ Chinês/Ing   │ Excelente│Excelente│Excelente │
    └─────────────────────┴──────────────┴────────┴────────┴────────────┘
    """
    print(comparison)

def show_resources():
    """Mostrar recursos do Origin Pilot."""
    print_section("Recursos do Origin Pilot")
    
    resources = """
    📚 Documentação Oficial
    ├─ GitHub: https://github.com/origin-quantum/origin-pilot
    ├─ Docs: https://origin-pilot.readthedocs.io
    └─ Issues: https://github.com/origin-quantum/origin-pilot/issues
    
    🎓 Tutoriais e Exemplos
    ├─ Quick Start: https://github.com/origin-quantum/origin-pilot#quick-start
    ├─ Exemplos: /examples no repositório
    └─ Notebooks: Jupyter notebooks com exemplos
    
    👥 Comunidade
    ├─ Discussões: GitHub Discussions
    ├─ Slack: Canal da comunidade
    └─ Conferências: QuantumBit MEET, Quantum Summit
    
    🔗 Integração com Outros Frameworks
    ├─ Qiskit: Compatível via adaptadores
    ├─ Cirq: Suporte em desenvolvimento
    └─ PennyLane: Integração planejada
    """
    print(resources)

def show_menu():
    """Mostrar menu interativo."""
    print_header("Origin Pilot Integration - Menu Interativo")
    
    menu_options = """
    1. Verificar instalação do Origin Pilot
    2. Instalar Origin Pilot
    3. Demonstração 1: Circuito Quântico Básico
    4. Demonstração 2: Variational Quantum Eigensolver (VQE)
    5. Demonstração 3: Classificador Quântico
    6. Demonstração 4: Escalonador de Tarefas
    7. Comparar Origin Pilot com outros frameworks
    8. Mostrar recursos
    9. Sair
    """
    print(menu_options)

def main():
    """Função principal."""
    print_header("Origin Pilot Integration Script")
    print("Integração com Origin Pilot - SO Quântico Chinês Open-Source\n")
    
    while True:
        show_menu()
        
        try:
            choice = input("Selecione uma opção (1-9): ").strip()
            
            if choice == "1":
                check_origin_pilot_installed()
            
            elif choice == "2":
                install_origin_pilot()
            
            elif choice == "3":
                if check_origin_pilot_installed():
                    demo_basic_circuit()
                else:
                    print("Por favor, instale Origin Pilot primeiro (opção 2)")
            
            elif choice == "4":
                if check_origin_pilot_installed():
                    demo_vqe()
                else:
                    print("Por favor, instale Origin Pilot primeiro (opção 2)")
            
            elif choice == "5":
                if check_origin_pilot_installed():
                    demo_quantum_classifier()
                else:
                    print("Por favor, instale Origin Pilot primeiro (opção 2)")
            
            elif choice == "6":
                if check_origin_pilot_installed():
                    demo_task_scheduler()
                else:
                    print("Por favor, instale Origin Pilot primeiro (opção 2)")
            
            elif choice == "7":
                compare_frameworks()
            
            elif choice == "8":
                show_resources()
            
            elif choice == "9":
                print("\n👋 Até logo!\n")
                break
            
            else:
                print("❌ Opção inválida. Por favor, tente novamente.")
        
        except KeyboardInterrupt:
            print("\n\n👋 Até logo!\n")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
