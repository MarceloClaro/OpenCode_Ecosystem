# Decisões Arquiteturais

> Registre ANTES de implementar decisões significativas. Consulte antes de refatorar ou propor mudanças de arquitetura.

<!--
FORMATO DE ENTRADA:

## [Título da decisão] — YYYY-MM-DD
**Contexto:** por que essa decisão foi necessária
**Decisão:** o que foi escolhido
**Alternativas descartadas:** o que foi considerado e por que não foi escolhido
**Consequências:** impactos esperados (positivos e negativos)
**Status:** ativa | substituída por [link]
-->

## Questões abertas — 2026-05-06
**Contexto:** Sessão de design thinking encerrada antes de responder questões críticas que impactam a spec.
**Status:** pendente — responder no início da próxima sessão antes de implementar qualquer coisa.

### Usuário
- Quem usa o sistema? Só o dono, time pequeno, ou público aberto?
- Precisa de login/cadastro para salvar perfil e filtros personalizados?

### Produto
- O resumo dos editais será só leitura ou permite exportar (PDF, planilha)?
- Notificações de novos editais por tema — Fase 1 ou Fase 2?
- Qual portal é prioridade absoluta para o MVP?

### Infraestrutura
- VPS já existe? Qual provedor, RAM e CPU? (IA roda via DeepSeek API — sem GPU local)
- Tem domínio para o sistema?

### Negócio
- Sistema gratuito, pago por assinatura, ou uso interno?
