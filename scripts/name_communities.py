#!/usr/bin/env python3
"""
name_communities.py — Nomeação Semântica das Comunidades Graphify
==================================================================
Algoritmo:
  1. Carrega graph.json (7.099 nós, 376 comunidades, 11.904 arestas)
  2. Para cada comunidade, extrai: labels, arquivos, tipos de relação
  3. Cruza com taxonomia de raciocínios (TAXONOMIA_RACIOCINIOS_AMPLIADA.md)
  4. Cruza com corpus noológico (corpus_noologico_referencia.txt)
  5. Cruza com SPECs (specs/*.md)
  6. Cruza com agentes (AGENTS.md)
  7. Gera nome semântico + registry completo
  8. Exporta COMMUNITY_REGISTRY.md
"""

import json
import re
import csv
import sys
from pathlib import Path
from collections import Counter, defaultdict

# ── Caminhos ─────────────────────────────────────────────────────────────
BASE = Path(__file__).parent.parent
GRAPH_JSON = BASE / "graphify-out" / "graph.json"
TAXONOMIA_MD = BASE / "TAXONOMIA_RACIOCINIOS_AMPLIADA.md"
CORPUS_TXT = BASE / "corpus_noologico_referencia.txt"
AGENTS_MD = BASE / "AGENTS.md"
SPECS_DIR = BASE / "specs"
REGISTRY_MD = BASE / "graphify-out" / "COMMUNITY_REGISTRY.md"
ECOSYSTEM_MD = BASE / "OPENCODE_ECOSYSTEM.md"
ARCHITECTURE_MD = BASE / "diagrams" / "ARCHITECTURE_COMPLETE.md"

# ── 1. Carregar dados de referência ─────────────────────────────────────

def load_graph():
    """Carrega o grafo Graphify."""
    if not GRAPH_JSON.exists():
        print(f"ERRO: {GRAPH_JSON} não encontrado")
        sys.exit(1)
    with open(GRAPH_JSON) as f:
        return json.load(f)


def load_taxonomia():
    """Carrega taxonomia de raciocínios e extrai categorias + tipos."""
    if not TAXONOMIA_MD.exists():
        return {}, []
    text = TAXONOMIA_MD.read_text(encoding="utf-8")
    categorias = {}
    raciocinios = []

    # Extrai categorias (I a XII)
    for m in re.finditer(r'\|\s*\*{0,2}(I{1,3}|IV|V|VI{1,3}|VI{1,3}|X{1,2})\*{0,2}\s*\|\s*(\w[\w\s-]+?)\s*\|', text):
        cat_id = m.group(1)
        cat_name = m.group(2).strip()
        categorias[cat_id] = cat_name

    # Extrai raciocínios (R1-R64)
    for m in re.finditer(r'\|\s*\*{0,2}(R\d+)\*{0,2}\s*\|\s*(\w[\w\s-]+?)\s*\|', text):
        raciocinios.append(m.group(1))

    return categorias, raciocinios


def load_corpus():
    """Carrega corpus noológico e extrai keywords por dimensão."""
    if not CORPUS_TXT.exists():
        return {}
    text = CORPUS_TXT.read_text(encoding="utf-8")
    dimensoes = {}
    current_dim = "Geral"
    for line in text.splitlines():
        m = re.match(r'^##\s+(.+)$', line)
        if m:
            current_dim = m.group(1).strip()
            continue
        if line.strip() and not line.startswith('#'):
            keywords = re.findall(r'\b[a-zà-ú]{4,}\b', line.lower())
            if keywords:
                dimensoes.setdefault(current_dim, []).extend(keywords)
    return dimensoes


def load_agents():
    """Carrega lista de agentes do AGENTS.md."""
    if not AGENTS_MD.exists():
        return []
    text = AGENTS_MD.read_text(encoding="utf-8")
    agents = re.findall(r'^-\s+\*{0,2}([\w-]+)\*{0,2}:', text, re.MULTILINE)
    return agents


