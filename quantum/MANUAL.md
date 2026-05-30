# Manual Completo - Skill de Computação Quântica

**Versão**: 2.0 com Menu Interativo  
**Última Atualização**: Abril 2026  
**Frameworks**: Qiskit, Cirq, PennyLane, Q#, TensorFlow Quantum

---

## Índice

1. [Introdução](#introdução)
2. [Quick Start](#quick-start)
3. [Instalação](#instalação)
4. [Menu Interativo](#menu-interativo)
5. [Guias por Nível](#guias-por-nível)
6. [Referência Completa](#referência-completa)
7. [Troubleshooting](#troubleshooting)
8. [Recursos](#recursos)
9. [FAQ](#faq)
10. [Suporte](#suporte)

---

## Introdução

O **Skill de Computação Quântica** é uma plataforma completa para aprender e desenvolver aplicações de computação quântica. Ele oferece:

- **5 Frameworks**: Qiskit, Cirq, PennyLane, Q#, TensorFlow Quantum
- **4 Domínios de Aplicação**: Química, Finanças, Otimização, Machine Learning
- **40+ Exercícios**: Exercícios kata-style com soluções
- **10 Referências**: Documentação técnica completa
- **9 Scripts**: Ferramentas executáveis para desenvolvimento
- **Menu Interativo**: Interface amigável para todos os níveis

### Quem Deve Usar Este Skill?

- **Iniciantes**: Novo em computação quântica
- **Intermediários**: Conhecimento básico de conceitos quânticos
- **Avançados**: Experiência com frameworks quânticos
- **Pesquisadores**: Desenvolvimento de pesquisa em quantum computing

---

## Quick Start

### 1. Instalação Rápida (5 minutos)

```bash
# Instalar Qiskit (padrão)
pip install qiskit qiskit-aer qiskit-ibm-runtime

# Ou instalar todos os frameworks
pip install qiskit cirq pennylane tensorflow-quantum
```

### 2. Iniciar Menu Interativo (1 minuto)

```bash
python scripts/main_menu.py
```

### 3. Selecione seu Nível

- **Iniciante**: Novo em quantum computing
- **Intermediário**: Conhecimento básico
- **Avançado**: Experiência com frameworks
- **Pesquisador**: Desenvolvimento de pesquisa

### 4. Siga o Caminho Recomendado

O menu oferecerá um caminho personalizado baseado no seu nível.

---

## Instalação

### Instalação Completa

#### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- 2GB de espaço em disco

#### Passo 1: Instalar Qiskit (IBM)

```bash
pip install qiskit qiskit-aer qiskit-ibm-runtime
```

**Verificar instalação**:
```bash
python -c "import qiskit; print(qiskit.__version__)"
```

#### Passo 2: Instalar Cirq (Google)

```bash
pip install cirq
```

#### Passo 3: Instalar PennyLane (Xanadu)

```bash
pip install pennylane
```

#### Passo 4: Instalar Q# (Microsoft)

```bash
dotnet add package Microsoft.Quantum.SDK
```

#### Passo 5: Instalar TensorFlow Quantum

```bash
pip install tensorflow-quantum
```

### Verificar Todas as Instalações

```bash
python scripts/main_menu.py
# Selecione: Configurações → Verificar Dependências
```

### Troubleshooting de Instalação

**Problema**: "pip: command not found"
```bash
# Use python -m pip
python -m pip install qiskit
```

**Problema**: "Permission denied"
```bash
# Use --user flag
pip install --user qiskit
```

**Problema**: Qiskit-Aer falha na compilação
```bash
# Use versão pré-compilada
pip install qiskit-aer --only-binary :all:
```

---

## Menu Interativo

### Como Iniciar

```bash
python scripts/main_menu.py
```

### Estrutura Principal

```
┌─ Menu Principal ─────────────────────┐
│ 1. 📚 Aprendizado                    │
│ 2. 🛠️  Desenvolvimento               │
│ 3. 🔧 Troubleshooting & Debugging    │
│ 4. 📊 Benchmarking                   │
│ 5. 📖 Recursos Curados               │
│ 6. ⚙️  Configurações                 │
└──────────────────────────────────────┘
```

### Navegação

- **Números (1-6)**: Selecionar opção
- **0**: Voltar ao menu anterior
- **Q**: Sair do programa
- **Enter**: Confirmar seleção

### 6 Categorias Principais

#### 1. 📚 Aprendizado

```
├─ Guia de Aprendizado Interativo
├─ Visualizar Caminho de Aprendizado
├─ Exercícios Kata-Style
├─ Auto-Avaliação
└─ Conceitos Fundamentais
```

**Melhor para**: Aprender conceitos de quantum computing

#### 2. 🛠️ Desenvolvimento

```
├─ Comparar Frameworks
├─ Criar Circuito Básico
├─ Explorar Aplicações
├─ Classificadores Quânticos
├─ Feature Maps Quânticos
└─ Otimizar Circuito
```

**Melhor para**: Implementar algoritmos e aplicações

#### 3. 🔧 Troubleshooting & Debugging

```
├─ Guia de Troubleshooting
├─ Problemas de Instalação
├─ Erros de Circuito
├─ Problemas de Simulação
├─ Otimização de Performance
└─ Referência de Erros
```

**Melhor para**: Resolver problemas e otimizar código

#### 4. 📊 Benchmarking

```
├─ Comparar Todos os Frameworks
├─ Benchmark Qiskit
├─ Benchmark Cirq
├─ Benchmark PennyLane
└─ Exportar Resultados
```

**Melhor para**: Comparar performance de frameworks

#### 5. 📖 Recursos Curados

```
├─ Recursos por Nível
├─ MOOCs e Cursos
├─ Livros e Papers
├─ Ferramentas de Desenvolvimento
├─ Comunidade
└─ Guia de Seleção
```

**Melhor para**: Encontrar recursos de aprendizado

#### 6. ⚙️ Configurações

```
├─ Alterar Nível de Usuário
├─ Visualizar Informações do Skill
└─ Verificar Dependências
```

**Melhor para**: Gerenciar preferências

---

## Guias por Nível

### Iniciante (Semanas 1-3)

#### Semana 1: Conceitos Básicos

**Objetivo**: Entender qubits, gates e medições

**Caminho Recomendado**:
1. Menu → Aprendizado → Guia Interativo
2. Leia `learning_path.md` - Level 1
3. Complete 5 primeiros exercícios kata-style
4. Execute `python scripts/create_basic_circuit.py bell 2`

**Conceitos**:
- Qubits vs bits
- Superposição
- Emaranhamento
- Gates quânticos (H, X, Y, Z, CNOT)
- Medição

**Exercícios**:
- Criar Bell state
- Criar superposição
- Entender medição

#### Semana 2: Algoritmos Básicos

**Objetivo**: Implementar Deutsch-Jozsa e Grover

**Caminho Recomendado**:
1. Menu → Aprendizado → Exercícios Kata-Style
2. Complete exercícios Level 2
3. Execute `python scripts/quantum_applications.py all`

**Conceitos**:
- Deutsch-Jozsa algorithm
- Grover's search
- Oracle design

#### Semana 3: Aplicações Práticas

**Objetivo**: Implementar primeira aplicação

**Caminho Recomendado**:
1. Menu → Desenvolvimento → Criar Circuito Básico
2. Menu → Desenvolvimento → Explorar Aplicações
3. Escolha uma aplicação (química, finanças, otimização)

**Próximos Passos**:
- Avançar para Intermediário
- Explorar frameworks diferentes
- Implementar aplicações mais complexas

---

### Intermediário (Semanas 4-8)

#### Fase 1: Exploração de Frameworks (Semanas 4-5)

**Objetivo**: Entender diferenças entre frameworks

**Caminho Recomendado**:
1. Menu → Desenvolvimento → Comparar Frameworks
2. Execute `python scripts/framework_comparison.py all`
3. Leia `quantum_frameworks.md`
4. Menu → Benchmarking → Comparar Todos os Frameworks

**Comparação**:
- Sintaxe de cada framework
- Performance
- Recursos disponíveis
- Comunidade

#### Fase 2: Implementação Prática (Semanas 6-7)

**Objetivo**: Implementar aplicações em múltiplos frameworks

**Caminho Recomendado**:
1. Escolha um framework (recomendado: Qiskit)
2. Menu → Desenvolvimento → Explorar Aplicações
3. Implemente aplicação em seu framework
4. Menu → Benchmarking → Exportar Resultados

**Aplicações**:
- Simulação molecular (química)
- Pricing de opções (finanças)
- MaxCut problem (otimização)
- Classificação (ML)

#### Fase 3: Otimização (Semana 8)

**Objetivo**: Otimizar circuitos para hardware

**Caminho Recomendado**:
1. Menu → Desenvolvimento → Otimizar Circuito
2. Menu → Troubleshooting → Otimização de Performance
3. Leia `advanced_patterns.md`

**Técnicas**:
- Reduzir profundidade
- Remover gates redundantes
- Mitigação de erros

**Próximos Passos**:
- Avançar para Avançado
- Explorar ML quântico
- Contribuir para comunidade

---

### Avançado (Semanas 9-13)

#### Fase 1: Machine Learning Quântico (Semanas 9-10)

**Objetivo**: Implementar classificadores quânticos

**Caminho Recomendado**:
1. Menu → Desenvolvimento → Classificadores Quânticos
2. Leia `quantum_machine_learning.md`
3. Execute `python scripts/quantum_classifier.py qnn`
4. Implemente seu próprio classificador

**Técnicas**:
- QSVM (Quantum Support Vector Machine)
- QNN (Quantum Neural Networks)
- Feature maps
- Kernel methods

#### Fase 2: Simulação Quântica (Semanas 11-12)

**Objetivo**: Simular sistemas quânticos complexos

**Caminho Recomendado**:
1. Leia `quantum_applications.md` - Chemistry
2. Implemente simulação molecular
3. Use `quantum_applications.py chemistry`
4. Otimize com `optimize_circuit.py`

**Aplicações**:
- Simulação de moléculas
- Cálculo de energias
- Descoberta de drogas

#### Fase 3: Pesquisa e Desenvolvimento (Semana 13)

**Objetivo**: Conduzir pesquisa original

**Caminho Recomendado**:
1. Menu → Recursos → Comunidade
2. Explore papers e publicações
3. Desenvolva seu próprio algoritmo
4. Publique resultados

**Recursos**:
- arXiv papers
- Conferências
- Comunidade QWorld/QOSF
- GitHub

---

### Pesquisador (Contínuo)

#### Pesquisa Avançada

**Objetivo**: Contribuir para pesquisa em quantum computing

**Recursos**:
1. Leia `curated_resources.md` - Advanced
2. Acompanhe papers recentes
3. Participe de eventos
4. Colabore com comunidade

**Áreas de Pesquisa**:
- Quantum machine learning
- Error mitigation
- Quantum simulation
- Quantum algorithms
- Hybrid quantum-classical

---

## Referência Completa

### Scripts Disponíveis

#### 1. `main_menu.py`
Menu interativo principal. Inicie com:
```bash
python scripts/main_menu.py
```

#### 2. `learning_roadmap.py`
Guia interativo de aprendizado. Execute com:
```bash
python scripts/learning_roadmap.py
```

#### 3. `framework_comparison.py`
Compare frameworks quânticos:
```bash
python scripts/framework_comparison.py all
python scripts/framework_comparison.py syntax
python scripts/framework_comparison.py performance
```

#### 4. `quantum_applications.py`
Explore aplicações quânticas:
```bash
python scripts/quantum_applications.py chemistry
python scripts/quantum_applications.py finance
python scripts/quantum_applications.py optimization
python scripts/quantum_applications.py ml
python scripts/quantum_applications.py all
```

#### 5. `create_basic_circuit.py`
Crie circuitos básicos:
```bash
python scripts/create_basic_circuit.py bell 2
python scripts/create_basic_circuit.py superposition 3
python scripts/create_basic_circuit.py grover 3 5
```

#### 6. `optimize_circuit.py`
Otimize circuitos:
```bash
python scripts/optimize_circuit.py circuit.qasm 2
```

#### 7. `quantum_classifier.py`
Implemente classificadores quânticos:
```bash
python scripts/quantum_classifier.py qsvm
python scripts/quantum_classifier.py qnn
python scripts/quantum_classifier.py kernel_demo
```

#### 8. `quantum_embeddings.py`
Explore feature maps quânticos:
```bash
python scripts/quantum_embeddings.py compare
python scripts/quantum_embeddings.py analyze Angle
python scripts/quantum_embeddings.py kernel_matrix
```

#### 9. `benchmarking.py`
Execute benchmarks:
```bash
python scripts/benchmarking.py --all
python scripts/benchmarking.py --qiskit
python scripts/benchmarking.py --export results.json
```

### Referências Disponíveis

| Referência | Tamanho | Conteúdo |
|-----------|---------|----------|
| `learning_path.md` | 3.5 KB | 40+ exercícios, 3 níveis |
| `advanced_patterns.md` | 2.5 KB | 7 padrões de implementação |
| `quantum_frameworks.md` | 3 KB | Comparação de 5 frameworks |
| `quantum_applications.md` | 2.5 KB | 4 domínios de aplicação |
| `quantum_algorithms.md` | 2 KB | 9 algoritmos quânticos |
| `quantum_machine_learning.md` | 2 KB | QML completo |
| `best_practices.md` | 1.5 KB | Boas práticas |
| `curated_resources.md` | 3 KB | 100+ recursos |
| `troubleshooting_guide.md` | 2 KB | Soluções de problemas |
| `menu_guide.md` | 6 KB | Guia do menu |
| `flowcharts.md` | 4 KB | 10 fluxogramas |

---

## Troubleshooting

### Problemas Comuns

#### Instalação

**Erro**: "pip: command not found"
```bash
# Solução
python -m pip install qiskit
```

**Erro**: "Permission denied"
```bash
# Solução
pip install --user qiskit
```

**Erro**: "Qiskit-Aer compilation failed"
```bash
# Solução
pip install qiskit-aer --only-binary :all:
```

#### Código

**Erro**: "IndexError: qubit index out of bounds"
```python
# Problema: Qubit não existe
qc = QuantumCircuit(2)
qc.h(5)  # ❌ Erro - só temos qubits 0 e 1

# Solução: Aumentar número de qubits
qc = QuantumCircuit(6)
qc.h(5)  # ✓ Correto
```

**Erro**: "ValueError: Duplicate parameter names"
```python
# Problema: Nomes duplicados
params = ParameterVector('θ', 2)
theta = Parameter('θ')  # ❌ Erro - 'θ' já existe

# Solução: Usar nomes únicos
params = ParameterVector('θ', 2)
phi = Parameter('φ')  # ✓ Correto
```

#### Simulação

**Problema**: "Falta de memória"
```python
# Problema: Muitos qubits
simulator = AerSimulator()
qc = QuantumCircuit(30)  # ❌ Muita memória

# Solução: Usar qasm_simulator
simulator = AerSimulator(method='qasm_simulator')
qc = QuantumCircuit(20)  # ✓ Melhor
```

**Problema**: "Simulação muito lenta"
```python
# Problema: Muitos shots
job = simulator.run(qc, shots=100000)  # ❌ Lento

# Solução: Reduzir shots
job = simulator.run(qc, shots=1000)  # ✓ Rápido
```

### Obter Ajuda

1. **Menu**: Menu → Troubleshooting
2. **Referência**: Leia `troubleshooting_guide.md`
3. **Comunidade**: 
   - QWorld: https://qworld.net
   - QOSF: https://qosf.org
   - GitHub Issues: https://github.com/Qiskit/qiskit

---

## Recursos

### Aprendizado

- **Brilliant.org**: Interactive quantum computing
- **Qiskit Textbook**: https://qiskit.org/textbook
- **edX**: Quantum Information Science I
- **Coursera**: Introduction to Quantum Computing

### Livros

- Nielsen & Chuang: "Quantum Computation and Quantum Information"
- Yanofsky & Mannucci: "Quantum Computing for Computer Scientists"
- Preskill: "Lecture Notes on Quantum Computation"

### Comunidade

- **QWorld**: Global network for quantum education
- **QOSF**: Quantum Open Source Foundation
- **IBM Quantum**: https://quantum.ibm.com
- **Qiskit**: https://qiskit.org

### Hardware

- IBM Quantum: Free access to real quantum computers
- Google Cirq: Quantum hardware access
- AWS Braket: Quantum computing service
- Azure Quantum: Microsoft quantum platform

---

## FAQ

### P: Por onde devo começar?
**R**: Execute `python scripts/main_menu.py` e selecione seu nível. O menu oferecerá um caminho personalizado.

### P: Qual framework devo usar?
**R**: Depende do seu objetivo:
- **Produção**: Qiskit
- **Aprendizado**: Cirq
- **ML**: PennyLane
- **Azure**: Q#

### P: Quanto tempo leva para aprender?
**R**: 
- Iniciante: 3-4 semanas
- Intermediário: 4-5 semanas
- Avançado: 5-6 semanas
- Total: 9-13 semanas

### P: Preciso de conhecimento de física?
**R**: Não, mas ajuda. O skill ensina conceitos de quantum computing do zero.

### P: Posso usar em produção?
**R**: Sim! Leia `advanced_patterns.md` para padrões de produção.

### P: Como contribuir?
**R**: Veja `curated_resources.md` - Comunidade para informações sobre contribuição.

---

## Suporte

### Canais de Suporte

1. **Menu Interativo**: Menu → Troubleshooting
2. **Documentação**: Leia as referências
3. **Comunidade**: QWorld, QOSF, GitHub
4. **Issues**: GitHub Issues do Qiskit

### Reportar Bugs

Se encontrar um bug:
1. Descreva o problema
2. Forneça código reproduzível
3. Inclua versão do Python e frameworks
4. Reporte no GitHub

### Feedback

Sua opinião é importante! Compartilhe feedback sobre:
- Qualidade do conteúdo
- Clareza das explicações
- Exemplos úteis
- Recursos faltantes

---

## Conclusão

Parabéns por escolher aprender computação quântica! Este skill oferece:

✅ **Educação Completa**: Do iniciante ao pesquisador
✅ **Prático**: 40+ exercícios + 9 scripts
✅ **Multi-Framework**: 5 frameworks principais
✅ **Bem Documentado**: 11 referências técnicas
✅ **Interativo**: Menu amigável para todos os níveis
✅ **Profissional**: Padrões de produção inclusos

**Comece agora**: `python scripts/main_menu.py`

Boa sorte em sua jornada de computação quântica! 🚀

---

## Apêndice

### Glossário

- **Qubit**: Unidade básica de informação quântica
- **Gate**: Operação que modifica qubits
- **Circuito**: Sequência de gates
- **Medição**: Extração de informação clássica
- **Superposição**: Estado quântico em múltiplos estados
- **Emaranhamento**: Correlação quântica entre qubits
- **Simulação**: Execução em computador clássico
- **Hardware**: Computador quântico real

### Símbolos Comuns

| Símbolo | Significado |
|---------|------------|
| H | Hadamard gate |
| X | Pauli-X gate (NOT) |
| Y | Pauli-Y gate |
| Z | Pauli-Z gate |
| CNOT | Controlled-NOT gate |
| CZ | Controlled-Z gate |
| RX(θ) | Rotation X gate |
| RY(θ) | Rotation Y gate |
| RZ(θ) | Rotation Z gate |

### Recursos Adicionais

- Mermaid Diagrams: https://mermaid.js.org
- Qiskit Docs: https://qiskit.org/documentation
- Cirq Docs: https://quantumai.google/cirq
- PennyLane Docs: https://pennylane.ai

---

**Versão**: 2.0  
**Data**: Abril 2026  
**Mantido por**: Skill de Computação Quântica  
**Licença**: MIT
