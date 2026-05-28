<!-- SAIDA OBRIGATORIA: PORTUGUES BRASILEIRO FORMAL -->
<!-- Inspirado por: Engenharia de Software com Agentes Inteligentes (Sandeco, 2026), Cap. 4 -->

---
name: maintenance-first
description: Design patterns e arquitetura em camadas para codigo mantivel com IA. 67% do custo do software esta na manutencao. Construa pensando nisso.
version: 1.0.0
author: ecosystem
category: superpowers
inspired_by: Engenharia de Software com Agentes Inteligentes (Sandeco) / Pressman SWEBOK
compatibility: deepseek-v4-pro
created_at: 2026-05-27
based_on_chapter: Cap. 4 - Criando de olho na Manutencao
---

# Maintenance-First Design

> "A manutencao consome 67% do custo total do ciclo de vida do software. A fase que recebe menos atencao no planejamento e a que mais custa." — Pressman, via Cap. 4

Quando voce instrui um agente inteligente a gerar codigo, ele nao tem compromisso com a manutenibilidade. Ele gera codigo funcional. Manutenivel e responsabilidade do engenheiro que define as diretrizes. Esta skill estabelece as diretrizes.

## Os 5 Design Patterns Essenciais para Manutencao

### 1. Repository — Separe negocio do banco

O agente tende a espalhar queries SQL pelo codigo. O padrao Repository concentra todo acesso a dados em uma unica camada. Quando o banco mudar (e vai mudar), voce altera um arquivo, nao cem.

```
# Regra para o agente:
# "Toda query de banco deve estar em uma classe Repository.
#  Nenhuma funcao de negocio pode conter SQL ou ORM direto."
```

### 2. Strategy — Comportamento intercambiavel

O agente tende a usar if/else em cascata para variacoes de comportamento. Strategy encapsula cada variacao em sua propria classe. Adicionar uma nova estrategia nao exige modificar codigo existente (Open/Closed Principle).

```
# Regra para o agente:
# "Se ha mais de 2 variacoes de um mesmo comportamento (ex: metodos de pagamento,
#  algoritmos de calculo, tipos de notificacao), use Strategy, nao if/else."
```

### 3. Observer — Desacople emissor do receptor

O agente tende a acoplar diretamente quem gera eventos com quem reage a eles. Observer desacopla: o emissor nao sabe quem ouve. Adicionar novos ouvintes nao mexe no emissor.

```
# Regra para o agente:
# "Eventos do sistema (login, compra, erro) devem usar pub/sub,
#  nao chamadas diretas. Quem emite nao conhece quem recebe."
```

### 4. Singleton — Uma unica instancia, com controle

O agente pode criar multiplas conexoes de banco, multiplos loggers, multiplos clients HTTP. Singleton garante instancia unica para recursos que precisam ser compartilhados.

```
# Regra para o agente:
# "Conexoes de banco, configuracoes globais e loggers devem ser Singleton.
#  Nao recrie conexoes a cada requisicao."
```

### 5. Factory Method — Crie objetos sem acoplar a classes concretas

O agente tende a usar `new ClasseConcreta()` diretamente. Factory Method delega a criacao para subclasses, permitindo que o codigo funcione com qualquer implementacao da interface.

```
# Regra para o agente:
# "Se o codigo da 'new' em uma classe concreta que tem interface,
#  extraia para um Factory Method. O codigo cliente deve depender da interface."
```

## Arquitetura em Camadas (Layered Architecture)

Toda geracao de codigo pelo agente deve respeitar estas 3 camadas:

```
┌─────────────────────────────────┐
│  Apresentacao (UI/API)          │  ← Controllers, DTOs, validacao de entrada
│  NAO contem logica de negocio   │
├─────────────────────────────────┤
│  Negocio (Domain/Services)       │  ← Regras, entidades, casos de uso
│  NAO contem SQL nem HTTP        │
├─────────────────────────────────┤
│  Dados (Repository/Infra)        │  ← Acesso a banco, APIs externas, filesystem
│  NAO contem regras de negocio   │
└─────────────────────────────────┘
```

Regra de ouro: uma camada so conhece a camada imediatamente inferior. Apresentacao conhece Negocio. Negocio conhece Dados. NUNCA o contrario.

## Instrucoes para o Agente (Prompt Template)

Ao solicitar codigo a um agente, inclua este bloco:

```
"Diretrizes de manutencao obrigatorias:
1. Use arquitetura em 3 camadas (controller → service → repository)
2. Toda query de banco vai na camada de dados (Repository)
3. Nenhuma regra de negocio na camada de apresentacao
4. Se houver 3+ variacoes de comportamento, use Strategy
5. Eventos do sistema usam Observer (pub/sub), nao chamada direta
6. Conexoes e configuracoes usam Singleton
7. Toda funcao publica tem tipagem explicita de entrada e saida
8. Nomes de variaveis e funcoes descrevem O QUE fazem, nao COMO
9. Cada funcao faz UMA coisa (Single Responsibility)
10. Nenhum metodo com mais de 30 linhas"
```

## Categorias de Manutencao (SWEBOK)

Ao planejar mudancas, classifique-as. Isso ajuda o agente a entender o contexto:

| Categoria | % do esforco | Descricao |
|-----------|-------------|-----------|
| Evolutiva | 50% | Adicionar funcionalidades que o cliente nao sabia que precisava |
| Adaptativa | 25% | Ajustar quando o ambiente muda (SO, banco, API externa) |
| Corretiva | 21% | Consertar o que quebrou em producao |
| Preventiva | 4% | Refatorar ANTES que o problema apareca (a mais valiosa) |

## Checklist de Manutenibilidade

Antes de aceitar codigo gerado pelo agente, verifique:

- [ ] E possivel adicionar uma funcionalidade sem reescrever modulos inteiros?
- [ ] E possivel trocar o banco de dados alterando apenas a camada Repository?
- [ ] E possivel entender o que cada funcao faz pelo nome?
- [ ] Existem testes que documentam o comportamento esperado?
- [ ] O codigo esta em camadas (apresentacao / negocio / dados)?
- [ ] Nao ha SQL ou chamadas HTTP na camada de negocio?
- [ ] Nao ha regras de negocio na camada de apresentacao?
- [ ] Alguem que nao escreveu o codigo consegue mante-lo?

Se menos de 6 itens marcados: pecA ao agente para refatorar ANTES de fazer merge. O custo de corrigir arquitetura ruim em producao e 3x maior do que corrigir agora.

## O que NUNCA aceitar do agente

- Codigo com funcao de 100+ linhas fazendo "tudo"
- Variaveis com nome de 1 letra (exceto contadores de loop)
- SQL espalhado em 5 arquivos diferentes
- Regras de negocio duplicadas em 2+ lugares
- Funcao que modifica estado global sem documentar
- Tratamento de erro com `except: pass` (silenciar erro)

## Integracao

| Componente | Tipo | Conexao |
|-----------|------|---------|
| ai-engineering-harness | Skill | Disciplina de processo |
| test-driven-development | Skill | Cobertura de testes |
| code-review | Skill | Revisao de qualidade |
| decisionnode | MCP | Registro de decisoes de arquitetura |