def load_specs():
    """Carrega SPECs do diretório specs/."""
    if not SPECS_DIR.exists():
        return []
    return sorted([f.stem for f in SPECS_DIR.glob("*.md") if f.stem.startswith("SPEC") or f.stem.startswith("SPEC")])


# ── 2. Análise de Comunidade ────────────────────────────────────────────

def analyze_communities(graph, tax_categorias, raciocinios, corpus, agents, specs):
    """Analisa todas as comunidades e gera nome semântico para cada."""
    nodes = graph.get("nodes", [])
    links = graph.get("links", [])

    # Agrupa nós por comunidade
    comm_nodes = defaultdict(list)
    for n in nodes:
        c = n.get("community", -1)
        if c >= 0:
            comm_nodes[c].append(n)

    # Mapa nó → comunidade
    node_comm = {n.get("id"): n.get("community") for n in nodes}

    # Arestas inter-comunidade
    inter_edges = set()
    for link in links:
        s = link.get("source")
        t = link.get("target")
        sc = node_comm.get(s)
        tc = node_comm.get(t)
        if sc is not None and tc is not None and sc != tc:
            inter_edges.add((sc, tc))

    # Prepara texto da taxonomia para matching
    tax_text = TAXONOMIA_MD.read_text(encoding="utf-8").lower() if TAXONOMIA_MD.exists() else ""

    # Prepara texto do corpus
    corpus_text = ""
    if CORPUS_TXT.exists():
        corpus_text = CORPUS_TXT.read_text(encoding="utf-8").lower()

    # Prepara texto dos agents
    agents_text = AGENTS_MD.read_text(encoding="utf-8").lower() if AGENTS_MD.exists() else ""

    # Prepara lista de spec names
    spec_names = [s.lower() for s in specs]

    # ── Mapa de conhecimento: arquivo → domínio ────────────────────────
    FILE_DOMAIN_MAP = {
        # Raciocínio / Lógica
        "micro_reasoning": "Raciocínio e Lógica",
        "reasoning": "Raciocínio e Lógica",
        "aletheia": "Raciocínio e Lógica",
        "arche": "Raciocínio e Lógica",
        "rlt": "Raciocínio e Lógica",
        "peirce": "Raciocínio e Lógica",
        # Conhecimento / Grafos
        "knowledge_graph": "Conhecimento e Grafos",
        "graph": "Conhecimento e Grafos",
        "ontology": "Conhecimento e Grafos",
        "entity": "Conhecimento e Grafos",
        # Ecossistema / Scanners
        "ecosystem_capabilities": "Ecossistema e Scanners",
        "scanner": "Ecossistema e Scanners",
        "noological": "Ecossistema e Scanners",
        "teleological": "Ecossistema e Scanners",
        "evolutionary": "Ecossistema e Scanners",
        "potentiality": "Ecossistema e Scanners",
        # Evolução
        "evolution": "Evolução e Feedback",
        "feedback": "Evolução e Feedback",
        "evolve": "Evolução e Feedback",
        "learning": "Evolução e Feedback",
        # Sincronização
        "sync": "Sincronização e Orquestração",
        "orchestr": "Sincronização e Orquestração",
        "barrier": "Sincronização e Orquestração",
        # Token Economy
        "token": "Economia de Tokens",
        "economy": "Economia de Tokens",
        "staking": "Economia de Tokens",
        "fee": "Economia de Tokens",
        "ledger": "Economia de Tokens",
        # Domain Shift
        "domain_shift": "Domain Shift e Auditoria",
        "audit": "Domain Shift e Auditoria",
        "shift": "Domain Shift e Auditoria",
        # Witness / Trust
        "witness": "Trust e Witness Pattern",
        "trust": "Trust e Witness Pattern",
        "gate": "Trust e Witness Pattern",
        "behavior": "Trust e Witness Pattern",
        # OQS / Questions
        "oqs": "Optimal Question Scanner",
        "question": "Optimal Question Scanner",
        "uncertainty": "Optimal Question Scanner",
        # ASDE
        "asde": "ASDE — Descoberta Científica",
        "experiment": "ASDE — Descoberta Científica",
        "research": "ASDE — Descoberta Científica",
        # MCP
        "mcp": "MCP e Adaptadores",
        "adapter": "MCP e Adaptadores",
        "bridge": "MCP e Adaptadores",
        # Estatística
        "statistic": "Estatística e Métricas",
        "test_d3": "Estatística e Métricas",
        "metric": "Estatística e Métricas",
        # Academic
        "academic": "Pipeline Acadêmico",
        "paper": "Pipeline Acadêmico",
        "qualis": "Pipeline Acadêmico",
        "article": "Pipeline Acadêmico",
        # Quantum
        "quantum": "Computação Quântica",
        "qubit": "Computação Quântica",
        # Social
        "social": "Algoritmos Sociais",
        "algorithm": "Algoritmos Sociais",
        # Game Theory
        "game": "Teoria dos Jogos",
        "nash": "Teoria dos Jogos",
        # Nexus
        "nexus_integration": "Integração Nexus",
        "nexus": "Integração Nexus",
        "di": "Integração Nexus",
        # Metacognição
        "metacogn": "Metacognição e Self-Model",
        "self": "Metacognição e Self-Model",
        "introspect": "Metacognição e Self-Model",
        # Docling
        "docling": "Docling e PDF",
        "pdf": "Docling e PDF",
        # Testes Gerais
        "test_ecosystem": "Testes do Ecossistema",
        "test_": "Testes e Validação",
        # Agentes
        "agent": "Agentes e Skills",
        "skill": "Agentes e Skills",
    }

    # ── Gerar nome para cada comunidade ────────────────────────────────
    results = []
    for cid in sorted(comm_nodes.keys()):
        nodes_in = comm_nodes[cid]
        size = len(nodes_in)

        # Extrai labels
        labels = [n.get("label", "") for n in nodes_in]
        labels_str = " ".join(labels).lower()

        # Extrai arquivos fonte
        files = [n.get("source_file", "") for n in nodes_in if n.get("source_file")]
        file_names = [Path(f).stem for f in files if f != "?"]
        file_counter = Counter(file_names)
        top_files = file_counter.most_common(5)

        # Extrai classes e funções (labels que contêm ponto ou começam com maiúscula)
        classes = [l for l in labels if l and l[0].isupper() and '.' not in l and not l.endswith('.py')]
        functions = [l for l in labels if l and l.startswith('.')]
        top_classes = Counter(classes).most_common(3)
        top_funcs = Counter(functions).most_common(3)

        # Determina domínio
        domain_scores = Counter()
        for fname, _ in top_files:
            for key, domain in FILE_DOMAIN_MAP.items():
                if key in fname.lower():
                    domain_scores[domain] += 1
        # Também verifica labels
        for key, domain in FILE_DOMAIN_MAP.items():
            if key in labels_str:
                domain_scores[domain] += 0.5

        primary_domain = domain_scores.most_common(1)[0][0] if domain_scores else "Geral"

        # Encontra SPECs relacionadas
        related_specs = []
        for spec in specs:
            spec_lower = spec.lower()
            # Procura SPEC no texto da comunidade
            if spec_lower.replace("-", "_") in labels_str or \
               spec_lower.replace("spec-", "spec") in labels_str:
                related_specs.append(spec)
            # Ou no nome dos arquivos
            for fname, _ in top_files:
                if spec_lower.replace("spec-", "") in fname.lower():
                    related_specs.append(spec)
                    break

        # Encontra agentes relacionados
        related_agents = []
        for agent in agents:
            if agent.lower() in labels_str:
                related_agents.append(agent)
            for fname, _ in top_files:
                if agent.lower() in fname.lower():
                    related_agents.append(agent)
                    break

        # Encontra raciocínios relacionados
        related_reasoning = []
        for r in raciocinios:
            if r.lower() in labels_str:
                related_reasoning.append(r)
        # Match por domínio
        domain_reasoning_map = {
            "Raciocínio e Lógica": ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9"],
            "Conhecimento e Grafos": ["R54", "R55", "R56"],
            "Ecossistema e Scanners": ["R60", "R61", "R62"],
            "Evolução e Feedback": ["R4", "R5"],
            "Sincronização e Orquestração": ["R54", "R56"],
            "Economia de Tokens": ["R48", "R49", "R50", "R51"],
            "Domain Shift e Auditoria": ["R44", "R45", "R46"],
            "Trust e Witness Pattern": ["R31", "R32"],
            "Optimal Question Scanner": ["R2", "R3", "R10"],
            "ASDE — Descoberta Científica": ["R35", "R36", "R37", "R38", "R39", "R40", "R41"],
            "Pipeline Acadêmico": ["R35", "R37", "R39", "R60"],
            "Estatística e Métricas": ["R37", "R12", "R13"],
            "Teoria dos Jogos": ["R48", "R49", "R50"],
            "Metacognição e Self-Model": ["R31", "R32", "R33", "R34"],
            "MCP e Adaptadores": ["R54", "R55"],
            "Agentes e Skills": ["R56", "R57"],
        }
        dr = domain_reasoning_map.get(primary_domain, [])
        for r in dr:
            if r not in related_reasoning:
                related_reasoning.append(r)

        # Conexões inter-comunidade
        connections = []
        for sc, tc in inter_edges:
            if sc == cid:
                connections.append(tc)
            elif tc == cid:
                connections.append(sc)
        top_connections = sorted(set(connections), key=lambda x: len(comm_nodes.get(x, [])), reverse=True)[:5]

        # Match com corpus noológico
        matched_dimensoes = set()
        if corpus:
            for dim, keywords in corpus.items():
                if any(kw in labels_str for kw in keywords[:20]):
                    matched_dimensoes.add(dim)

        # ── GERAR NOME SEMÂNTICO ──────────────────────────────────────
        # Regras de nomeação:
        # 1. Usa classes/funções principais + domínio
        # 2. Se houver classes, usa o nome da classe principal
        # 3. Se não, usa o arquivo principal + domínio
        # 4. Garante que não seja genérico

        # Tenta extrair um nome específico
        specific_name = ""

        # Prioridade 1: classe principal
        if top_classes:
            specific_name = top_classes[0][0]
        # Prioridade 2: função principal
        elif top_funcs:
            specific_name = top_funcs[0][0].lstrip(".")
        # Prioridade 3: arquivo principal (sem extensão)
        elif top_files:
            fname = top_files[0][0]
            # Converte snake_case para Title Case
            fname = fname.replace("_", " ").replace("-", " ").title()
            # Remove prefixos genéricos
            for prefix in ["Test ", "Teste ", "Spec "]:
                if fname.startswith(prefix):
                    fname = fname[len(prefix):]
            specific_name = fname

        # Se o nome for genérico, usa o domínio
        generic_names = {"test", "teste", "spec", "main", "index", "base", "core", "utils", "util", "helper"}
        if specific_name.lower().strip() in generic_names:
            specific_name = ""

        # Sanitiza: remove caracteres que quebram Markdown/CSV
        def sanitize(s):
            return s.replace('|', '-').replace('\n', ' ').replace('\r', '').replace(
                '[', '(').replace(']', ')').strip()

        # Monta nome final
        if specific_name:
            semantic_name = sanitize(f"{primary_domain}: {specific_name}")
        else:
            semantic_name = sanitize(primary_domain)

        # Garante que não fique genérico
        if semantic_name == "Geral":
            # Tenta algo mais específico dos labels
            unique_labels = [l for l in labels if l and not l.endswith('.py') and len(l) > 5]
            if unique_labels:
                semantic_name = f"Especializado: {Counter(unique_labels).most_common(1)[0][0]}"
            else:
                semantic_name = f"Comunidade {cid}"

        results.append({
            "id": f"C{cid}",
            "name": semantic_name,
            "size": size,
            "files": ", ".join(f"{f[0]}.py" for f in top_files[:3]),
            "specs": ", ".join(sorted(set(related_specs))[:5]) if related_specs else "-",
            "agents": ", ".join(sorted(set(related_agents))[:5]) if related_agents else "-",
            "reasoning": ", ".join(sorted(set(related_reasoning))[:5]) if related_reasoning else "-",
            "connections": ", ".join(f"C{c}" for c in top_connections) if top_connections else "-",
            "domain": primary_domain,
            "matched_dimensoes": ", ".join(sorted(matched_dimensoes)[:3]) if matched_dimensoes else "-",
            "top_classes": ", ".join(f"{c[0]}" for c in top_classes[:3]) if top_classes else "-",
            "top_funcs": ", ".join(f"{f[0]}" for f in top_funcs[:3]) if top_funcs else "-",
        })

    return results


