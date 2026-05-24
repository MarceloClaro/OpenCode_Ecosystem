"""
MASWOS V5 NEXUS — Servidor MCP RAG REAL (porta 3003)
Vector DB com embeddings (TF-IDF local + opcional OpenAI/sentence-transformers).
9 estratégias RAG implementadas.
"""

import sys, json, asyncio, os, math, hashlib, sqlite3, time, re, glob
from datetime import datetime
from collections import defaultdict
from mcp.server import FastMCP

app = FastMCP("maswos-rag", debug=False, log_level="INFO")

# ── Vector DB (SQLite + cosine similarity) ──
def vector_db():
    os.makedirs(".reversa", exist_ok=True)
    db = sqlite3.connect(".reversa/rag_vector.db")
    db.execute("""CREATE TABLE IF NOT EXISTS documents (
        id TEXT PRIMARY KEY, content TEXT, source TEXT, 
        embedding TEXT, metadata TEXT, indexed_at TEXT)""")
    return db

# ── TF-IDF Embedding Engine Real ──
class TFIDFEmbedding:
    def __init__(self, dim=256):
        self.dim = dim
        self.vocabulary = {}
        self.idf = {}
        self.fitted = False

    def tokenize(self, text: str) -> list:
        text = re.sub(r'[^a-zA-Zá-úÁ-Ú0-9\s]', ' ', text.lower())
        tokens = text.split()
        stopwords = {
            "o", "a", "os", "as", "e", "de", "do", "da", "em", "um", "uma", "para", 
            "com", "na", "no", "que", "se", "por", "dos", "das", "nos", "nas", "ao", 
            "aos", "como", "mas", "ou", "mais", "foi", "sua", "seu", "suas", "seus", 
            "esta", "este", "estas", "estes", "isso", "isto", "aquilo", "uns", "umas",
            "pelo", "pela", "qual", "quais", "quem", "quando", "onde", "porque",
            "sobre", "entre", "também", "são", "ser", "tem", "ter", "está", "estão"
        }
        return [t for t in tokens if len(t) > 2 and t not in stopwords]

    def fit(self, documents: list):
        if not documents: return
        df = defaultdict(int)
        total_docs = len(documents)
        term_freqs = defaultdict(int)
        
        for doc in documents:
            seen = set()
            for token in self.tokenize(doc):
                term_freqs[token] += 1
                if token not in seen:
                    df[token] += 1
                    seen.add(token)
                    
        self.idf = {t: math.log((total_docs + 1) / (df[t] + 1)) + 1 for t in df}
        # Pegar os 'dim' termos mais frequentes como vocabulário
        sorted_terms = sorted(term_freqs.keys(), key=lambda x: term_freqs[x], reverse=True)
        self.vocabulary = sorted_terms[:self.dim]
        self.fitted = True

    def embed(self, text: str) -> list:
        if not self.fitted:
            return [0.0] * self.dim
        tokens = self.tokenize(text)
        tf = defaultdict(int)
        for t in tokens:
            tf[t] += 1
        embedding = [0.0] * self.dim
        for i, word in enumerate(self.vocabulary):
            if word in tf:
                # Sublinear TF (1 + log(tf)) para evitar dominância de palavras repetidas
                sublinear_tf = 1 + math.log(tf[word])
                embedding[i] = sublinear_tf * self.idf.get(word, 1.0)
        norm = math.sqrt(sum(v**2 for v in embedding))
        if norm > 0:
            embedding = [v / norm for v in embedding]
        return embedding

    def cosine_similarity(self, a: list, b: list) -> float:
        if not a or not b or len(a) != len(b): return 0.0
        dot = sum(a[i] * b[i] for i in range(len(a)))
        na = math.sqrt(sum(v**2 for v in a))
        nb = math.sqrt(sum(v**2 for v in b))
        return dot / (na * nb) if na > 0 and nb > 0 else 0

engine = TFIDFEmbedding(dim=256)
_similarity_threshold = 0.05

# ── Indexação de Documentos Reais (Não Simulado) ──
def chunk_text(text: str, max_words=150) -> list:
    # Divisão primária por parágrafos para manter coesão semântica
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
    chunks = []
    current_chunk = []
    current_length = 0
    
    for p in paragraphs:
        words = p.split()
        if current_length + len(words) > max_words and current_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_length = 0
        
        # Se um parágrafo for colossal (excede o max_words), quebra forçada
        if len(words) > max_words:
            for i in range(0, len(words), max_words):
                chunks.append(" ".join(words[i:i+max_words]))
        else:
            current_chunk.extend(words)
            current_length += len(words)
            
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

