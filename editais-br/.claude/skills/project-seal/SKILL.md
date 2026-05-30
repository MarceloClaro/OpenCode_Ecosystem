---
name: project-seal
description: "Skill do ecossistema OpenCode - project-seal"
---


name: project-seal
description: Fecha o setup inicial do projeto — commita specs, documentação e configuração após project-init + primeira spec. Roda uma vez, logo após a primeira spec ser criada e revisada.
disable-model-invocation: true
argument-hint: "[mensagem de commit opcional]"
---

---
name: project-seal
description: Fecha o setup inicial do projeto — commita specs, documentação e configuração após project-init + primeira spec. Roda uma vez, logo após a primeira spec ser criada e revisada.
disable-model-invocation: true
argument-hint: "[mensagem de commit opcional]"
---

# Skill: project-seal

**Quando executar:** Uma vez, após `project-init` + criação da primeira spec com `spec-create`. Também pode ser usado a qualquer momento para commitar e publicar mudanças de setup/documentação acumuladas.

**Objetivo:** Revisar o que mudou desde o último commit, commitar tudo que é relevante e (opcionalmente) fazer push — garantindo que o repo reflita o estado real do projeto, não o template.

---



## Conteudo de Referencia

Para manter esta skill leve, dados densos foram movidos para arquivos de referencia:

- [`references/protocolo-detalhado.md`](references/protocolo-detalhado.md) — Protocolo Detalhado
