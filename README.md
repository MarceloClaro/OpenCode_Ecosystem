<div align="center">
  <img src="diagrams/architecture-overview.svg" alt="OpenCode Ecosystem Architecture" width="100%"/>
  
  <h1>OpenCode Ecosystem v5.1</h1>
  <p><strong>A Primeira Agência de Inteligência Artificial Autônoma Operando no Seu PC</strong></p>
</div>

---

## 🌍 O que é o OpenCode Ecosystem? (Visão Geral)

Imagine ter uma empresa inteira de tecnologia, um laboratório de pesquisa e uma banca de cientistas — tudo rodando **localmente, de forma autônoma e gratuita** na sua máquina. 

O **OpenCode Ecosystem** é uma arquitetura revolucionária de Inteligência Artificial Multiagente. Ele não é apenas um "assistente de código", mas um **Hub Operacional Autônomo**. Quando você fornece uma missão (seja criar um aplicativo do zero, cruzar dados financeiros ou escrever um artigo científico de nível Doutorado), o sistema desperta **125 agentes virtuais especialistas**. Eles dividem o trabalho, debatem soluções para evitar erros, programam, auditam a segurança e entregam o resultado pronto e revisado.

---

## 🚀 Para Startups e Investidores (O Valor do Negócio)

- **Execução Híbrida e Inteligente:** O ecossistema é flexível e opera tanto de forma local offline (via **Ollama CLI** com modelos como `opencode/qwen-coder-pro`) quanto integrada com a nuvem (via **Xiaomi MiMo API** com contexto gigante de até 1M de tokens para tarefas longas), extinguindo ou minimizando custos com infraestrutura.
- **Produtividade Exponencial:** O pipeline *AutoEvolve* substitui o fluxo de trabalho de semanas por minutos. Tarefas de planejamento de produto, extração de métricas de mercado (50 indicadores globais) e codificação acontecem em paralelo.
- **Escalabilidade Plug & Play:** Arquitetura agnóstica baseada no novo padrão da indústria (Model Context Protocol). A sua empresa pode injetar "Skills" corporativas proprietárias no cérebro do ecossistema instantaneamente.
- **Governança Preventiva Contra Goal Drift:** O ecossistema implementa a tecnologia de **Preventive Cognitive Guardrails (Barreiras Cognitivas Preventivas)** baseada no *SPEC-038 TrustEngine*. Cada decisão tomada pelos agentes de IA passa por um conselho de auditores de confiança em tempo real, mitigando e eliminando alucinações cognitivas e desvios de objetivos em produção.

---

## ⚙️ Para o Público Técnico (Sob o Capô)

A versão **v5.1** eleva o teto da automação de software operando através de WSL2, Windows e Containers de forma transparente:

- 🧠 **Orquestração Nexus (NMA v6.2):** Framework de sincronização meta-granular responsável por coordenar operações atômicas entre agentes usando 120+ barreiras de concorrência.
- 🤖 **125 Agentes Catalogados & 106 Skills Ativas:** Especialistas dinâmicos geridos via um robusto Container de Injeção de Dependências (DI) transversal.
- 🔌 **Camada Universal de Protocolos (41 Servidores MCP):** Integração *out-of-the-box* com bancos SQLite, Web Crawlers, APIs financeiras, Execução de Código Sandbox (Node/Python) e pontes integradas para o **Antigravity CLI (agy)**.
- 🔬 **Módulo de Pesquisa e IA Avançada:** Integração nativa de Computação Quântica simulada (81 arquiteturas testadas) e DataOrchestrator com RAG Multi-Engine Adaptativo.
- 🧬 **Metacognição Funcional e Auditoria:** Sistema de auto-observação (N0 a N3.5) que se autodiagnostica, propõe patches e executa correções em tempo de execução. Todo o modelo teórico, provas matemáticas de complexidade (Set Cover) e mitigação de auto-referência estão compilados no **Manuscrito de Dissertação de 96 páginas** do projeto.

Para o aprofundamento arquitetural e mapeamento vetorial dos processos, consulte a bíblia do sistema:
👉 **[Documentação Técnica Completa (OPENCODE_ECOSYSTEM.md)](OPENCODE_ECOSYSTEM.md)**
👉 **[Manuscrito de Dissertação Acadêmica (DISSERTACAO_OPENCODE_ECOSYSTEM.pdf)](docs/DISSERTACAO_OPENCODE_ECOSYSTEM.pdf)**

---

## 🛠️ Como Iniciar a Agência no seu Windows / WSL2

O ecossistema foi projetado para auto-gestão inteligente. Você só precisa acordar o orquestrador.

**1. Requisitos Iniciais**
- Ambiente Windows rodando WSL2 (Ubuntu).

**2. Acordando o Sistema**
Abra seu PowerShell como Administrador na pasta raiz e invoque a inicialização:
```powershell
.\start_ecosystem.ps1
```
*(O script se encarrega de levantar os serviços de Inteligência Artificial locais, pontes de proxy e os serviços de container no Linux de forma invisível).*

**3. Auditoria e Validação (Test-Driven)**
Se desejar verificar o pulso dos agentes e atestar que as ferramentas de infraestrutura (MCPs) estão se comunicando sem atritos, dispare a suite de testes no terminal do WSL:
```bash
./tests/test_environment.sh
```

---

> *"O software tradicional exige que você digite os comandos. O OpenCode Ecosystem inventa as soluções."*
> **Construído com excelência para moldar o futuro da Autonomia Digital.**
