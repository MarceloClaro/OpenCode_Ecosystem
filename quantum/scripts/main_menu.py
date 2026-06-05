#!/usr/bin/env python3
"""
Quantum Computing Skill - Interactive Menu System

Main entry point for navigating all quantum computing resources and tools.
Supports: Learning, Development, Troubleshooting, Benchmarking, Resources
"""

import os
import sys
import subprocess
from typing import Callable, Dict, List
from enum import Enum

class UserLevel(Enum):
    """User experience levels."""
    BEGINNER = "Iniciante"
    INTERMEDIATE = "Intermediário"
    ADVANCED = "Avançado"
    RESEARCHER = "Pesquisador"

class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class QuantumComputingMenu:
    """Interactive menu system for quantum computing skill."""
    
    def __init__(self):
        self.user_level = None
        self.skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.scripts_dir = os.path.join(self.skill_dir, 'scripts')
        self.references_dir = os.path.join(self.skill_dir, 'references')
    
    def clear_screen(self):
        """Clear terminal screen."""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def print_header(self, title: str):
        """Print formatted header."""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}{title.center(70)}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.ENDC}\n")
    
    def print_menu(self, title: str, options: Dict[str, str]):
        """Print formatted menu with options."""
        self.print_header(title)
        for key, description in options.items():
            print(f"{Colors.GREEN}{key}{Colors.ENDC}. {description}")
        print(f"{Colors.YELLOW}0{Colors.ENDC}. Voltar")
        print(f"{Colors.RED}Q{Colors.ENDC}. Sair")
    
    def get_choice(self, valid_choices: List[str] = None) -> str:
        """Get user choice with validation."""
        while True:
            choice = input(f"\n{Colors.BOLD}Escolha uma opção: {Colors.ENDC}").strip().upper()
            
            if choice == 'Q':
                return 'Q'
            if choice == '0':
                return '0'
            if valid_choices is None or choice in valid_choices:
                return choice
            
            print(f"{Colors.RED}Opção inválida. Tente novamente.{Colors.ENDC}")
    
    def run_origin_pilot_integration(self):
        """Run Origin Pilot integration script."""
        script_path = os.path.join(self.scripts_dir, 'origin_pilot_integration.py')
        if os.path.exists(script_path):
            subprocess.run([sys.executable, script_path])
        else:
            print(f"{Colors.RED}Script não encontrado: {script_path}{Colors.ENDC}")
    
    def select_user_level(self):
        """Let user select their experience level."""
        self.print_header("Bem-vindo ao Skill de Computação Quântica")
        print(f"{Colors.BOLD}Qual é seu nível de experiência?{Colors.ENDC}\n")
        
        options = {
            '1': 'Iniciante - Novo em computação quântica',
            '2': 'Intermediário - Conhecimento básico',
            '3': 'Avançado - Experiência com frameworks',
            '4': 'Pesquisador - Desenvolvimento de pesquisa'
        }
        
        self.print_menu("Seleção de Nível", options)
        choice = self.get_choice(['1', '2', '3', '4'])
        
        if choice == 'Q':
            self.exit_program()
        
        level_map = {
            '1': UserLevel.BEGINNER,
            '2': UserLevel.INTERMEDIATE,
            '3': UserLevel.ADVANCED,
            '4': UserLevel.RESEARCHER
        }
        
        self.user_level = level_map[choice]
        print(f"\n{Colors.GREEN}✓ Nível selecionado: {self.user_level.value}{Colors.ENDC}")
        input("\nPressione Enter para continuar...")
    
    # ==================== Main Menu ====================
    
    def main_menu(self):
        """Main menu with all categories."""
        while True:
            self.clear_screen()
            self.print_header(f"Menu Principal - {self.user_level.value}")
            
            options = {
                '1': '📚 Aprendizado',
                '2': '🛠️  Desenvolvimento',
                '3': '🔧 Troubleshooting & Debugging',
                '4': '📊 Benchmarking',
                '5': '📖 Recursos Curados',
                '6': '⚙️  Configurações'
            }
            
            self.print_menu("Menu Principal", options)
            choice = self.get_choice(['1', '2', '3', '4', '5', '6'])
            
            if choice == 'Q':
                self.exit_program()
            elif choice == '1':
                self.learning_menu()
            elif choice == '2':
                self.development_menu()
            elif choice == '3':
                self.troubleshooting_menu()
            elif choice == '4':
                self.benchmarking_menu()
            elif choice == '5':
                self.resources_menu()
            elif choice == '6':
                self.settings_menu()
    
    # ==================== Learning Menu ====================
    
    def learning_menu(self):
        """Learning and education menu."""
        while True:
            self.clear_screen()
            self.print_header("📚 Aprendizado")
            
            options = {
                '1': 'Guia de Aprendizado Interativo',
                '2': 'Visualizar Caminho de Aprendizado',
                '3': 'Exercícios Kata-Style',
                '4': 'Auto-Avaliação',
                '5': 'Conceitos Fundamentais'
            }
            
            self.print_menu("Menu de Aprendizado", options)
            choice = self.get_choice(['1', '2', '3', '4', '5'])
            
            if choice == 'Q':
                self.exit_program()
            elif choice == '0':
                break
            elif choice == '1':
                self.run_script('learning_roadmap.py')
            elif choice == '2':
                self.view_reference('learning_path.md')
            elif choice == '3':
                self.show_exercises()
            elif choice == '4':
                self.self_assessment()
            elif choice == '5':
                self.view_reference('quantum_algorithms.md')
    
    def show_exercises(self):
        """Show available exercises."""
        self.clear_screen()
        self.print_header("Exercícios Kata-Style")
        
        print(f"{Colors.BOLD}Exercícios Disponíveis por Nível:{Colors.ENDC}\n")
        
        exercises = {
            'Level 1': [
                'Basic gates (H, X, Y, Z)',
                'Multi-qubit gates (CNOT, CZ)',
                'Bell states',
                'Superposition',
                'Measurement'
            ],
            'Level 2': [
                'Deutsch-Jozsa algorithm',
                'Grover search',
                'Quantum Fourier Transform',
                'Phase estimation',
                'Oracle design'
            ],
            'Level 3': [
                'Variational Quantum Eigensolver (VQE)',
                'Quantum Approximate Optimization (QAOA)',
                'Quantum Machine Learning',
                'Error correction',
                'Quantum simulation'
            ]
        }
        
        for level, exs in exercises.items():
            print(f"{Colors.CYAN}{level}:{Colors.ENDC}")
            for ex in exs:
                print(f"  • {ex}")
            print()
        
        print(f"{Colors.YELLOW}Dica: Leia 'learning_path.md' para exercícios detalhados com soluções.{Colors.ENDC}")
        input("\nPressione Enter para voltar...")
    
    def self_assessment(self):
        """Self-assessment quiz."""
        self.clear_screen()
        self.print_header("Auto-Avaliação")
        
        print(f"{Colors.BOLD}Responda as perguntas abaixo para avaliar seu progresso:{Colors.ENDC}\n")
        
        questions = [
            ("Você entende o conceito de superposição?", "Conceito Fundamental"),
            ("Você consegue implementar um Bell state?", "Level 1"),
            ("Você entende o algoritmo de Grover?", "Level 2"),
            ("Você consegue implementar VQE?", "Level 3"),
            ("Você entende mitigação de erros?", "Level 3")
        ]
        
        score = 0
        for question, level in questions:
            answer = input(f"{Colors.CYAN}{question} (S/N): {Colors.ENDC}").strip().upper()
            if answer == 'S':
                score += 1
                print(f"  {Colors.GREEN}✓ Bom! ({level}){Colors.ENDC}")
            else:
                print(f"  {Colors.YELLOW}→ Recomendação: Estude {level}{Colors.ENDC}")
        
        print(f"\n{Colors.BOLD}Resultado: {score}/5{Colors.ENDC}")
        
        if score <= 2:
            print(f"{Colors.YELLOW}Recomendação: Comece com Level 1{Colors.ENDC}")
        elif score <= 4:
            print(f"{Colors.YELLOW}Recomendação: Prossiga para Level 2{Colors.ENDC}")
        else:
            print(f"{Colors.GREEN}Recomendação: Você está pronto para Level 3!{Colors.ENDC}")
        
        input("\nPressione Enter para voltar...")
    
    # ==================== Development Menu ====================
    
    def development_menu(self):
        """Development and implementation menu."""
        while True:
            self.clear_screen()
            self.print_header("🛠️  Desenvolvimento")
            
            options = {
                '1': 'Comparar Frameworks',
                '2': 'Criar Circuito Quântico',
                '3': 'Aplicações Práticas',
                '4': 'Otimizar Circuito',
                '5': 'Classificadores Quânticos',
                '6': 'Explorar Padrões Avançados',
                '7': '🇨🇳 Origin Pilot - SO Quântico Chinês'
            }
            
            self.print_menu("Menu de Desenvolvimento", options)
            choice = self.get_choice(['1', '2', '3', '4', '5', '6', '7'])
            
            if choice == 'Q':
                self.exit_program()
            elif choice == '0':
                break
            elif choice == '1':
                self.framework_comparison_menu()
            elif choice == '2':
                self.run_script('create_basic_circuit.py')
            elif choice == '3':
                self.run_script('quantum_applications.py')
            elif choice == '4':
                self.run_script('quantum_classifier.py')
            elif choice == '5':
                self.run_script('quantum_embeddings.py')
            elif choice == '6':
                self.run_script('optimize_circuit.py')
            elif choice == '7':
                self.run_origin_pilot_integration()
    
    def framework_comparison_menu(self):
        """Framework comparison submenu."""
        self.clear_screen()
        self.print_header("Comparação de Frameworks")
        
        options = {
            '1': 'Bell State em Todos os Frameworks',
            '2': 'Comparação de Recursos',
            '3': 'Comparação de Sintaxe',
            '4': 'Métricas de Performance',
            '5': 'Comparação Completa'
        }
        
        self.print_menu("Framework Comparison", options)
        choice = self.get_choice(['1', '2', '3', '4', '5'])
        
        if choice == 'Q':
            self.exit_program()
        elif choice == '0':
            return
        
        script_path = os.path.join(self.scripts_dir, 'framework_comparison.py')
        args_map = {
            '1': 'bell',
            '2': 'features',
            '3': 'syntax',
            '4': 'performance',
            '5': 'all'
        }
        
        if choice in args_map:
            subprocess.run(['python', script_path, args_map[choice]])
            input("\nPressione Enter para voltar...")
    
    # ==================== Troubleshooting Menu ====================
    
    def troubleshooting_menu(self):
        """Troubleshooting and debugging menu."""
        while True:
            self.clear_screen()
            self.print_header("🔧 Troubleshooting & Debugging")
            
            options = {
                '1': 'Guia de Troubleshooting',
                '2': 'Problemas de Instalação',
                '3': 'Erros de Circuito',
                '4': 'Problemas de Simulação',
                '5': 'Otimização de Performance',
                '6': 'Referência de Erros'
            }
            
            self.print_menu("Menu de Troubleshooting", options)
            choice = self.get_choice(['1', '2', '3', '4', '5', '6'])
            
            if choice == 'Q':
                self.exit_program()
            elif choice == '0':
                break
            elif choice == '1':
                self.view_reference('troubleshooting_guide.md')
            elif choice == '2':
                self.show_installation_help()
            elif choice == '3':
                self.show_circuit_errors()
            elif choice == '4':
                self.show_simulation_help()
            elif choice == '5':
                self.show_performance_tips()
            elif choice == '6':
                self.show_error_reference()
    
    def show_installation_help(self):
        """Show installation help."""
        self.clear_screen()
        self.print_header("Problemas de Instalação")
        
        print(f"{Colors.BOLD}Problemas Comuns e Soluções:{Colors.ENDC}\n")
        
        problems = {
            'Qiskit não instala': [
                'pip install --upgrade pip setuptools wheel',
                'pip install qiskit'
            ],
            'ImportError: No module named qiskit': [
                'python -c "import qiskit; print(qiskit.__version__)"',
                'Verifique se está no ambiente correto'
            ],
            'Qiskit-Aer falha na compilação': [
                'pip install qiskit-aer --only-binary :all:',
                'Ou use: conda install -c conda-forge qiskit-aer'
            ]
        }
        
        for problem, solutions in problems.items():
            print(f"{Colors.RED}❌ {problem}{Colors.ENDC}")
            for solution in solutions:
                print(f"   {Colors.GREEN}→ {solution}{Colors.ENDC}")
            print()
        
        print(f"{Colors.YELLOW}Para mais detalhes, veja 'troubleshooting_guide.md'{Colors.ENDC}")
        input("\nPressione Enter para voltar...")
    
    def show_circuit_errors(self):
        """Show circuit error help."""
        self.clear_screen()
        self.print_header("Erros de Circuito")
        
        print(f"{Colors.BOLD}Erros Comuns em Circuitos:{Colors.ENDC}\n")
        
        errors = {
            'IndexError: qubit index out of bounds': 'Aumentar tamanho do circuito',
            'ValueError: Duplicate parameter names': 'Usar nomes únicos para parâmetros',
            'ValueError: Cannot bind parameters': 'Fornecer todos os valores de parâmetros',
            'ValueError: Invalid parameter value': 'Usar valores numéricos válidos'
        }
        
        for error, solution in errors.items():
            print(f"{Colors.RED}{error}{Colors.ENDC}")
            print(f"  {Colors.GREEN}Solução: {solution}{Colors.ENDC}\n")
        
        input("Pressione Enter para voltar...")
    
    def show_simulation_help(self):
        """Show simulation help."""
        self.clear_screen()
        self.print_header("Problemas de Simulação")
        
        print(f"{Colors.BOLD}Problemas Comuns em Simulação:{Colors.ENDC}\n")
        
        print(f"{Colors.YELLOW}Falta de Memória:{Colors.ENDC}")
        print("  • Use qasm_simulator para > 20 qubits")
        print("  • Reduza o número de shots")
        print("  • Otimize a profundidade do circuito\n")
        
        print(f"{Colors.YELLOW}Simulação Lenta:{Colors.ENDC}")
        print("  • Reduza o número de shots (ex: 100 em vez de 10000)")
        print("  • Use GPU acceleration se disponível")
        print("  • Paralelizar múltiplas simulações\n")
        
        print(f"{Colors.YELLOW}Resultados Inesperados:{Colors.ENDC}")
        print("  • Visualize o circuito: qc.draw()")
        print("  • Inspecione o statevector")
        print("  • Verifique a base de medição\n")
        
        input("Pressione Enter para voltar...")
    
    def show_performance_tips(self):
        """Show performance optimization tips."""
        self.clear_screen()
        self.print_header("Otimização de Performance")
        
        print(f"{Colors.BOLD}Dicas de Otimização:{Colors.ENDC}\n")
        
        print(f"{Colors.GREEN}✓ Reduzir Profundidade do Circuito{Colors.ENDC}")
        print("  • Usar transpilação")
        print("  • Remover gates redundantes")
        print("  • Usar commutation analysis\n")
        
        print(f"{Colors.GREEN}✓ Paralelizar Simulações{Colors.ENDC}")
        print("  • Executar múltiplos circuitos em batch")
        print("  • Usar ThreadPoolExecutor")
        print("  • Aproveitar GPU\n")
        
        print(f"{Colors.GREEN}✓ Usar Benchmarking{Colors.ENDC}")
        print("  • python scripts/benchmarking.py --all")
        print("  • Comparar frameworks")
        print("  • Exportar resultados para análise\n")
        
        input("Pressione Enter para voltar...")
    
    def show_error_reference(self):
        """Show error reference table."""
        self.clear_screen()
        self.print_header("Referência de Erros")
        
        print(f"{Colors.BOLD}Tabela de Erros Comuns:{Colors.ENDC}\n")
        
        print(f"{'Erro':<40} {'Causa':<30} {'Solução':<30}")
        print("-" * 100)
        
        errors = [
            ("IndexError: qubit out of bounds", "Qubit não existe", "Aumentar circuito"),
            ("ValueError: Duplicate parameter", "Nome duplicado", "Nomes únicos"),
            ("ImportError: No module", "Não instalado", "pip install"),
            ("MemoryError", "Muitos qubits", "Usar qasm_simulator"),
            ("QiskitError: No simulator", "Aer não instalado", "pip install qiskit-aer"),
        ]
        
        for error, cause, solution in errors:
            print(f"{error:<40} {cause:<30} {solution:<30}")
        
        print(f"\n{Colors.YELLOW}Para lista completa, veja 'troubleshooting_guide.md'{Colors.ENDC}")
        input("\nPressione Enter para voltar...")
    
    # ==================== Benchmarking Menu ====================
    
    def benchmarking_menu(self):
        """Benchmarking menu."""
        self.clear_screen()
        self.print_header("📊 Benchmarking")
        
        options = {
            '1': 'Comparar Todos os Frameworks',
            '2': 'Benchmark Qiskit',
            '3': 'Benchmark Cirq',
            '4': 'Benchmark PennyLane',
            '5': 'Exportar Resultados'
        }
        
        self.print_menu("Menu de Benchmarking", options)
        choice = self.get_choice(['1', '2', '3', '4', '5'])
        
        if choice == 'Q':
            self.exit_program()
        elif choice == '0':
            return
        
        script_path = os.path.join(self.scripts_dir, 'benchmarking.py')
        
        args_map = {
            '1': ['--all'],
            '2': ['--qiskit'],
            '3': ['--cirq'],
            '4': ['--pennylane'],
            '5': ['--all', '--export', 'benchmark_results.json']
        }
        
        if choice in args_map:
            subprocess.run(['python', script_path] + args_map[choice])
            input("\nPressione Enter para voltar...")
    
    # ==================== Resources Menu ====================
    
    def resources_menu(self):
        """Resources and learning materials menu."""
        while True:
            self.clear_screen()
            self.print_header("📖 Recursos Curados")
            
            options = {
                '1': 'Recursos por Nível',
                '2': 'MOOCs e Cursos',
                '3': 'Livros e Papers',
                '4': 'Ferramentas de Desenvolvimento',
                '5': 'Comunidade',
                '6': 'Guia de Seleção'
            }
            
            self.print_menu("Menu de Recursos", options)
            choice = self.get_choice(['1', '2', '3', '4', '5', '6'])
            
            if choice == 'Q':
                self.exit_program()
            elif choice == '0':
                break
            elif choice == '1':
                self.view_reference('curated_resources.md')
            elif choice == '2':
                self.show_moocs()
            elif choice == '3':
                self.show_books()
            elif choice == '4':
                self.show_tools()
            elif choice == '5':
                self.show_community()
            elif choice == '6':
                self.view_reference('curated_resources.md')
    
    def show_moocs(self):
        """Show MOOC recommendations."""
        self.clear_screen()
        self.print_header("MOOCs e Cursos Recomendados")
        
        print(f"{Colors.BOLD}Cursos Online:{Colors.ENDC}\n")
        
        moocs = {
            'Iniciante': [
                'Brilliant.org Quantum Computing',
                'CNOT.io - Introdução Interativa',
                'FutureLearn - Understanding Quantum Computers'
            ],
            'Intermediário': [
                'edX - Quantum Information Science I',
                'Coursera - Introduction to Quantum Computing',
                'Udemy - QC101 Quantum Computing'
            ],
            'Avançado': [
                'MIT OpenCourseWare - Quantum Information',
                'Stanford - Quantum Computer Programming',
                'Caltech - John Preskill Lecture Notes'
            ]
        }
        
        for level, courses in moocs.items():
            print(f"{Colors.CYAN}{level}:{Colors.ENDC}")
            for course in courses:
                print(f"  • {course}")
            print()
        
        input("Pressione Enter para voltar...")
    
    def show_books(self):
        """Show book recommendations."""
        self.clear_screen()
        self.print_header("Livros e Papers Recomendados")
        
        print(f"{Colors.BOLD}Livros:{Colors.ENDC}\n")
        
        books = {
            'Iniciante': [
                'Quantum Computing: A Gentle Introduction',
                'Quantum Computing Explained'
            ],
            'Intermediário': [
                'Learn Quantum Computation using Qiskit',
                'Learn Quantum Computing with Python and Q#'
            ],
            'Avançado': [
                'Quantum Computation and Quantum Information (Nielsen & Chuang)',
                'Problems and Solutions in Quantum Computing'
            ]
        }
        
        for level, book_list in books.items():
            print(f"{Colors.CYAN}{level}:{Colors.ENDC}")
            for book in book_list:
                print(f"  • {book}")
            print()
        
        input("Pressione Enter para voltar...")
    
    def show_tools(self):
        """Show development tools."""
        self.clear_screen()
        self.print_header("Ferramentas de Desenvolvimento")
        
        print(f"{Colors.BOLD}Frameworks Quânticos:{Colors.ENDC}\n")
        
        tools = {
            'Qiskit (IBM)': 'Production, IBM hardware, comprehensive',
            'Cirq (Google)': 'Simplicity, Google hardware, NISQ focus',
            'PennyLane (Xanadu)': 'ML focus, hardware-agnostic',
            'Q# (Microsoft)': 'Azure Quantum, strong typing',
            'TensorFlow Quantum': 'Hybrid ML, TensorFlow integration'
        }
        
        for tool, description in tools.items():
            print(f"{Colors.GREEN}{tool}{Colors.ENDC}")
            print(f"  → {description}\n")
        
        input("Pressione Enter para voltar...")
    
    def show_community(self):
        """Show community resources."""
        self.clear_screen()
        self.print_header("Comunidade Quântica")
        
        print(f"{Colors.BOLD}Organizações:{Colors.ENDC}\n")
        
        orgs = {
            'QWorld': 'Global network for quantum education',
            'QOSF': 'Quantum Open Source Foundation',
            'IBM Quantum': 'IBM quantum computing community',
            'Qiskit': 'Official Qiskit community'
        }
        
        for org, desc in orgs.items():
            print(f"{Colors.CYAN}{org}{Colors.ENDC}")
            print(f"  → {desc}\n")
        
        print(f"{Colors.BOLD}Eventos:{Colors.ENDC}\n")
        print("  • IBM Quantum Challenges (quarterly)")
        print("  • Qiskit Global Summer School (annual)")
        print("  • Quantum Computing Conferences")
        print("  • Webinars and Workshops\n")
        
        input("Pressione Enter para voltar...")
    
    # ==================== Settings Menu ====================
    
    def settings_menu(self):
        """Settings and preferences menu."""
        self.clear_screen()
        self.print_header("⚙️  Configurações")
        
        print(f"{Colors.BOLD}Configurações Disponíveis:{Colors.ENDC}\n")
        print(f"1. Alterar Nível de Usuário")
        print(f"2. Visualizar Informações do Skill")
        print(f"3. Verificar Dependências")
        print(f"0. Voltar\n")
        
        choice = input(f"{Colors.BOLD}Escolha uma opção: {Colors.ENDC}").strip()
        
        if choice == '1':
            self.select_user_level()
        elif choice == '2':
            self.show_skill_info()
        elif choice == '3':
            self.check_dependencies()
    
    def show_skill_info(self):
        """Show skill information."""
        self.clear_screen()
        self.print_header("Informações do Skill")
        
        print(f"{Colors.BOLD}Quantum Computing Skill{Colors.ENDC}\n")
        print(f"Versão: 2.0 (com Menu Interativo)")
        print(f"Frameworks: Qiskit, Cirq, PennyLane, Q#, TensorFlow Quantum")
        print(f"Scripts: 9 (incluindo menu)")
        print(f"Referências: 10")
        print(f"Exercícios: 40+")
        print(f"Recursos: 100+\n")
        
        print(f"{Colors.BOLD}Conteúdo:{Colors.ENDC}")
        print(f"  • Learning paths (3 níveis)")
        print(f"  • Implementation patterns (7)")
        print(f"  • Applications (4 domínios)")
        print(f"  • Troubleshooting guide")
        print(f"  • Benchmarking suite")
        print(f"  • Curated resources\n")
        
        input("Pressione Enter para voltar...")
    
    def check_dependencies(self):
        """Check installed dependencies."""
        self.clear_screen()
        self.print_header("Verificação de Dependências")
        
        print(f"{Colors.BOLD}Verificando frameworks instalados...{Colors.ENDC}\n")
        
        frameworks = {
            'qiskit': 'Qiskit (IBM)',
            'cirq': 'Cirq (Google)',
            'pennylane': 'PennyLane (Xanadu)',
            'tensorflow_quantum': 'TensorFlow Quantum'
        }
        
        for module, name in frameworks.items():
            try:
                __import__(module)
                print(f"{Colors.GREEN}✓ {name}{Colors.ENDC} - Instalado")
            except ImportError:
                print(f"{Colors.RED}✗ {name}{Colors.ENDC} - Não instalado")
        
        print(f"\n{Colors.YELLOW}Dica: Use 'pip install <framework>' para instalar.{Colors.ENDC}")
        input("\nPressione Enter para voltar...")
    
    # ==================== Utility Methods ====================
    
    def run_script(self, script_name: str):
        """Run a Python script from scripts directory."""
        script_path = os.path.join(self.scripts_dir, script_name)
        if os.path.exists(script_path):
            subprocess.run(['python', script_path])
        else:
            print(f"{Colors.RED}Erro: Script não encontrado: {script_name}{Colors.ENDC}")
        
        input("\nPressione Enter para voltar...")
    
    def view_reference(self, ref_name: str):
        """View a reference file."""
        ref_path = os.path.join(self.references_dir, ref_name)
        if os.path.exists(ref_path):
            # Try to use less for better viewing
            os.system(f'less "{ref_path}"')
        else:
            print(f"{Colors.RED}Erro: Referência não encontrada: {ref_name}{Colors.ENDC}")
            input("\nPressione Enter para voltar...")
    
    def exit_program(self):
        """Exit the program gracefully."""
        self.clear_screen()
        print(f"\n{Colors.BOLD}{Colors.GREEN}Obrigado por usar o Skill de Computação Quântica!{Colors.ENDC}")
        print(f"{Colors.CYAN}Continue aprendendo e desenvolvendo com quantum computing.{Colors.ENDC}\n")
        sys.exit(0)
    
    def run(self):
        """Main entry point."""
        self.clear_screen()
        self.select_user_level()
        self.main_menu()


def main():
    """Main entry point."""
    try:
        menu = QuantumComputingMenu()
        menu.run()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Programa interrompido pelo usuário.{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.RED}Erro: {e}{Colors.ENDC}")
        sys.exit(1)


if __name__ == "__main__":
    main()
