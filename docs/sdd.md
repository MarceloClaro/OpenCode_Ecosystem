# Software Design Document (SDD) - OpenCode Ecosystem

Este documento define o design do repositório [OpenCode_Ecosystem](https://github.com/MarceloClaro/OpenCode_Ecosystem), projetado para automatizar, testar (TDD) e tornar reprodutível o ambiente de desenvolvimento do OpenCode, Ollama e Antigravity no Windows com WSL (Ubuntu).

---

## 1. Objetivos do Sistema

- **Exclusividade:** Concentrar todas as configurações, scripts de instalação, backups e projetos em um único diretório.
- **Reprodutibilidade:** Garantir que o ambiente completo possa ser reconfigurado em outro computador com um único script.
- **Auditabilidade (TDD):** Usar scripts de teste estruturados para validar que todos os requisitos do ambiente estão instalados e funcionando corretamente.
- **Inteligência Local & Vocalização:** Habilitar execução off-line de LLMs eficientes em CPUs com busca interna/externa e síntese de voz nativa.

---

## 2. Estrutura de Diretórios Recomendada

A pasta está localizada em `C:\Users\marce\Documents\OpenCode_Ecosystem` (mapeada no WSL como `/mnt/c/Users/marce/Documents/OpenCode_Ecosystem`). Ela contém:

```text
OpenCode_Ecosystem/
├── docs/
│   ├── sdd.md               # Este documento de design e especificações
│   └── manual_academic_presentation.md # Manual científico e slides de apresentação
├── scripts/
│   ├── install_ecosystem.sh # Script de instalação automatizada dentro do WSL
│   ├── console.sh           # Painel de controle interativo (WSL)
│   ├── console.bat          # Atalho/Launcher Windows para o console.sh
│   ├── chat_ollama.sh       # Interface de Chat Local com Busca e TTS
│   └── run_server.bat       # Script Windows para iniciar o OpenCode
├── tests/
│   ├── test_environment.sh  # Script de teste (TDD) para validar o ambiente WSL
│   └── run_tests.bat        # Executor de testes pelo lado do Windows
└── projects/                # Pasta onde ficarão todos os projetos de desenvolvimento
```

---

## 3. Especificação dos Componentes

### 3.1. Script de Teste (TDD) - `tests/test_environment.sh`
O script executa asserções (testes) automatizadas para verificar a integridade da instalação. Ele retorna código de saída `0` se passar, ou `1` se houver falhas.

| Caso de Teste | Descrição | Validação |
| :--- | :--- | :--- |
| **T1: WSL Running** | Verifica se o ambiente é o Linux WSL. | Valida se `/proc/version` contém 'microsoft'. |
| **T2: User Verification** | Verifica se o usuário ativo é `marcelo`. | Comando `whoami` deve retornar `marcelo`. |
| **T3: OpenCode Installed** | Verifica se o executável `opencode` está no PATH. | Comando `which opencode` deve retornar um caminho válido. |
| **T4: OpenCode Executable** | Verifica se `opencode --version` funciona. | Deve retornar com status `0` e exibir a versão. |
| **T5: Projects Dir** | Verifica se o diretório de projetos existe e tem escrita. | Testa se o caminho `/mnt/c/Users/marce/Documents/OpenCode_Ecosystem/projects` está disponível. |

---

## 4. Integração do Modelo Local (Ollama)

Para prover inteligência local otimizada para CPUs convencionais, foi integrado o **Ollama** com o seguinte design:

- **Motor de Inferência:** Ollama executado sob serviço systemd no WSL.
- **Modelo Selecionado:** `qwen2.5-coder:1.5b`. Este modelo equilibra de forma excelente o tamanho do arquivo (~986MB), o consumo de RAM/CPU e a eficácia na geração e interpretação de código e linguagem natural, alcançando ótimos tokens por segundo em hardware sem GPU dedicada.

---

## 5. Arquitetura de Busca e Vocalização (RAG + TTS)

### 5.1. Mecanismo de Busca Interna e Externa
Para expandir o conhecimento do modelo local com dados em tempo real:
- **Busca Interna:** Mapeada sobre a pasta `projects/` utilizando buscas textuais estruturadas via `grep` de alta velocidade.
- **Busca Externa:** Integração com a API rest da Wikipedia em Português para recuperar artigos conceituais e definições de alta relevância científica.
- **Orquestrador de Contexto:** Mescla os dados encontrados e os entrega estruturados como contexto na pergunta enviada ao modelo.

### 5.2. Síntese de Voz Nativa (TTS)
As saídas das respostas são convertidas em áudio falado de forma nativa e assíncrona:
- O WSL faz a ponte com o Windows executando `powershell.exe` em background.
- A classe do sistema `.NET` `System.Speech.Synthesis.SpeechSynthesizer` é invocada para ler o texto higienizado, provendo vocalização em Português (BR) sem dependências ou latências externas.
