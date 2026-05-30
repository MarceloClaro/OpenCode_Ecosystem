---
name: deploy
description: Checklist e procedimento pré-deploy. Execute antes de qualquer deploy em qualquer ambiente. Valida código, ambiente, migrations e comunicação com o time.
disable-model-invocation: true
---

# Skill: deploy

**Quando usar:** Antes de qualquer deploy em qualquer ambiente.

> Este arquivo é um template. Preencha a seção de configuração durante ou após o `/project-init`.
> Veja o diretório `scripts/` para scripts de automação que você pode adicionar.

---

## Configuração deste projeto

<!-- Preencher com os dados reais do projeto -->
- **Staging:** [URL]
- **Produção:** [URL]
- **Comando de deploy:** [comando]
- **Variáveis de ambiente:** [lista ou referência ao .env.example]
- **Migrations:** [sim/não — se sim, qual comando]
- **Rollback:** [procedimento em caso de falha]

---

## Checklist pré-deploy

### Código
- [ ] Branch atualizada com main
- [ ] Todos os testes passando localmente
- [ ] Nenhuma variável de debug ativa
- [ ] Migrations revisadas e testadas (se houver)

### Segurança
- [ ] Nenhum secret hardcoded
- [ ] Variáveis de ambiente de produção conferidas

### Spec
- [ ] Spec da feature atualizada para status `done`
- [ ] `INDEX.md` atualizado
- [ ] Algo a registrar em `lessons.md`?

### Comunicação
- [ ] Time avisado (se houver time)
- [ ] Janela de deploy adequada — evitar horários de pico e fim de semana

---

## Após o deploy

- Monitore logs por 15 minutos
- Confirme as principais funcionalidades manualmente
- Atualize o PR com a data de deploy

## Scripts de suporte

Veja [`scripts/`](scripts/) para scripts opcionais de automação que você pode adicionar a esta skill.
