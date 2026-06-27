# ADR-011: Criação de Skill de Escrita Acadêmica APA

## Status
Aceito

## Data
22/06/2026

## Contexto
O ecossistema OpenCode precisa de suporte padronizado para escrita acadêmica seguindo normas APA 7ª edição, especialmente para Projetos Finais (PF) conforme as normas institucionais. A análise do documento "Normas Projeto Final (PF)" revelou a necessidade de:

1. **Padronização**: Diferentes programas acadêmicos utilizam APA ou Vancouver
2. **Automação**: Geração automática de citações e referências
3. **Validação**: Verificação de conformidade com normas
4. **Integração**: Conexão com agentes e skills existentes

## Decisão
Criar uma skill dedicada de escrita acadêmica APA com as seguintes componentes:

### 1. Skill `apa-academic-writing`
- Documentação completa das normas APA 7ª edição
- Guias práticos para formatação
- Exemplos de citações e referências
- Checklist de conformidade

### 2. SPEC-048: APA Academic Writing
- Especificação técnica para implementação
- Requisitos funcionais e não-funcionais
- Arquitetura de componentes
- Roadmap de implementação

### 3. Hook de Validação APA
- Script bash para validação automática
- Verificações básicas de conformidade
- Integração com pipeline de edição

### 4. Validador Python APA
- Validação detalhada de documentos
- Relatórios de conformidade
- Suporte a múltiplos formatos

## Consequências

### Positivas
- **Consistência**: Documentos acadêmicos seguem padrão uniforme
- **Produtividade**: Automação reduz tempo de formatação
- **Qualidade**: Validação automática melhora conformidade
- **Integração**: Conexão com ecossistema existente
- **Documentação**: Referência centralizada para normas APA

### Negativas
- **Manutenção**: Necessidade de atualizar com mudanças nas normas
- **Complexidade**: Aprendizado inicial para usuários
- **Dependência**: Para workflows que usam outros estilos

### Riscos
- **Mudanças normativas**: APA pode atualizar regras
- **Variações institucionais**: Diferentes programas podem ter requisitos específicos
- **Performance**: Validação pode ser lenta para documentos grandes

## Alternativas Consideradas

### 1. Usar ferramentas externas (Grammarly, Writefull)
- **Prós**: Ferramentas maduras e testadas
- **Contras**: Não integradas ao ecossistema, podem não cobrir todas as normas APA

### 2. Criar apenas documentação (sem automação)
- **Prós**: Simples de implementar
- **Contras**: Não oferece automação ou validação

### 3. Integrar com Zotero/Mendeley diretamente
- **Prós**: Gestão robusta de referências
- **Contras**: Dependência de ferramentas externas, complexidade de integração

## Fatores de Decisão
1. **Necessidade do usuário**: Demanda por suporte APA em PFs
2. **Ecossistema existente**: Agentes e skills já podem ser estendidos
3. **Autonomia**: Controle total sobre implementação
4. **Flexibilidade**: Suporte a múltiplos estilos (APA, Vancouver)

## Plano de Implementação

### Fase 1: Documentação (Semanas 1-2)
- [x] Skill `apa-academic-writing`
- [x] Documentação de normas APA 7ª edição
- [ ] Exemplos práticos e templates

### Fase 2: Validação (Semanas 3-4)
- [x] Hook de validação bash
- [x] Validador Python APA
- [ ] Testes automatizados

### Fase 3: Integração (Semanas 5-6)
- [ ] Conexão com agentes existentes
- [ ] Hooks de pipeline
- [ ] Validação end-to-end

### Fase 4: Refinamento (Semanas 7-8)
- [ ] Feedback dos usuários
- [ ] Otimização de performance
- [ ] Documentação avançada

## Métricas de Sucesso
- **Adoção**: 80% dos novos documentos acadêmicos usam a skill
- **Conformidade**: 95% de aprovação em validações automáticas
- **Satisfação**: Nota ≥ 9/10 em feedback dos usuários
- **Cobertura**: Suporte a 90% dos tipos de referência APA

## Referências
- American Psychological Association. (2020). *Publication manual* (7a ed.)
- Documento: "Normas Projeto Final (PF)"
- SPEC-048: APA Academic Writing
- Skills existentes: `edicao-cirurgica`, `potentiality-estimator-v2`

## Participantes
- **Marcelo Claro**: Orquestrador Supremo (decisão)
- **Ecossistema OpenCode**: Implementação e testes