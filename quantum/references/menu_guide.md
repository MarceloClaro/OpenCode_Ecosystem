# Menu Interativo - Guia Completo

Guia de uso do menu interativo do Skill de Computação Quântica.

## Começando

### Iniciar o Menu

```bash
python scripts/main_menu.py
```

### Seleção de Nível

Ao iniciar, você será solicitado a selecionar seu nível de experiência:

- **Iniciante**: Novo em computação quântica
- **Intermediário**: Conhecimento básico de conceitos quânticos
- **Avançado**: Experiência com frameworks quânticos
- **Pesquisador**: Desenvolvimento de pesquisa em quantum computing

Sua seleção personaliza as recomendações e guias no menu.

---

## Estrutura do Menu

### Menu Principal

O menu principal oferece 6 categorias principais:

```
1. 📚 Aprendizado
2. 🛠️  Desenvolvimento
3. 🔧 Troubleshooting & Debugging
4. 📊 Benchmarking
5. 📖 Recursos Curados
6. ⚙️  Configurações
```

---

## 📚 Menu de Aprendizado

Acesso a recursos educacionais e exercícios.

### Opções

| Opção | Descrição | Melhor Para |
|-------|-----------|------------|
| 1 | Guia de Aprendizado Interativo | Iniciantes - Roadmap personalizado |
| 2 | Visualizar Caminho de Aprendizado | Todos - Ver estrutura de aprendizado |
| 3 | Exercícios Kata-Style | Todos - Praticar com exercícios |
| 4 | Auto-Avaliação | Todos - Avaliar progresso |
| 5 | Conceitos Fundamentais | Iniciantes - Aprender teoria |

### Fluxo Recomendado para Iniciantes

1. Selecione **"Guia de Aprendizado Interativo"** (opção 1)
2. Siga o roadmap personalizado
3. Leia **"Caminho de Aprendizado"** (opção 2) para seu nível
4. Pratique com **"Exercícios Kata-Style"** (opção 3)
5. Use **"Auto-Avaliação"** (opção 4) para verificar progresso

### Fluxo Recomendado para Intermediários

1. Visualize **"Caminho de Aprendizado"** (opção 2) Level 2
2. Pratique **"Exercícios Kata-Style"** (opção 3) Level 2
3. Estude **"Conceitos Fundamentais"** (opção 5)
4. Passe para Menu de Desenvolvimento

### Fluxo Recomendado para Avançados

1. Vá direto para **Menu de Desenvolvimento**
2. Use **"Conceitos Fundamentais"** como referência conforme necessário
3. Explore **"Recursos Curados"** para pesquisa

---

## 🛠️  Menu de Desenvolvimento

Ferramentas para implementar algoritmos e aplicações quânticas.

### Opções

| Opção | Descrição | Saída |
|-------|-----------|-------|
| 1 | Comparar Frameworks | Análise comparativa |
| 2 | Criar Circuito Básico | Circuitos de exemplo |
| 3 | Explorar Aplicações | Demos de aplicações |
| 4 | Classificadores Quânticos | QSVM, QNN |
| 5 | Feature Maps Quânticos | Encodings diferentes |
| 6 | Otimizar Circuito | Circuito otimizado |

### Submenu: Comparação de Frameworks

Quando você seleciona a opção 1, um submenu oferece:

```
1. Bell State em Todos os Frameworks
2. Comparação de Recursos
3. Comparação de Sintaxe
4. Métricas de Performance
5. Comparação Completa
```

**Recomendação**: Comece com opção 1 (Bell State) para ver as diferenças de sintaxe.

### Fluxo Recomendado

**Para Iniciantes**:
1. Selecione **"Criar Circuito Básico"** (opção 2)
2. Explore **"Comparar Frameworks"** (opção 1) - Sintaxe
3. Estude **"Explorar Aplicações"** (opção 3)

**Para Intermediários**:
1. Selecione **"Comparar Frameworks"** (opção 1) - Completo
2. Escolha um framework
3. Implemente **"Classificadores Quânticos"** (opção 4)

**Para Avançados**:
1. Use **"Otimizar Circuito"** (opção 6)
2. Implemente **"Feature Maps Quânticos"** (opção 5)
3. Crie aplicações customizadas

---

## 🔧 Menu de Troubleshooting & Debugging

Ajuda para resolver problemas e otimizar código.

### Opções

