# OpenCode Ecosystem

Repositório exclusivo para gerenciamento de projetos e automação da instalação do ecossistema do OpenCode e Antigravity no Windows (WSL).

## Diretórios do Repositório

- `docs/` - Documentação e especificações técnicas (Software Design Document - SDD).
- `scripts/` - Scripts de automação e inicialização.
- `tests/` - Scripts de teste e auditoria de ambiente (TDD).
- `projects/` - Pasta exclusiva para seus projetos de desenvolvimento integrados ao ecossistema.

## Como Reproduzir este Ambiente em Outro PC

### 1. Pré-requisitos
Certifique-se de que o WSL (Ubuntu) esteja instalado no Windows.

### 2. Executar os Testes Iniciais (Red)
Na raiz do projeto no Windows, execute:
```bash
.\tests\run_tests.bat
```
*(Os testes devem falhar indicando que o OpenCode ainda não foi instalado no WSL)*

### 3. Executar o Script de Instalação no WSL
Abra o terminal do WSL e execute:
```bash
bash /mnt/c/Users/marce/Documents/OpenCode_Ecosystem/scripts/install_ecosystem.sh
```
*(Isso baixará, instalará o OpenCode e configurará o PATH automaticamente)*

### 4. Executar os Testes Novamente (Green)
Execute novamente o script de auditoria no Windows:
```bash
.\tests\run_tests.bat
```
*(Desta vez, todos os testes deverão passar!)*

---

Para detalhes técnicos e de especificação, consulte o arquivo [docs/sdd.md](docs/sdd.md).
