<!-- Conteudo extraido de project-seal/SKILL.md via progressive-disclosure -->

## Protocolo

### 1 — Diagnóstico do estado atual

Execute e exiba o resultado ao usuário:

```bash
git status
git remote get-url origin
git log --oneline -5
```

Identifique:
- Arquivos modificados/novos que ainda não foram commitados
- Se o remote ainda aponta para o template (`template-claude-code`) — se sim, avise o usuário antes de continuar
- Qual foi o último commit (para contexto da mensagem)

---

### 2 — Revisão dos arquivos a commitar

Liste os arquivos relevantes detectados no `git status`. Agrupe por categoria:

| Categoria | Arquivos típicos |
|-----------|-----------------|
| Configuração do projeto | `CLAUDE.md`, `.claude/memory/MEMORY.md`, `.claude/references.md` |
| Specs | `.claude/specs/*.md`, `.claude/specs/INDEX.md` |
| Documentação | `README.md`, `README_MCP.md` |
| Outros | qualquer arquivo novo criado durante o setup |

Pergunte ao usuário: "Quer incluir todos esses arquivos ou excluir algum?"

---

### 3 — Commit

Monte a mensagem de commit. Se o usuário passou um argumento ao invocar `/project-seal <mensagem>`, use-o. Caso contrário, use o padrão:

```
docs: seal project setup — specs and configuration
```

Execute o commit apenas com os arquivos confirmados pelo usuário:

```bash
git add <arquivos confirmados>
git commit -m "<mensagem>"
```

Mostre o resultado do commit ao usuário.

---

### 4 — Push (opcional, sempre confirmar)

Verifique se o remote está configurado corretamente:

```bash
git remote get-url origin
```

**Se o remote ainda for o template:** pare aqui e exiba:
```
O remote ainda aponta para o template. Antes do push, configure o repositório do novo projeto:
  git remote set-url origin git@github.com:<seu-usuario>/<seu-repo>.git
Depois rode git push -u origin main.
```

**Se o remote já for o novo projeto:** pergunte:
"Deseja fazer push para `origin main` agora?"
- Se sim: `git push -u origin main`
- Se não: exiba o comando para o usuário rodar quando quiser

---

### 5 — Confirmação final

Exiba um resumo:
- Arquivos commitados
- Hash do commit
- Status do push (feito / pendente)
- Próximos passos sugeridos (ex: começar a implementar a primeira spec)