# ── 3. Gerar REGISTRY Markdown ──────────────────────────────────────────

def generate_registry_md(communities):
    """Gera COMMUNITY_REGISTRY.md completo."""
    lines = []
    lines.append("---")
    lines.append("title: \"Graphify Community Registry — Mapa Semântico do Ecossistema\"")
    lines.append("version: \"1.0.0\"")
    lines.append("date: \"2026-07-04\"")
    lines.append("generated_by: \"name_communities.py\"")
    lines.append("total_communities: \"376\"")
    lines.append(f"registered: \"{len(communities)}\"")
    lines.append("---")
    lines.append("")
    lines.append("# 🌐 Graphify Community Registry")
    lines.append("")
    lines.append(f"> **{len(communities)} comunidades nomeadas** de 376 totais (7.099 nós, 11.904 arestas).")
    lines.append("> Cada comunidade mapeia para um subsistema do ecossistema. Use `graphify query` para navegar.")
    lines.append("")
    lines.append("## Legenda")
    lines.append("")
    lines.append("| Coluna | Descrição |")
    lines.append("|--------|-----------|")
    lines.append("| **ID** | Identificador da comunidade (C0-C375) |")
    lines.append("| **Nome Semântico** | Nome derivado dos labels + domínio |")
    lines.append("| **Nós** | Quantidade de nós na comunidade |")
    lines.append("| **Arquivos Core** | Top 3 arquivos mais frequentes |")
    lines.append("| **SPECs** | SPECs relacionadas |")
    lines.append("| **Agentes** | Agentes que atuam na comunidade |")
    lines.append("| **Raciocínios** | Tipos de raciocínio (taxonomia R1-R64) |")
    lines.append("| **Conexões** | Comunidades vizinhas |")
    lines.append("| **Domínio Noológico** | Classificação noológica |")
    lines.append("")
    lines.append("## Registry Completo")
    lines.append("")
    lines.append("| ID | Nome Semântico | Nós | Arquivos Core | SPECs | Agentes | Raciocínios | Conexões | Domínio Noológico |")
    lines.append("|----|----------------|:---:|---------------|-------|---------|-------------|----------|-------------------|")

    for c in communities:
        lines.append(
            f"| {c['id']} | {c['name']} | {c['size']} | {c['files']} | "
            f"{c['specs']} | {c['agents']} | {c['reasoning']} | "
            f"{c['connections']} | {c['domain']} |"
        )

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Top 20 — Maiores Comunidades")
    lines.append("")
    lines.append("| # | ID | Nome Semântico | Nós | % do Total |")
    lines.append("|---|----|----------------|:---:|:----------:|")

    top20 = sorted(communities, key=lambda c: c["size"], reverse=True)[:20]
    total_nodes = sum(c["size"] for c in communities)
    accum = 0
    for i, c in enumerate(top20, 1):
        pct = 100 * c["size"] / total_nodes
        accum += pct
        lines.append(f"| {i} | {c['id']} | {c['name']} | {c['size']} | {pct:.1f}% |")

    lines.append(f"| | **Total Top 20** | | **{sum(c['size'] for c in top20)}** | **{accum:.1f}%** |")
    lines.append("")
    lines.append("## Métricas do Grafo")
    lines.append("")
    lines.append(f"- **Nós totais**: {total_nodes}")
    lines.append(f"- **Arestas totais**: carregar do graph.json")
    lines.append(f"- **Comunidades**: 376")
    lines.append(f"- **Nomeadas**: {len(communities)}")
    lines.append(f"- **Cobertura top 20**: {accum:.1f}%")
    lines.append(f"- **Média de nós/comunidade**: {total_nodes/376:.1f}")
    lines.append("")
    lines.append("## Como Usar")
    lines.append("")
    lines.append("```bash")
    lines.append("# Navegar por comunidade")
    lines.append("graphify query \"comunidade C0\"")
    lines.append("graphify explain \"Micro Reasoning\"")
    lines.append("graphify path \"C0\" \"C3\"")
    lines.append("")
    lines.append("# Buscar por domínio")
    lines.append("graphify query \"raciocínio abdutivo\"")
    lines.append("graphify query \"token economy\"")
    lines.append("```")
    lines.append("")

    return "\n".join(lines)


