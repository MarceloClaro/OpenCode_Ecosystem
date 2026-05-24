"""Camada 2: Motor de síntese.

Aqui mora o "padrão wiki": pega uma fonte e a integra à wiki existente,
atualizando páginas, criando novas, sinalizando contradições.

Estratégia para modelos locais (Ollama):
- Ingestão é quebrada em 3 etapas: ANALISAR → CRIAR PÁGINA DE FONTE → ATUALIZAR PÁGINAS DE ENTIDADES
- Cada etapa é uma chamada LLM independente, com prompt focado e (quando possível) JSON mode.
- Validação programática entre etapas.
"""
from __future__ import annotations
from datetime import datetime, timedelta
from pathlib import Path
import re
from typing import Optional, Iterator

from src import storage, llm
from src.config import Config, WIKI_DIR, SCHEMA_PATH


PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


# ---------- Schema management ----------

def get_schema() -> str:
    """Lê o schema atual. Se não existir, copia do default."""
    if not SCHEMA_PATH.exists():
        default = (PROMPTS_DIR / "schema_default.md").read_text(encoding="utf-8")
        SCHEMA_PATH.parent.mkdir(parents=True, exist_ok=True)
        SCHEMA_PATH.write_text(default, encoding="utf-8")
    return SCHEMA_PATH.read_text(encoding="utf-8")


def save_schema(content: str) -> None:
    SCHEMA_PATH.write_text(content, encoding="utf-8")
    storage.log_event("edit", "Schema atualizado pelo usuário")


def reset_schema() -> str:
    """Volta ao schema default."""
    default = (PROMPTS_DIR / "schema_default.md").read_text(encoding="utf-8")
    save_schema(default)
    return default


# ---------- Helpers ----------

def _load_prompt(name: str) -> str:
    return (PROMPTS_DIR / f"{name}.md").read_text(encoding="utf-8")


def _kebab(text: str) -> str:
    """Converte texto em slug kebab-case sem acentos."""
    import unicodedata
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[\s_]+", "-", text).strip("-")
    return text or "sem-titulo"


def _existing_pages_summary(limit: int = 30) -> str:
    """Lista resumida de páginas existentes para incluir no prompt."""
    pages = storage.list_pages()
    if not pages:
        return "(nenhuma página existe ainda — esta é a primeira ingestão)"
    lines = []
    for p in pages[:limit]:
        lines.append(f"- {p['path']} ({p['title']})")
    if len(pages) > limit:
        lines.append(f"... e mais {len(pages) - limit} páginas")
    return "\n".join(lines)