| Opção | Descrição | Quando Usar |
|-------|-----------|------------|
| 1 | Guia de Troubleshooting | Problema geral |
| 2 | Problemas de Instalação | Erros ao instalar |
| 3 | Erros de Circuito | Erro em código |
| 4 | Problemas de Simulação | Simulação falha |
| 5 | Otimização de Performance | Código lento |
| 6 | Referência de Erros | Procurar erro específico |

### Fluxo de Troubleshooting

1. **Identifique o tipo de problema**:
   - Instalação → Opção 2
   - Código → Opção 3
   - Simulação → Opção 4
   - Performance → Opção 5

2. **Procure a solução**:
   - Veja a descrição do problema
   - Siga as soluções sugeridas
   - Teste a solução

3. **Se não resolver**:
   - Consulte **"Guia de Troubleshooting"** (opção 1)
   - Veja **"Referência de Erros"** (opção 6)
   - Procure em recursos online

### Exemplos de Problemas

**Problema**: "ImportError: No module named 'qiskit'"
- **Solução**: Menu → Troubleshooting → Problemas de Instalação

**Problema**: "IndexError: qubit index out of bounds"
- **Solução**: Menu → Troubleshooting → Erros de Circuito

**Problema**: "Simulação muito lenta"
- **Solução**: Menu → Troubleshooting → Otimização de Performance

---

## 📊 Menu de Benchmarking

Compare frameworks e otimize circuitos.

### Opções

| Opção | Descrição | Tempo |
|-------|-----------|-------|
| 1 | Comparar Todos os Frameworks | ~2-5 min |
| 2 | Benchmark Qiskit | ~1-2 min |
| 3 | Benchmark Cirq | ~1-2 min |
| 4 | Benchmark PennyLane | ~1-2 min |
| 5 | Exportar Resultados | ~2-5 min |

### O que é Benchmarked

- **Bell State**: Criação e simulação
- **Grover's Algorithm**: Busca quântica (3 qubits)
- **VQE Ansatz**: Variational quantum eigensolver

### Interpretando Resultados

```
[Qiskit] Benchmarking Bell state...
  Execution time: 0.0234s
  Results: {'00': 512, '11': 512}
```

- **Execution time**: Tempo total de execução
- **Results**: Distribuição de medições
- **Framework**: Qual framework foi testado

### Exportar Resultados

Selecione opção 5 para exportar para `benchmark_results.json`:

```json
{
  "framework": "Qiskit",
  "circuit": "Bell state",
  "shots": 1024,
  "execution_time": 0.0234,
  "qubits": 2,
  "gates": 3
}
```

---

## 📖 Menu de Recursos Curados

Acesso a 100+ recursos de aprendizado e desenvolvimento.

### Opções

| Opção | Descrição | Conteúdo |
|-------|-----------|----------|
| 1 | Recursos por Nível | Beginner, Intermediate, Advanced |
| 2 | MOOCs e Cursos | Brilliant.org, edX, Coursera |
| 3 | Livros e Papers | Nielsen & Chuang, Preskill |
| 4 | Ferramentas de Desenvolvimento | Frameworks, simuladores |
| 5 | Comunidade | QWorld, QOSF, eventos |
| 6 | Guia de Seleção | Recomendações personalizadas |

### Recursos por Nível

**Iniciante**:
- Interactive Introduction to Quantum Computing
- Brilliant.org Quantum Computing
- Quantum Computing: A Gentle Introduction

**Intermediário**:
- Qiskit Textbook
- Learn Quantum Computing with Python and Q#
- edX Quantum Information Science I

**Avançado**:
- Nielsen & Chuang (Quantum Computation and Quantum Information)
- John Preskill's Lecture Notes
- arXiv papers

### Comunidade

Conecte-se com a comunidade quântica:

- **QWorld**: Rede global para educação quântica
- **QOSF**: Quantum Open Source Foundation
- **IBM Quantum**: Comunidade IBM
- **Qiskit**: Comunidade oficial Qiskit

### Eventos

- IBM Quantum Challenges (trimestral)
- Qiskit Global Summer School (anual)
- Conferências de Quantum Computing
- Webinars e workshops

---

## ⚙️  Menu de Configurações

Gerenciar preferências e verificar sistema.

### Opções

| Opção | Descrição |
|-------|-----------|
| 1 | Alterar Nível de Usuário |
| 2 | Visualizar Informações do Skill |
| 3 | Verificar Dependências |

### Verificar Dependências

Verifica quais frameworks estão instalados:

```
✓ Qiskit (IBM) - Instalado
✗ Cirq (Google) - Não instalado
✓ PennyLane (Xanadu) - Instalado
✗ TensorFlow Quantum - Não instalado
```

