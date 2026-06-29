# SECRETS — Configuração de Acesso ao GitHub

> **ATENÇÃO**: Este arquivo contém instruções para configurar o acesso ao GitHub.
> Substitua `SEU_PAT_AQUI` pelo token real antes de usar.

---

## 🚀 Push do Livro-Volume2 ao GitHub

### Pré-requisitos

1. **GitHub Personal Access Token (PAT)** com escopo `repo` (clássico) OU
   - Fine-grained PAT com permissão `Contents: Write` no repositório `MarceloClaro/odonto-digital-twin`

### Como criar o PAT

1. Acesse https://github.com/settings/tokens
2. Clique em **"Generate new token (classic)"**
3. Marque o escopo **`repo`** (acesso total a repositórios privados)
4. Gere e **copie o token imediatamente** (só aparece uma vez)

### Como fazer o push (PowerShell)

Abra **PowerShell como Administrador** e execute:

```powershell
# 1. Navegar até o repositório
cd C:\Users\marce\Documents\OpenCode_Ecosystem\livro-volume2

# 2. Configurar remote com token (substitua SEU_PAT_AQUI)
git remote set-url origin https://MarceloClaro:SEU_PAT_AQUI@github.com/MarceloClaro/odonto-digital-twin.git

# 3. Push
git push -u origin main
```

### Alternativa: Usar o script GIT_PUSH.bat

Edite o arquivo `C:\Users\marce\Documents\OpenCode_Ecosystem\livro-volume2\GIT_PUSH.bat`
e substitua `SEU_PAT_AQUI` pelo token real, depois execute como Administrador.

### Verificação

Após o push, verifique em: https://github.com/MarceloClaro/odonto-digital-twin

---

## 🔐 Segurança

- **NUNCA** comite o token no repositório
- **NUNCA** compartilhe o token
- O arquivo `.gitignore` já exclui `.env` e `.env.local`
- Crie um arquivo `.env` na raiz para armazenar o token com segurança:

```
# .env
GITHUB_PAT=seu_token_aqui
```
