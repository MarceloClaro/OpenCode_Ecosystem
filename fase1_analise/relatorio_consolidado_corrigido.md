# Relatório Consolidado — Fase 1: Análise Documental
## 1.0 Ambiente
- OpenCode CLI v1.15.12 (OK)
- Skill editais-br: 65 editais curados
- Graph: 175 nós, 6 arestas, 110 tags (build_graph.py OK via PYTHONIOENCODING=utf-8)
## 1.1 Curadoria Existente
- CURATED_EDITAIS_FULL.json: 65 editais com scores
- Nenhum edital curado contém "LGPD", "privacidade", "ética" ou "UFC" nos títulos
## 1.2 Buscas Adicionais (5 queries)
### Query 1: "LGPD privacidade dados pessoais pesquisa" (--curadoria-only)
- 10 resultados: todos genéricos (Jovem Pesquisador FAPESP, Auxílio FAPERJ, Universal CNPq, etc.)
- Nenhum focado em LGPD
### Query 2: "Lei 13.709 proteção dados" (--curadoria-only)
- 2 resultados: Lei Rouanet, Lei do Bem
- Ambos com baixa relevância para LGPD
### Query 3: "ética pesquisa integridade acadêmica" (--curadoria-only)
- 5 resultados: genéricos (Universal CNPq, CAPES)
- Nenhum específico sobre ética em IA
### Query 4: "privacidade educação estudantes" (--curadoria-only)
- 5 resultados: genéricos
- Nenhum específico
### Query 5: "UFC PPGTE" (--curadoria-only)
- 5 resultados: genéricos
- Nenhum específico para UFC/PPGTE
## 1.3 Web Search (complementar)
### CNPq Portaria 2.664/2026 ("CNPq Portaria 2664 integridade científica IA")
- Blog doutoranathalia.com.br (análise da portaria)
- gov.br/cnpq (oficial)
- IFSC/USP (divulgação)
- Conteúdo: exige declaração de uso de IA em todas as fases da pesquisa, proíbe submissão de conteúdo gerado por IA como autoria humana
### CNPq Portaria 2.664/2026 (busca "UFMA")
- Notícia UFMA confirmando a nova política de integridade científica
### LGPD pesquisa científica ("LGPD privacidade dados pessoais pesquisa científica Brasil")
- Conteúdo YouTube (2020): vídeos sobre LGPD e pesquisa
- Nenhum edital específico
## 1.4 Grafo de Conhecimento
- Build: OK (175 nós, 6 arestas, 110 tags)
- 174 nós órfãos: grafo precisa de mais arestas entre agentes-skills-MCPs-comandos
- 6 arestas quebradas: referências a nós que não existem mais
## Conclusões Preliminares
1. CNPq Portaria 2.664/2026 é o instrumento-chave: exige transparência no uso de IA em pesquisa
2. Editais curados não cobrem LGPD/privacidade/ética — necessário complemento via web search
3. Grafo construído mas esparso: 99% nós órfãos — precisa de enriquecimento de arestas
4. LGPD aplicada à pesquisa científica tem fontes jurídicas (ANPD, doutrina) mas não editais de fomento
## Próximos Passos (Semana 2)
1. Extração de conceitos legais via entity-ner-reader
2. Mapeamento de requisitos LGPD para funcionalidades OpenCode
3. Preenchimento da Matriz de Conformidade LGPD × OpenCode