**Para instalar um framework**:
```bash
pip install qiskit
pip install cirq
pip install pennylane
pip install tensorflow-quantum
```

---

## Atalhos e Dicas

### Navegação

- **0**: Voltar ao menu anterior
- **Q**: Sair do programa
- **Enter**: Confirmar seleção

### Dicas de Uso

1. **Para Iniciantes**: Comece com Menu de Aprendizado
2. **Para Intermediários**: Alterne entre Aprendizado e Desenvolvimento
3. **Para Avançados**: Use Desenvolvimento e Benchmarking
4. **Para Troubleshooting**: Use Menu de Troubleshooting quando necessário

### Fluxo Recomendado Completo

```
1. Selecione seu nível
2. Menu → Aprendizado → Guia Interativo
3. Menu → Aprendizado → Exercícios
4. Menu → Desenvolvimento → Comparar Frameworks
5. Menu → Desenvolvimento → Criar Circuito
6. Menu → Benchmarking → Comparar Frameworks
7. Menu → Recursos → Comunidade
8. Menu → Troubleshooting (conforme necessário)
```

---

## Exemplos de Uso

### Exemplo 1: Iniciante Aprendendo Quantum Computing

```
1. python scripts/main_menu.py
2. Selecione: Iniciante
3. Menu → Aprendizado → Guia Interativo
4. Siga o roadmap
5. Menu → Aprendizado → Exercícios Kata-Style
6. Complete Level 1
7. Menu → Desenvolvimento → Criar Circuito Básico
```

### Exemplo 2: Intermediário Explorando Frameworks

```
1. python scripts/main_menu.py
2. Selecione: Intermediário
3. Menu → Desenvolvimento → Comparar Frameworks → Sintaxe
4. Menu → Benchmarking → Comparar Todos
5. Menu → Desenvolvimento → Criar Circuito Básico
6. Menu → Desenvolvimento → Classificadores Quânticos
```

### Exemplo 3: Avançado Otimizando Código

```
1. python scripts/main_menu.py
2. Selecione: Avançado
3. Menu → Desenvolvimento → Otimizar Circuito
4. Menu → Benchmarking → Exportar Resultados
5. Menu → Troubleshooting → Otimização de Performance
6. Menu → Recursos → Comunidade
```

### Exemplo 4: Troubleshooting de Erro

```
1. Você recebe: "IndexError: qubit index out of bounds"
2. Menu → Troubleshooting → Erros de Circuito
3. Veja a solução: "Aumentar tamanho do circuito"
4. Corrija seu código
5. Teste novamente
```

---

## Recursos Adicionais

### Dentro do Menu

- Todas as referências estão acessíveis via Menu → Recursos
- Scripts executáveis podem ser rodados diretamente do menu
- Benchmarking integrado para comparação de frameworks

### Fora do Menu

```bash
# Executar scripts diretamente
python scripts/learning_roadmap.py
python scripts/framework_comparison.py all
python scripts/benchmarking.py --all

# Visualizar referências
less references/learning_path.md
less references/troubleshooting_guide.md
less references/curated_resources.md
```

---

## Troubleshooting do Menu

### Problema: Menu não inicia

**Solução**:
```bash
# Verifique Python
python --version  # Deve ser 3.8+

# Verifique o arquivo
ls scripts/main_menu.py

# Tente com python3
python3 scripts/main_menu.py
```

### Problema: Scripts não executam

**Solução**:
```bash
# Verifique permissões
chmod +x scripts/main_menu.py

# Verifique dependências
python scripts/main_menu.py
# Selecione: Configurações → Verificar Dependências
```

### Problema: Caracteres especiais aparecem errados

**Solução**:
```bash
# Configure encoding
export LANG=pt_BR.UTF-8
python scripts/main_menu.py
```

---

## Feedback e Melhorias

O menu foi projetado para ser intuitivo e acessível. Se você tiver sugestões:

1. Use Menu → Recursos → Comunidade
2. Contribua no GitHub
3. Reporte issues no Qiskit

---

## Resumo

O menu interativo oferece:

✅ **Fácil Navegação**: Interface intuitiva para todos os níveis
✅ **Acesso Rápido**: Atalhos para recursos e scripts
✅ **Personalização**: Adapta-se ao seu nível de experiência
✅ **Integração**: Combina aprendizado, desenvolvimento e troubleshooting
✅ **Recursos**: 100+ materiais de aprendizado integrados

**Comece agora**: `python scripts/main_menu.py`