# ── 4. Gerar Seção para OPENCODE_ECOSYSTEM.md ────────────────────────────

def generate_ecosystem_section(communities):
    """Gera seção Graphify Community Map para OPENCODE_ECOSYSTEM.md."""
    top10 = sorted(communities, key=lambda c: c["size"], reverse=True)[:10]

    lines = []
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 🌐 Graphify Community Map v1.0")
    lines.append("")
    lines.append("> Mapa de conhecimento do ecossistema: **7.099 nós, 11.904 arestas, 376 comunidades**")
    lines.append("> gerado pelo Graphify a partir de 245 arquivos Python. Use `graphify query` para navegar.")
    lines.append("")
    lines.append("### Top 10 Comunidades")
    lines.append("")
    lines.append("| ID | Nome Semântico | Nós | SPECs | Agentes |")
    lines.append("|----|----------------|:---:|-------|---------|")

    for c in top10:
        lines.append(f"| {c['id']} | {c['name']} | {c['size']} | {c['specs'][:60]} | {c['agents'][:60]} |")

    lines.append("")
    lines.append("### Registry Completo")
    lines.append("")
    lines.append("Consulte `graphify-out/COMMUNITY_REGISTRY.md` para todas as 376 comunidades.")
    lines.append("")
    lines.append("### Fluxo de Navegação")
    lines.append("")
    lines.append("```")
    lines.append("graphify query \"<comunidade|domínio|raciocínio>\"")
    lines.append("graphify explain \"<nome da comunidade>\"")
    lines.append("graphify path \"<comunidade A>\" \"<comunidade B>\"")
    lines.append("```")
    lines.append("")
    lines.append("### Métricas")
    lines.append("")
    lines.append(f"- **Nós**: 7.099")
    lines.append(f"- **Arestas**: 11.904")
    lines.append(f"- **Comunidades**: 376")
    lines.append(f"- **Nomeadas**: {len(communities)}")
    lines.append(f"- **Top 10 cobre**: {sum(c['size'] for c in top10):,} nós ({100*sum(c['size'] for c in top10)/sum(c['size'] for c in communities):.1f}%)")
    lines.append("")

    return "\n".join(lines)


