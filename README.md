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

- **Custo Operacional Zero:** Diferente da concorrência que depende de APIs pagas por token (em dólar), o OpenCode foi otimizado para rodar de forma híbrida e local (com modelos de 200K de contexto), extinguindo o custo de nuvem.
- **Produtividade Exponencial:** O pipeline *AutoEvolve* substitui o fluxo de trabalho de semanas por minutos. Tarefas de planejamento de produto, extração de métricas de mercado (50 indicadores globais) e codificação acontecem em paralelo.
- **Escalabilidade Plug & Play:** Arquitetura agnóstica baseada no novo padrão da indústria (Model Context Protocol). A sua empresa pode injetar "Skills" corporativas proprietárias no cérebro do ecossistema instantaneamente.
- **Governança Rigorosa:** A IA não sofre de alucinações desenfreadas. Cada decisão tomada pela máquina passa por um conselho de auditores lógicos baseados na Teoria dos Jogos (Equilíbrio de Nash) e Validação Cruzada antes de ser executada.

---

## ⚙️ Para o Público Técnico (Sob o Capô)

A versão **v5.1** eleva o teto da automação de software operando através de WSL2, Windows e Containers de forma transparente:

- 🧠 **Orquestração Nexus (NMA v6.2):** Framework de sincronização meta-granular responsável por coordenar operações atômicas entre agentes usando 120+ barreiras de concorrência.
- 🤖 **125 Agentes Catalogados & 106 Skills Ativas:** Especialistas dinâmicos geridos via um robusto Container de Injeção de Dependências (DI) transversal.
- 🔌 **Camada Universal de Protocolos (41 Servidores MCP):** Integração *out-of-the-box* com bancos SQLite, Web Crawlers, APIs financeiras, Execução de Código Sandbox (Node/Python) e Motores CJK.
- 🔬 **Módulo de Pesquisa e IA Avançada:** Integração nativa de Computação Quântica simulada (81 arquiteturas testadas) e DataOrchestrator com RAG Multi-Engine Adaptativo.
- 🧬 **Fusão de Frameworks (MASWOS / MiroFish / BettaFish):** Padrões acadêmicos absorvidos no *core* para validação rígida em 8 domínios distintos (Geo, Finance, Crypto, BioMed, Economics, etc.).

Para o aprofundamento arquitetural e mapeamento vetorial dos processos, consulte a bíblia do sistema:
👉 **[Documentação Técnica Completa (OPENCODE_ECOSYSTEM.md)](OPENCODE_ECOSYSTEM.md)**

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