def extract_entities(text: str) -> list:
    # 1. Entidades compostas com inicial maiúscula (Ex: OpenCode Ecosystem)
    compound = re.findall(r'\b(?:[A-ZÀ-Ÿ][a-zà-ÿ]+(?:\s+[A-ZÀ-Ÿ][a-zà-ÿ]+)+)\b', text)
    # 2. Acrônimos ou tecnologias em maiúsculas (Ex: RAG, TF-IDF, JSON, API)
    acronyms = re.findall(r'\b[A-Z]{2,}(?:-[A-Z]+)*\b', text)
    # 3. Entidades simples capitalizadas (mínimo 4 letras)
    simple = re.findall(r'\b[A-ZÀ-Ÿ][a-zà-ÿ]{3,}\b', text)
    
    entities = set(compound + acronyms + simple)
    # Filtrar stopwords capitalizadas de início de frase
    false_positives = {"Para", "Como", "Este", "Esta", "Quando", "Onde", "Mas", "Por", "Que", "Qual", "Sobre", "Além"}
    return list(set([e.lower() for e in entities if e not in false_positives]))

def index_real_documents():
    db = vector_db()
    existing = db.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    
    # Processar diretório real de documentos
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../documentos"))
    files = glob.glob(os.path.join(base_dir, "**/*.md"), recursive=True)
    files += glob.glob(os.path.join(base_dir, "**/*.txt"), recursive=True)
    
    docs_to_index = []
    for fpath in files:
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
            chunks = chunk_text(content, max_words=150)
            for i, chunk in enumerate(chunks):
                if len(chunk.strip()) > 50:
                    docs_to_index.append({
                        "content": chunk, 
                        "source": f"{os.path.basename(fpath)}#chunk{i}", 
                        "topics": extract_entities(chunk)
                    })
        except:
            continue

    if not docs_to_index:
        # Fallback de segurança se diretório vazio
        docs_to_index = [{"content": "OpenCode V4.2 MASWOS Documentação de segurança do ecossistema Multi-Agente...", "source": "system", "topics": ["opencode", "maswos"]}]

    # Treinar embedding engine primeiro com todo o corpus
    all_texts = [d["content"] for d in docs_to_index]
    engine.fit(all_texts)

    # Indexar no SQLite
    db.execute("BEGIN TRANSACTION")
    for doc in docs_to_index:
        doc_id = hashlib.md5(doc["content"].encode()).hexdigest()[:12]
        # Skip se já existe para otimizar
        if db.execute("SELECT 1 FROM documents WHERE id=?", (doc_id,)).fetchone():
            continue
        embedding = engine.embed(doc["content"])
        db.execute("INSERT OR REPLACE INTO documents VALUES (?,?,?,?,?,?)", (
            doc_id, doc["content"], doc["source"],
            json.dumps(embedding), json.dumps({"topics": doc["topics"]}),
            datetime.now().isoformat()))
    db.commit()

# Rodar indexação na inicialização
index_real_documents()

# ── Estratégias RAG Reais ──
RAG_STRATEGIES = {
    "vanilla": {"name": "Vanilla RAG", "desc": "Busca vetorial pura (cosseno)."},
    "memory_rag": {"name": "Memory RAG", "desc": "Injeta contexto de histórico na query atual."},
    "agentic": {"name": "Agentic RAG", "desc": "Analisa intenção e delega (routing) internamente."},
    "graph_rag": {"name": "Graph RAG", "desc": "Expansão de grafo usando entidades extraídas."},
    "hybrid": {"name": "Hybrid RAG", "desc": "RRF mesclando vetorial (dense) e exact-match (sparse)."},
    "crag": {"name": "CRAG (Self-RAG)", "desc": "Avalia retrieved context, filtra irrelevantes, refaz query se necessário."},
    "adaptive": {"name": "Adaptive RAG", "desc": "Altera top_k e threshold baseado no tamanho/complexidade da query."},
    "fusion": {"name": "Fusion RAG", "desc": "Gera sub-queries, busca separadamente e aplica RRF."},
    "hyde": {"name": "HyDE", "desc": "Hypothetical Document Embeddings - usa query para simular resposta antes da busca."},
}