# ── 5. Pipeline de Integração no OPENCODE_ECOSYSTEM.md ─────────────────

def update_ecosystem_md(section_text):
    """Insere ou atualiza a seção Graphify no OPENCODE_ECOSYSTEM.md."""
    if not ECOSYSTEM_MD.exists():
        print(f"AVISO: {ECOSYSTEM_MD} não encontrado")
        return False

    text = ECOSYSTEM_MD.read_text(encoding="utf-8")

    # Remove seção antiga se existir
    text = re.sub(
        r'\n---\n\n## 🌐 Graphify Community Map.*?(?=\n---\n\n## |\Z)',
        '',
        text,
        flags=re.DOTALL
    )

    # Encontra o final do documento antes do footer
    # Insere antes do último "---" ou no final
    insert_point = text.rfind("\n---\n")
    if insert_point > 0:
        # Verifica se é o footer final
        remaining = text[insert_point+5:].strip()
        if remaining.startswith(">") or "Repositório" in remaining:
            # É footer, insere antes
            text = text[:insert_point] + section_text + "\n" + text[insert_point+1:]
        else:
            text += section_text
    else:
        text += section_text

    ECOSYSTEM_MD.write_text(text, encoding="utf-8")
    print(f"✅ {ECOSYSTEM_MD} atualizado")
    return True