def _truncate_for_context(text: str, max_chars: int = 8000) -> str:
    """Trunca texto preservando início e fim — modelos locais têm contexto limitado."""
    if len(text) <= max_chars:
        return text
    head = text[: max_chars * 2 // 3]
    tail = text[-max_chars // 3:]
    return f"{head}\n\n[...trecho intermediário omitido por limitação de contexto...]\n\n{tail}"


# ---------- INGEST ----------

def analyze_source(source_id: str) -> dict:
    """Etapa 1 da ingestão: pede ao LLM para analisar a fonte (apenas).

    NÃO escreve nada na wiki ainda. Retorna o JSON de análise para o usuário revisar.
    """
    src = storage.get_source(source_id)
    if not src:
        raise ValueError(f"Fonte {source_id} não encontrada")

    prompt = _load_prompt("ingest_analyze").format(
        schema=get_schema(),
        existing_pages=_existing_pages_summary(),
        filename=src["filename"],
        source_text=_truncate_for_context(src["content_text"]),
    )

    schema_hint = '{"summary": "...", "key_points": [...], "entities_mentioned": [...], "potential_conflicts": [...], "source_bias": "...", "source_type": "..."}'
    analysis = llm.chat_json(
        messages=[{"role": "user", "content": prompt}],
        schema_hint=schema_hint,
    )

    # Validação programática
    analysis.setdefault("summary", "")
    analysis.setdefault("key_points", [])
    analysis.setdefault("entities_mentioned", [])
    analysis.setdefault("potential_conflicts", [])
    analysis.setdefault("source_bias", "medio")
    analysis.setdefault("source_type", "outro")

    return analysis


def commit_ingestion(source_id: str, analysis: dict) -> dict:
    """Etapa 2-3 da ingestão: cria a página de fonte e atualiza/cria páginas de entidades.

    Retorna um relatório do que foi criado/atualizado.

    Idempotente: se a fonte já foi marcada como ingerida, retorna relatório vazio
    indicando que a operação foi pulada (proteção contra cliques duplos ou reruns).
    """
    src = storage.get_source(source_id)
    if not src:
        raise ValueError(f"Fonte {source_id} não encontrada")

    if src.get("ingested_at"):
        return {
            "source_page": src.get("summary_page"),
            "pages_updated": [],
            "pages_created": [],
            "errors": [],
            "skipped": True,
            "reason": f"Fonte já foi ingerida em {src['ingested_at']}.",
        }

    today = datetime.now().strftime("%Y-%m-%d")
    filename_kebab = _kebab(Path(src["filename"]).stem)
    source_page_path = f"fontes/{filename_kebab}.md"

    report = {
        "source_page": source_page_path,
        "pages_updated": [],
        "pages_created": [],
        "errors": [],
    }

    # Determina quais páginas de entidades vão ser criadas/atualizadas
    target_entities = []
    for ent in analysis.get("entities_mentioned", []):
        name = ent.get("name", "").strip()
        category = ent.get("category", "").strip()
        if not name or category not in ("topicos", "entidades", "conceitos"):
            continue
        slug = _kebab(name)
        page_path = f"{category}/{slug}.md"
        target_entities.append({
            "name": name,
            "category": category,
            "page_path": page_path,
            "is_new": ent.get("is_new", True),
        })

    # 1. Cria a página da fonte
    try:
        source_page_content = _generate_source_page(
            src=src,
            analysis=analysis,
            target_entities=target_entities,
            today=today,
            filename_kebab=filename_kebab,
        )
        emb = llm.embed_text(source_page_content[:2000])  # primeiros 2000 chars para embedding
        storage.save_page(source_page_path, source_page_content, embedding=emb)
        report["pages_created"].append(source_page_path)
    except Exception as e:
        report["errors"].append(f"Erro criando página de fonte: {e}")

    # 2. Cria/atualiza páginas de entidades
    for entity in target_entities:
        try:
            existing = storage.get_page(entity["page_path"])
            page_content = _generate_entity_page(
                entity=entity,
                analysis=analysis,
                source_filename=filename_kebab,
                today=today,
                existing_content=existing["content"] if existing else "",
            )
            emb = llm.embed_text(page_content[:2000])
            storage.save_page(entity["page_path"], page_content, embedding=emb)
            if existing:
                report["pages_updated"].append(entity["page_path"])
            else:
                report["pages_created"].append(entity["page_path"])
        except Exception as e:
            report["errors"].append(f"Erro processando {entity['page_path']}: {e}")

    # 3. Marca a fonte como ingerida
    storage.mark_source_ingested(source_id, source_page_path)
    storage.log_event(
        operation="ingest",
        summary=f"Ingestão de {src['filename']}",
        details=report,
    )

    return report


def _generate_source_page(src: dict, analysis: dict, target_entities: list,
                          today: str, filename_kebab: str) -> str:
    """Chamada LLM para gerar a página em fontes/."""
    updated_pages_str = "\n".join(f"- [[{e['page_path']}]]" for e in target_entities) or "(nenhuma)"
    key_points_str = "\n".join(f"- {p}" for p in analysis.get("key_points", []))

    prompt = _load_prompt("create_source_page").format(
        filename=src["filename"],
        source_type=analysis.get("source_type", "outro"),
        source_bias=analysis.get("source_bias", "medio"),
        summary=analysis.get("summary", ""),
        key_points=key_points_str,
        updated_pages=updated_pages_str,
        today=today,
        filename_kebab=filename_kebab,
        filename_no_ext=src["filename"].rsplit(".", 1)[0],
    )
    content = llm.chat([{"role": "user", "content": prompt}])
    return _strip_code_fences(content)


def _generate_entity_page(entity: dict, analysis: dict, source_filename: str,
                          today: str, existing_content: str) -> str:
    """Chamada LLM para criar/atualizar página de uma entidade."""
    relevant_points = "\n".join(f"- {p}" for p in analysis.get("key_points", []))
    summary = analysis.get("summary", "")

    category_singular = {
        "topicos": "topico",
        "entidades": "entidade",
        "conceitos": "conceito",
    }.get(entity["category"], "outro")

    prompt = _load_prompt("create_or_update_page").format(
        schema=get_schema(),
        entity_name=entity["name"],
        entity_name_title=entity["name"],
        category=entity["category"],
        category_singular=category_singular,
        source_summary=summary,
        relevant_points=relevant_points,
        existing_content=existing_content or "(página nova — não existe ainda)",
        today=today,
        source_filename=source_filename,
    )
    content = llm.chat([{"role": "user", "content": prompt}])
    return _strip_code_fences(content)


def _strip_code_fences(text: str) -> str:
    """Remove ```markdown ... ``` se o LLM ignorou a instrução de não usar fences."""
    text = text.strip()
    if text.startswith("```"):
        # Remove primeira e última linha
        lines = text.splitlines()
        if lines[0].startswith("```") and lines[-1].startswith("```"):
            text = "\n".join(lines[1:-1])
    return text.strip()


# ---------- QUERY ----------

def find_relevant_pages(question: str, top_k: int = 5) -> list[dict]:
    """Busca semântica + textual nas páginas. Retorna páginas mais relevantes."""
    page_embs = storage.get_page_embeddings()
    if not page_embs:
        # Fallback: busca textual
        keywords = " ".join(question.lower().split()[:3])
        return storage.search_pages_text(keywords, limit=top_k)

    q_emb = llm.embed_text(question)
    scored = [(path, title, llm.cosine_similarity(q_emb, emb))
              for path, title, emb in page_embs]
    scored.sort(key=lambda x: x[2], reverse=True)
    top = scored[:top_k]

    results = []
    for path, title, score in top:
        page = storage.get_page(path)
        if page:
            page["relevance_score"] = score
            results.append(page)
    return results


def answer_query_stream(question: str, chat_history: Optional[list] = None) -> Iterator[str]:
    """Responde uma pergunta usando streaming. Yields chunks de texto."""
    relevant = find_relevant_pages(question, top_k=5)

    if not relevant:
        yield "A wiki ainda não tem páginas relevantes para responder essa pergunta. Que tal ingerir algumas fontes primeiro?"
        return

    # Monta contexto com páginas relevantes (truncadas se necessário)
    pages_context_parts = []
    for p in relevant:
        content_truncated = _truncate_for_context(p["content"], max_chars=2000)
        pages_context_parts.append(f"### [[{p['path']}]]\n{content_truncated}")
    pages_context = "\n\n---\n\n".join(pages_context_parts)

    # Histórico (se houver)
    history_str = ""
    if chat_history:
        last_turns = chat_history[-4:]  # últimos 4 turnos
        history_str = "\n".join(
            f"{t['role']}: {t['content']}" for t in last_turns
        )
    else:
        history_str = "(início da conversa)"

    prompt = _load_prompt("query_answer").format(
        schema=get_schema(),
        relevant_pages=pages_context,
        chat_history=history_str,
        question=question,
    )

    storage.log_event("query", f"Query: {question[:80]}", {"relevant_pages": [p["path"] for p in relevant]})

    yield from llm.chat_stream([{"role": "user", "content": prompt}])


def save_synthesis(title: str, content: str) -> str:
    """Salva uma síntese gerada via chat como página em sinteses/."""
    slug = _kebab(title)
    path = f"sinteses/{slug}.md"
    today = datetime.now().strftime("%Y-%m-%d")

    # Adiciona frontmatter se não tiver
    if not content.startswith("---"):
        content = f"---\ntipo: sintese\ndata_atualizacao: {today}\n---\n\n# {title}\n\n{content}"

    emb = llm.embed_text(content[:2000])
    storage.save_page(path, content, embedding=emb)
    storage.log_event("edit", f"Síntese salva: {title}", {"path": path})
    return path


# ---------- LINT ----------

def run_lint() -> dict:
    """Executa health-check da wiki. Combina dados pré-calculados + análise LLM."""
    pages = storage.list_pages()
    orphans = storage.list_orphan_pages()
    broken = storage.list_broken_links()

    # Páginas estagnadas
    stale_threshold = datetime.now() - timedelta(days=30)
    stale = [
        p["path"] for p in pages
        if datetime.fromisoformat(p["updated_at"]) < stale_threshold
    ]

    # Pré-calcula listas para o prompt
    pages_metadata = "\n".join(f"- {p['path']} (atualizado {p['updated_at'][:10]})" for p in pages[:50])
    orphan_str = "\n".join(f"- {p}" for p in orphans[:20]) or "(nenhuma)"
    broken_str = "\n".join(f"- {f} → {t}" for f, t in broken[:20]) or "(nenhum)"
    stale_str = "\n".join(f"- {p}" for p in stale[:20]) or "(nenhuma)"

    prompt = _load_prompt("lint").format(
        pages_metadata=pages_metadata,
        orphan_pages=orphan_str,
        broken_links=broken_str,
        stale_pages=stale_str,
    )

    schema_hint = '{"summary": "...", "issues": [...], "next_steps": [...]}'
    try:
        report = llm.chat_json(
            messages=[{"role": "user", "content": prompt}],
            schema_hint=schema_hint,
        )
    except Exception as e:
        # Fallback: relatório só com dados pré-calculados se LLM falhar
        report = {
            "summary": f"Análise automática parcial (LLM falhou: {e}).",
            "issues": [],
            "next_steps": [],
        }

    # Adiciona issues programáticos garantidos
    if orphans:
        report.setdefault("issues", []).append({
            "severity": "media",
            "type": "orfa",
            "description": f"{len(orphans)} página(s) órfã(s) — sem links de entrada.",
            "affected_pages": orphans,
            "suggested_action": "Adicionar referências a partir de páginas relacionadas.",
        })
    if broken:
        report.setdefault("issues", []).append({
            "severity": "alta",
            "type": "link-quebrado",
            "description": f"{len(broken)} link(s) quebrado(s).",
            "affected_pages": [f"{f} → {t}" for f, t in broken[:10]],
            "suggested_action": "Criar as páginas faltantes ou remover os links.",
        })

    storage.log_event("lint", "Health check executado", {"issue_count": len(report.get("issues", []))})
    return report