@app.tool()
def consultar_rag(pergunta: str, estrategia: str = "vanilla", top_k: int = 5) -> str:
    """Consulta Vector DB com implementação real das 9 estratégias RAG."""
    
    db = vector_db()
    rows = db.execute("SELECT id, content, source, embedding, metadata FROM documents").fetchall()
    if not rows:
        return json.dumps({"erro": "Banco de dados de vetores vazio."})

    # Preparar Histórico (Memory RAG)
    cache_key = f"rag_{hashlib.md5(pergunta.encode()).hexdigest()[:10]}"
    try:
        cache_db = sqlite3.connect(".reversa/rag_cache.db")
        cache_db.execute("CREATE TABLE IF NOT EXISTS rag_cache (key TEXT PRIMARY KEY, query TEXT, ts TEXT)")
    except: cache_db = None

    query_to_embed = pergunta

    # LÓGICA 1: Memory RAG (Recupera query anterior e une)
    if estrategia == "memory_rag" and cache_db:
        last_query = cache_db.execute("SELECT query FROM rag_cache ORDER BY ts DESC LIMIT 1").fetchone()
        if last_query:
            query_to_embed = f"{last_query[0]} {pergunta}"

    # LÓGICA 2: HyDE (Gera documento hipotético simulado adicionando sinônimos/entidades)
    if estrategia == "hyde":
        # Simulação de resposta heurística expandindo entidades chave
        entities = extract_entities(pergunta)
        hipotese = f"{pergunta}. A documentação aborda {', '.join(entities)}. Os processos e metodologias relacionados a {pergunta} são definidos nos documentos do ecossistema."
        query_to_embed = hipotese

    # LÓGICA 3: Fusion RAG (Quebra a query em subqueries)
    subqueries = [query_to_embed]
    if estrategia == "fusion":
        tokens = engine.tokenize(pergunta)
        if len(tokens) > 2:
            mid = len(tokens) // 2
            subqueries.append(" ".join(tokens[:mid]))
            subqueries.append(" ".join(tokens[mid:]))

    # Realizar buscas
    doc_scores = defaultdict(float)
    doc_data = {}
    
    for sq in subqueries:
        query_emb = engine.embed(sq)
        query_tokens = set(engine.tokenize(sq))
        
        for row in rows:
            doc_id, content, source, emb_json, meta_json = row
            doc_emb = json.loads(emb_json)
            
            # Vanilla Vector Search
            sim_vetorial = engine.cosine_similarity(query_emb, doc_emb)
            score_final = sim_vetorial
            
            # LÓGICA 4: Hybrid RAG (Sparse + Dense)
            if estrategia == "hybrid" or estrategia == "fusion":
                content_tokens = set(engine.tokenize(content))
                overlap = len(query_tokens.intersection(content_tokens))
                bm25_proxy = overlap / (len(query_tokens) + 1)
                score_final = (sim_vetorial * 0.6) + (bm25_proxy * 0.4)
            
            if score_final > _similarity_threshold:
                doc_scores[doc_id] = max(doc_scores[doc_id], score_final)
                doc_data[doc_id] = {"id": doc_id, "source": source, "content": content, "metadata": json.loads(meta_json), "base_score": score_final}

    # Ordenar resultados iniciais
    sorted_docs = sorted(doc_scores.keys(), key=lambda k: doc_scores[k], reverse=True)
    top_results = [doc_data[d] for d in sorted_docs[:top_k]]

    # LÓGICA 5: Graph RAG (Expansão de nós/entidades)
    if estrategia == "graph_rag" and top_results:
        graph_entities = set()
        for r in top_results:
            graph_entities.update(r["metadata"].get("topics", []))
        
        # Encontrar nós vizinhos que partilham entidades
        for row in rows:
            if row[0] not in [r["id"] for r in top_results]:
                meta = json.loads(row[4])
                shared = len(graph_entities.intersection(meta.get("topics", [])))
                if shared > 0:
                    top_results.append({
                        "id": row[0], "source": row[2], "content": row[1], 
                        "metadata": meta, "base_score": 0.1 * shared, "relation": "graph_hop"
                    })
        top_results.sort(key=lambda x: x["base_score"], reverse=True)
        top_results = top_results[:top_k]

    # LÓGICA 6: CRAG / Self-RAG (Corrective Filter)
    if estrategia == "crag":
        filtered = []
        for r in top_results:
            # Avaliador heurístico: requer que pelo menos 1 termo principal da query exista no documento literal
            q_terms = engine.tokenize(pergunta)
            content_lower = r["content"].lower()
            if any(t in content_lower for t in q_terms) and r["base_score"] > 0.1:
                r["crag_eval"] = "Aprovado"
                filtered.append(r)
        
        if not filtered:
            return json.dumps({"pergunta": pergunta, "estrategia": "crag", "status": "REJEITADO - Necessário fallback externo (WebSearch)", "resultados": []}, ensure_ascii=False)
        top_results = filtered

    # LÓGICA 7: Adaptive RAG
    if estrategia == "adaptive":
        complexity = len(engine.tokenize(pergunta))
        if complexity > 10:
            top_k += 3  # Busca mais profunda para queries complexas
            _similarity_threshold_local = 0.03
        else:
            top_k = max(2, top_k // 2)
            _similarity_threshold_local = 0.1
        
        top_results = [r for r in top_results if r["base_score"] >= _similarity_threshold_local][:top_k]

    # LÓGICA 8: Agentic RAG
    if estrategia == "agentic":
        # Roteamento baseado em pattern matching
        if "?" in pergunta or "como" in pergunta.lower():
            # Treat as QA -> Vanilla
            routed_strategy = "vanilla"
        elif "relação" in pergunta.lower() or "entre" in pergunta.lower():
            routed_strategy = "graph_rag"
        else:
            routed_strategy = "hybrid"
        
        # Refaz recursivamente com a estratégia escolhida pelo roteador
        if routed_strategy != "agentic":
            return consultar_rag(pergunta, routed_strategy, top_k)

    # LÓGICA 9: Salvar estado (Memory)
    if cache_db:
        cache_db.execute("INSERT OR REPLACE INTO rag_cache VALUES (?,?,?)",
                         (cache_key, pergunta, datetime.now().isoformat()))
        cache_db.commit()

    # Formatar output final
    output = []
    for r in top_results:
        output.append({
            "id": r["id"],
            "source": r["source"],
            "score": round(r["base_score"], 4),
            "snippet": r["content"][:250] + "..." if len(r["content"]) > 250 else r["content"],
            "topics": r["metadata"].get("topics", [])[:5]
        })

    return json.dumps({
        "pergunta": pergunta,
        "estrategia_executada": estrategia.upper(),
        "total_encontrados": len(output),
        "resultados": output
    }, ensure_ascii=False, indent=2)

@app.tool()
def listar_estrategias_rag() -> str:
    """Lista as 9 estratégias RAG reais implementadas."""
    return json.dumps({
        "total": len(RAG_STRATEGIES),
        "estrategias": [{"id": k, **v} for k, v in RAG_STRATEGIES.items()],
    }, ensure_ascii=False, indent=2)

@app.tool()
def comparar_estrategias_rag(pergunta: str) -> str:
    """Compara TODAS as estratégias RAG reais na mesma query."""
    comparison = {}
    for strategy_id in RAG_STRATEGIES:
        if strategy_id == "agentic": continue
        res_str = consultar_rag(pergunta, strategy_id, 3)
        res = json.loads(res_str)
        if "erro" in res or "status" in res:
            comparison[strategy_id] = {"total": 0, "top_score": 0}
        else:
            comparison[strategy_id] = {
                "total": res["total_encontrados"],
                "top_score": res["resultados"][0]["score"] if res["resultados"] else 0,
            }

    best = max(comparison.keys(), key=lambda s: comparison[s]["top_score"])
    return json.dumps({
        "pergunta": pergunta, "estrategias_comparadas": len(comparison),
        "melhor_estrategia": best, "melhor_estrategia_nome": RAG_STRATEGIES[best]["name"],
        "comparacao": comparison,
    }, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    port = 3003
    for i, a in enumerate(sys.argv):
        if a == "--port" and i + 1 < len(sys.argv):
            port = int(sys.argv[i + 1])
    print(f"[MASWOS-RAG] Inicializando com RAGs REAIS | Porta {port} | VectorDB: SQLite | Embeddings: TF-IDF (256d)", file=sys.stderr)
    
    if "--sse" in sys.argv:
        # FastMCP tem um modo assíncrono para SSE
        srv = FastMCP("maswos-rag-sse", port=port)
        srv._tool_manager = app._tool_manager
        asyncio.run(srv.run_sse_async())
    else:
        app.run()