# ── 6. Main ──────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  name_communities.py — Nomeação Semântica de Comunidades")
    print("=" * 60)

    # Carrega dados
    print("\n📥 Carregando graph.json...")
    graph = load_graph()
    print(f"   {len(graph.get('nodes', []))} nós, {len(graph.get('links', []))} arestas")

    print("📥 Carregando taxonomia de raciocínios...")
    tax_categorias, raciocinios = load_taxonomia()
    print(f"   {len(tax_categorias)} categorias, {len(raciocinios)} raciocínios")

    print("📥 Carregando corpus noológico...")
    corpus = load_corpus()
    print(f"   {len(corpus)} dimensões")

    print("📥 Carregando agentes...")
    agents = load_agents()
    print(f"   {len(agents)} agentes")

    print("📥 Carregando SPECs...")
    specs = load_specs()
    print(f"   {len(specs)} SPECs")

    # Analisa e nomeia
    print("\n🧠 Analisando comunidades e gerando nomes semânticos...")
    communities = analyze_communities(graph, tax_categorias, raciocinios, corpus, agents, specs)
    print(f"   {len(communities)} comunidades nomeadas")

    # Mostra top 10
    print("\n📊 Top 10 Comunidades Nomeadas:")
    print(f"   {'ID':<5} {'Nome Semântico':<45} {'Nós':<6} {'Domínio':<30}")
    print(f"   {'-'*5} {'-'*45} {'-'*6} {'-'*30}")
    for c in sorted(communities, key=lambda x: x["size"], reverse=True)[:10]:
        print(f"   {c['id']:<5} {c['name']:<45} {c['size']:<6} {c['domain']:<30}")

    # Gera registry
    print("\n📝 Gerando COMMUNITY_REGISTRY.md...")
    registry_md = generate_registry_md(communities)
    REGISTRY_MD.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_MD.write_text(registry_md, encoding="utf-8")
    print(f"   ✅ {REGISTRY_MD} — {len(communities)} entradas")

    # Gera seção para ecosystem
    print("\n📝 Gerando seção Graphify para OPENCODE_ECOSYSTEM.md...")
    section = generate_ecosystem_section(communities)
    update_ecosystem_md(section)

    # Exporta CSV para auditoria
    csv_path = BASE / "graphify-out" / "community_registry.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=communities[0].keys())
        writer.writeheader()
        writer.writerows(communities)
    print(f"   ✅ {csv_path}")

    print("\n" + "=" * 60)
    print("  ✅ Nomeação concluída com sucesso!")
    print("=" * 60)

    return communities


if __name__ == "__main__":
    result = main()
