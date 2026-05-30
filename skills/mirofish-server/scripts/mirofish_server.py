"""
P23-P26: MiroFish Local Server — Backend API + Deep Interaction + Frontend
Supera MiroFish original: local, zero dependências externas, BRAZIL_TZ, WebSocket-like SSE.

Arquitetura:
  Browser (HTML/CSS/JS) ←→ HTTP/SSE ←→ Python Server ←→ SimulationEngine ←→ SQLite

Iniciar:
  python mirofish_server.py              # Inicia em http://localhost:8765
  python mirofish_server.py --port 9000  # Porta customizada
"""
import sys, os, json, math, time, threading, http.server, urllib.parse, queue, random
import logging, atexit, signal, builtins
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import asdict

# ═══════════════════════════════════════════════════════════════════
# Logging Estruturado & Redirecionamento Global de Prints
# ═══════════════════════════════════════════════════════════════════
_REVERSA_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".reversa"))
os.makedirs(_REVERSA_DIR, exist_ok=True)
_LOG_FILE = os.path.join(_REVERSA_DIR, "mirofish_server.log")

logger = logging.getLogger("MiroFishServer")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(threadName)s] %(message)s')

if not logger.handlers:
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = TimedRotatingFileHandler(_LOG_FILE, when="D", interval=1, backupCount=7, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

# Redirecionar prints globais para o log estruturado
_original_print = print
def logger_print(*args, **kwargs):
    msg = " ".join(str(arg) for arg in args)
    logger.info(msg)
builtins.print = logger_print

# sim_engine é importado dinamicamente (caminho resolvido em runtime via sys.path)
# Pyrefly/LSP não consegue resolver — falso positivo, ignorar.
_SIM_ENGINE_DIR = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', '..', 'simulation-runner', 'scripts'))
if os.path.isdir(_SIM_ENGINE_DIR):
    sys.path.insert(0, _SIM_ENGINE_DIR)

# Data collector path (para relatório Qualis A1)
_DATA_DIR = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data-collector', 'scripts'))
if os.path.isdir(_DATA_DIR):
    sys.path.insert(0, _DATA_DIR)
try:
    from sim_engine import SimulationEngine, ActionType, Sentiment, BRAZIL_TIME  # type: ignore[import-not-found]
    HAS_SIM = True
except ImportError:
    HAS_SIM = False
    BRAZIL_TIME = lambda: datetime.now(timezone(timedelta(hours=-3)))
    _SIM_ENGINE_DIR = None  # type: ignore[unused-ignore]

# ═══════════════════════════════════════════════════════════════════
# Global State
# ═══════════════════════════════════════════════════════════════════

class AppState:
    def __init__(self):
        self.engine: Optional[Any] = None
        self.simulation_running = False
        self.simulation_thread: Optional[threading.Thread] = None
        self.sse_clients: List[queue.Queue] = []
        self.chat_history: List[Dict] = []
        self.stats: Dict[str, Any] = {}
        self.last_summary: Dict[str, Any] = {}
        self.last_report_path: str = ""
        self.wa_profiles: Dict[str, Any] = {}
        self.wa_sim_agents: List[Dict] = []

STATE = AppState()

# ═══════════════════════════════════════════════════════════════════
# Tratamento de Desconexão Involuntária & Arquivos WAL Órfãos
# ═══════════════════════════════════════════════════════════════════
def cleanup_databases():
    """Garante a consolidação das tabelas SQLite e fechamento de conexões órfãs em modo WAL."""
    logger.info("🧹 Iniciando consolidação e encerramento limpo das conexões SQLite (WAL checkpoint)...")
    
    db_paths = [
        os.path.join(_REVERSA_DIR, "omen_logs.db"),
        os.path.join(_REVERSA_DIR, "sim_brazil.db"),
        os.path.join(_REVERSA_DIR, "sim_Brazil_MiroFish.db"),
    ]
    if getattr(STATE, 'engine', None) and getattr(STATE.engine, 'db_path', None):
        db_paths.append(STATE.engine.db_path)
        
    import sqlite3
    for path in set(db_paths):
        if os.path.exists(path):
            try:
                conn = sqlite3.connect(path, timeout=5.0)
                conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
                conn.execute("VACUUM;")
                conn.close()
                logger.info(f"✅ Banco consolidado com sucesso: {os.path.basename(path)}")
            except Exception as e:
                logger.error(f"❌ Erro ao consolidar banco {os.path.basename(path)}: {e}")

atexit.register(cleanup_databases)

def signal_handler(signum, frame):
    logger.warning(f"⚠️ Sinal {signum} recebido. Desligando e limpando conexões SQLite...")
    cleanup_databases()
    sys.exit(0)

if threading.current_thread() is threading.main_thread():
    try:
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    except ValueError:
        pass

def save_omen_prediction(prediction_data: dict):
    """Salva previsão Omen no banco de dados SQLite para log vetorial e análise histórica com suporte a metadados Reversa."""
    db_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", ".reversa", "omen_logs.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS omen_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                scenario TEXT,
                category TEXT,
                risk_level TEXT,
                trend_strength REAL,
                recommendation TEXT,
                raw_data TEXT,
                traceability TEXT,
                confidence_score REAL,
                gaps_detected TEXT
            )
        """)
        
        # Migração segura: Adicionar colunas se não existirem
        c = conn.cursor()
        c.execute("PRAGMA table_info(omen_logs)")
        cols = [row[1] for row in c.fetchall()]
        if "traceability" not in cols:
            conn.execute("ALTER TABLE omen_logs ADD COLUMN traceability TEXT;")
        if "confidence_score" not in cols:
            conn.execute("ALTER TABLE omen_logs ADD COLUMN confidence_score REAL DEFAULT 100.0;")
        if "gaps_detected" not in cols:
            conn.execute("ALTER TABLE omen_logs ADD COLUMN gaps_detected TEXT;")

        # Mapeamento de variáveis para obter fontes (Traceability Reversa)
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "simulation-runner", "scripts"))
            from omen_engine import REAL_VARIABLES, ETHNIC_DIMENSIONS  # type: ignore[import-not-found]
            var_metadata = {}
            for dom, v_dict in REAL_VARIABLES.items():
                for k, v in v_dict.items():
                    var_metadata[f"{dom}.{k}"] = v
            for k, v in ETHNIC_DIMENSIONS.items():
                var_metadata[f"ethnic.{k}"] = v
        except Exception:
            var_metadata = {}

        now = datetime.now(timezone(timedelta(hours=-3))).isoformat()
        preds = prediction_data.get("predictions", {})
        for scenario_name, data in preds.items():
            cat = data.get("_category", "geral")
            risk = data.get("_risk_level", "MEDIO")
            trend = data.get("forecast_stats", {}).get("total_change_pct", 0.0)
            rec = data.get("_recommendation", "")
            
            # --- Métricas de Confiança Reversa (arXiv:2605.18684v1) ---
            used_fallback = data.get("_used_fallback", False)
            ft = data.get("forecast_table", [])
            n_inferred = len(ft)
            
            # Supondo 20 pontos históricos padrão
            n_hist = 20
            
            if used_fallback:
                confirmed = 0
                gaps = n_hist
                inferred = n_inferred
                gap_list = [f"Dado histórico ausente para o cenário {scenario_name}. Usando fallback sintético calibrado."]
            else:
                confirmed = n_hist
                gaps = 0
                inferred = n_inferred
                gap_list = []
                
            total_claims = confirmed + inferred + gaps
            conf_score = round(((confirmed + 0.5 * inferred) / max(total_claims, 1)) * 100, 1)
            
            # --- Rastreabilidade de Variáveis ---
            raw_vars = data.get("variables", [])
            if not raw_vars:
                try:
                    from omen_engine import EXPANDED_SCENARIOS  # type: ignore[import-not-found]
                    raw_vars = EXPANDED_SCENARIOS.get(scenario_name, {}).get("variables", [])
                except:
                    raw_vars = []
                    
            traceability_list = []
            for v_key in raw_vars:
                meta = var_metadata.get(v_key, {})
                traceability_list.append({
                    "variable": v_key,
                    "label": meta.get("label", v_key),
                    "source": meta.get("source", "Simulação Interna")
                })
                
            conn.execute("""
                INSERT INTO omen_logs (timestamp, scenario, category, risk_level, trend_strength, recommendation, raw_data, traceability, confidence_score, gaps_detected)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                now, 
                scenario_name, 
                cat, 
                risk, 
                trend, 
                rec, 
                json.dumps(data, ensure_ascii=False),
                json.dumps(traceability_list, ensure_ascii=False),
                conf_score,
                json.dumps(gap_list, ensure_ascii=False)
            ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[OMEN] Erro ao salvar log vetorial com metadados Reversa: {e}")


# ═══════════════════════════════════════════════════════════════════
# Simulation Controller
# ═══════════════════════════════════════════════════════════════════

def broadcast_sse(event_type: str, data: Dict):
    """Envia evento SSE para todos os clientes conectados."""
    msg = f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
    dead = []
    for q in STATE.sse_clients:
        try:
            q.put_nowait(msg)
        except queue.Full:
            dead.append(q)
    for d in dead:
        if d in STATE.sse_clients:
            STATE.sse_clients.remove(d)

def run_simulation_async(params: Dict):
    """Executa simulação em thread separada."""
    try:
        rounds = int(params.get("rounds", 30))
        agents = int(params.get("agents", 100))
        inject_events = params.get("events", "true").lower() == "true"

        engine = SimulationEngine(name="MiroFish_Local", db_path=".reversa/mirofish_local.db")
        engine._clear_db()

        # Criar perfis base + WhatsApp + todos do banco
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                "..", "..", "simulation-runner", "scripts"))
            from profile_manager import get_profile_manager  # type: ignore[import-not-found]
            from expanded_profiles import ExpandedProfileManager  # type: ignore[import-not-found]
            pm = get_profile_manager()
            # Seed 30 perfis expandidos se não existirem
            if pm.count() < 20:
                epm = ExpandedProfileManager()
                epm.seed_all()
                print(f"   🧠 30 perfis psicológicos/cognitivos semeados")
            all_profiles = pm.to_sim_profiles()
            print(f"   📋 {len(all_profiles)} perfis carregados do banco: {pm.get_summary()}")
        except Exception as e:
            print(f"   ⚠ ProfileManager offline: {e}")
            all_profiles = []

        if all_profiles:
            engine.create_agents_from_profiles(all_profiles)
        else:
            # Fallback: perfis padrão
            profiles = [
                {"name": "Ministro da Fazenda", "labels": ["Official"],
                 "activity_config": {"activity_level": 0.3, "influence_weight": 3.0, "stance": "supportive", "sentiment_bias": 0.2, "posts_per_hour": 0.3}},
                {"name": "Presidente do BC", "labels": ["Official"],
                 "activity_config": {"activity_level": 0.2, "influence_weight": 2.8, "stance": "neutral", "posts_per_hour": 0.2}},
                {"name": "CEO Startup IA", "labels": ["Person"],
                 "activity_config": {"activity_level": 0.7, "influence_weight": 2.0, "stance": "supportive", "sentiment_bias": 0.5, "posts_per_hour": 1.5}},
                {"name": "Sindicalista", "labels": ["Person"],
                 "activity_config": {"activity_level": 0.8, "influence_weight": 1.5, "stance": "critical", "sentiment_bias": -0.3, "posts_per_hour": 2.0}},
                {"name": "Pesquisador Unicamp", "labels": ["Professor"],
                 "activity_config": {"activity_level": 0.5, "influence_weight": 2.2, "stance": "curious", "sentiment_bias": 0.1, "posts_per_hour": 0.8}},
                {"name": "Jornalista Econômico", "labels": ["MediaOutlet"],
                 "activity_config": {"activity_level": 0.8, "influence_weight": 2.5, "stance": "neutral", "sentiment_bias": 0, "posts_per_hour": 3.0}},
            ]
            engine.create_agents_from_profiles(profiles)
            engine.create_agents_batch(max(0, agents - len(profiles)))

        # Eventos
        if inject_events:
            engine.inject_event("Nova regulamentação de IA aprovada", "Marco regulatório exige transparência", 0.8, 10, 3)
            engine.inject_event("Bolha IAs: NVIDIA perde 30%", "Investidores questionam valuations de IA", 0.9, 25, 5)
            engine.inject_event("Brasil anuncia R$ 50 bi em P&D", "Investimento recorde em inovação", 0.7, 40, 4)

        STATE.engine = engine
        STATE.simulation_running = True

        def round_callback(r, data):
            broadcast_sse("round_update", {
                "round": r, "actions": data["actions"],
                "active": data["active"], "sentiment": data["sentiment"],
                "total_agents": data["total_agents"],
            })

        stats = engine.run_simulation(rounds=rounds, agents=agents, callback=round_callback)
        STATE.stats = stats
        STATE.last_summary = stats
        STATE.simulation_running = False

        broadcast_sse("simulation_complete", stats)

    except Exception as e:
        STATE.simulation_running = False
        broadcast_sse("simulation_error", {"error": str(e)})

# ═══════════════════════════════════════════════════════════════════
# Deep Interaction (Chat with Agents)
# ═══════════════════════════════════════════════════════════════════

def chat_with_agent(agent_id: str, message: str) -> Dict:
    """Simula conversa com um agente pós-simulação."""
    if not STATE.engine or agent_id not in STATE.engine.agents:
        return {"error": f"Agente {agent_id} não encontrado"}

    agent = STATE.engine.agents[agent_id]

    # Construir resposta contextual baseada no perfil do agente
    activity_cfg = agent.profile.get("activity_config", {})
    stance = activity_cfg.get("stance", "neutral")
    sentiment_bias = activity_cfg.get("sentiment_bias", 0)

    # Template de resposta baseado em perfil
    responses = {
        "supportive": [
            f"Concordo plenamente! Como {agent.name}, vejo que {message[:50]}... é uma excelente iniciativa.",
            f"Excelente ponto. Minha posição como {agent.name} sempre foi favorável a este tipo de abordagem.",
            f"Com certeza. Os dados que acompanho mostram que iniciativas como '{message[:30]}...' geram resultados positivos.",
        ],
        "critical": [
            f"Discordo veementemente. A experiência como {agent.name} me mostra que {message[:40]}... é problemático.",
            f"Precisamos ter cautela. {message[:30]}... pode parecer bom, mas há riscos sérios que não estamos considerando.",
            f"Não posso apoiar isso. Os números não mentem: iniciativas assim historicamente falharam no Brasil.",
        ],
        "neutral": [
            f"Interessante questão. Deixe-me analisar como {agent.name}: {message[:50]}... tem prós e contras.",
            f"Há argumentos dos dois lados. Minha análise técnica sugere que precisamos de mais dados sobre '{message[:30]}...'.",
        ],
        "curious": [
            f"Que pergunta fascinante! Como pesquisador, adoraria explorar mais sobre {message[:50]}...",
            f"Isso levanta questões importantes. Será que {message[:30]}... realmente funciona no contexto brasileiro?",
        ],
    }

    templates = responses.get(stance, responses["neutral"])
    reply = random.choice(templates)

    # Registrar na história
    chat_entry = {
        "agent_id": agent_id,
        "agent_name": agent.name,
        "message": message,
        "reply": reply,
        "timestamp": BRAZIL_TIME().isoformat(),
        "stance": stance,
    }
    STATE.chat_history.append(chat_entry)

    return chat_entry

def get_agent_list() -> List[Dict]:
    """Lista todos os agentes disponíveis para chat."""
    if not STATE.engine:
        return []
    return [
        {
            "id": a.id,
            "name": a.name,
            "stance": a.stance,
            "posts": a.posts_count,
            "interactions": a.interactions_count,
            "emotional_state": round(a.memory.emotional_state, 2),
            "followers": len(a.followers),
            "activity": round(a.activity_level, 2),
        }
        for a in STATE.engine.agents.values()
    ]

# ═══════════════════════════════════════════════════════════════════
# HTTP SERVER
# ═══════════════════════════════════════════════════════════════════

HTML_FRONTEND = r"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>🐟 MiroFish Local — OpenCode Ecosystem v4.2</title>
<style>
:root{--bg:#060618;--panel:#0e0e28;--accent:#818cf8;--accent2:#34d399;--red:#f87171;--yellow:#fbbf24;--text:#e2e8f0;--text2:#94a3b8;--border:#1e293b;--card:#111133}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--text);min-height:100vh}
header{background:linear-gradient(135deg,#0e0e28,#1a1040);border-bottom:2px solid var(--accent);padding:14px 24px;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;z-index:100}
header h1{font-size:1.4rem}
header h1 span{color:var(--accent)}
.status-badge{font-size:.8rem;padding:6px 14px;border-radius:20px;font-weight:600;letter-spacing:.5px}
.status-badge.idle{background:#1e293b;color:#94a3b8}
.status-badge.running{background:#064e3b;color:var(--accent2);animation:pulse 1.5s infinite}
.status-badge.error{background:#450a0a;color:var(--red)}
@keyframes pulse{0%,100%{opacity:1;box-shadow:0 0 12px rgba(52,211,153,.3)}50%{opacity:.7;box-shadow:0 0 4px rgba(52,211,153,.1)}}
.layout{display:grid;grid-template-columns:280px 1fr 320px;gap:1px;height:calc(100vh - 62px);background:var(--border);overflow:hidden}
@media(max-width:1100px){.layout{grid-template-columns:1fr;overflow-y:auto}}
.panel{background:var(--panel);padding:14px;overflow-y:auto}
.panel h2{font-size:.9rem;color:var(--accent);margin-bottom:10px;text-transform:uppercase;letter-spacing:1px;display:flex;align-items:center;gap:6px}
.panel h2::before{content:'';width:4px;height:16px;background:var(--accent);border-radius:2px}
.controls{display:flex;flex-direction:column;gap:8px;margin-bottom:12px}
.controls label{font-size:.75rem;color:var(--text2);text-transform:uppercase;letter-spacing:.5px}
.controls input,.controls select{background:#1a1a3a;border:1px solid var(--border);color:var(--text);padding:8px 10px;border-radius:8px;font-size:.85rem;width:100%;transition:border .2s}
.controls input:focus{outline:none;border-color:var(--accent)}
.btn{width:100%;padding:10px;border-radius:8px;border:none;cursor:pointer;font-weight:700;font-size:.85rem;transition:all .2s;letter-spacing:.5px}
.btn-start{background:linear-gradient(135deg,var(--accent),#6366f1);color:#fff}
.btn-start:hover{transform:translateY(-1px);box-shadow:0 4px 20px rgba(99,102,241,.3)}
.btn-stop{background:rgba(248,113,113,.15);color:var(--red);border:1px solid rgba(248,113,113,.3)}
.btn-stop:hover{background:rgba(248,113,113,.25)}
.btn-inject{background:rgba(251,191,36,.15);color:var(--yellow);border:1px solid rgba(251,191,36,.3)}
.stat-row{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:10px}
.stat-card{background:var(--card);border-radius:8px;padding:10px;text-align:center;border:1px solid var(--border)}
.stat-card .val{font-size:1.4rem;font-weight:800;background:linear-gradient(135deg,var(--accent),#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.stat-card .lbl{font-size:.65rem;color:var(--text2);margin-top:2px;text-transform:uppercase;letter-spacing:.5px}
.canvas-box{background:var(--card);border-radius:10px;border:1px solid var(--border);overflow:hidden;aspect-ratio:1;position:relative}
.canvas-box canvas{width:100%;height:100%}
.chart-box{height:120px;background:var(--card);border-radius:10px;border:1px solid var(--border);margin-bottom:8px;position:relative}
.chart-box canvas{width:100%;height:100%}
.chat-box{display:flex;flex-direction:column;gap:6px;height:calc(100% - 80px);overflow-y:auto;padding-right:4px}
.chat-msg{padding:8px 12px;border-radius:10px;max-width:88%;font-size:.85rem;line-height:1.4;animation:slideIn .2s ease}
.chat-msg.user{background:var(--accent);align-self:flex-end;border-bottom-right-radius:2px}
.chat-msg.agent{align-self:flex-start;background:var(--card);border:1px solid var(--border);border-bottom-left-radius:2px}
.chat-msg .sender{font-size:.7rem;font-weight:700;margin-bottom:3px}
.chat-msg .sender.user{color:rgba(255,255,255,.7)}
.chat-msg .sender.agent{color:var(--accent2)}
@keyframes slideIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.chat-input{display:flex;gap:6px;margin-top:8px}
.chat-input input{flex:1;background:#1a1a3a;border:1px solid var(--border);color:var(--text);padding:8px 12px;border-radius:8px;font-size:.8rem}
.chat-input input:focus{outline:none;border-color:var(--accent2)}
.chat-input button{background:var(--accent2);color:#000;border:none;padding:8px 14px;border-radius:8px;cursor:pointer;font-weight:700;font-size:.8rem}
.agent-mini{display:flex;align-items:center;gap:8px;padding:8px;border-radius:8px;cursor:pointer;transition:background .15s;margin-bottom:4px}
.agent-mini:hover{background:var(--card)}
.agent-mini .dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.agent-mini .info{flex:1;min-width:0}
.agent-mini .info .n{font-size:.8rem;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.agent-mini .info .m{font-size:.68rem;color:var(--text2)}
.agent-mini .sent{font-size:.75rem;font-weight:700}
.topic-bar{margin-bottom:6px}
.topic-bar .lbl{display:flex;justify-content:space-between;font-size:.7rem;margin-bottom:2px}
.topic-bar .bar{height:6px;background:var(--border);border-radius:3px;overflow:hidden}
.topic-bar .bar .fill{height:100%;border-radius:3px;transition:width .5s}
.log-box{font-family:'Cascadia Code',monospace;font-size:.7rem;color:var(--accent2);max-height:150px;overflow-y:auto;white-space:pre-wrap;line-height:1.5}
::-webkit-scrollbar{width:4px}::-webkit-scrollbar-track{background:transparent}::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px}
</style>
</head>
<body>
<header>
  <h1>🐟 <span>MiroFish</span> Local — OpenCode Ecosystem v4.2</h1>
  <div style="display:flex;gap:10px;align-items:center">
    <span style="font-size:.75rem;color:var(--text2)">BRAZIL (UTC-3)</span>
    <span id="statusBadge" class="status-badge idle">● PRONTO</span>
  </div>
</header>

<div class="layout">
  <!-- LEFT PANEL: Controls + Topics + Event Injection -->
  <div class="panel">
    <h2>🎮 Controles</h2>
    <div class="controls">
      <input type="text" id="researchTopic" placeholder="Tema de pesquisa (ex: IA e mercado de trabalho)" style="background:var(--card);border:1px solid var(--border);color:var(--text);padding:6px;border-radius:6px;font-size:.7rem;width:100%;margin-bottom:6px">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
        <div><label>Agentes</label><input type="number" id="agents" value="200" min="10" max="2000"></div>
        <div><label>Rodadas</label><input type="number" id="rounds" value="30" min="5" max="200"></div>
      </div>
      <label style="display:flex;align-items:center;gap:6px;margin-top:4px"><input type="checkbox" id="events" checked style="width:auto"> Auto-injetar eventos</label>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px">
        <button class="btn btn-start" onclick="startSim()">▶ INICIAR</button>
        <button class="btn btn-stop" onclick="stopSim()">⏹ PARAR</button>
      </div>
      <button class="btn" onclick="generateReport()" style="width:100%;margin-top:4px;background:linear-gradient(135deg,rgba(251,191,36,.2),rgba(245,158,11,.1));color:var(--yellow);border:1px solid rgba(251,191,36,.3);padding:8px;border-radius:8px;cursor:pointer;font-weight:700;font-size:.75rem;transition:all .2s">📄 GERAR RELATÓRIO Qualis A1</button>
      <button class="btn" onclick="runOmenPrediction()" style="width:100%;margin-top:4px;background:linear-gradient(135deg,rgba(99,102,241,.2),rgba(139,92,246,.1));color:#a78bfa;border:1px solid rgba(99,102,241,.3);padding:8px;border-radius:8px;cursor:pointer;font-weight:700;font-size:.75rem;transition:all .2s">🔮 PREVER CENÁRIOS (500+ vars)</button>
      <button class="btn" onclick="auditOmen()" style="width:100%;margin-top:4px;background:linear-gradient(135deg,rgba(245,158,11,.15),rgba(217,119,6,.08));color:#f59e0b;border:1px solid rgba(245,158,11,.3);padding:8px;border-radius:8px;cursor:pointer;font-weight:700;font-size:.75rem;transition:all .2s">🔍 AUDITAR PREVISÕES (Previsto vs Ocorrido)</button>
      <button class="btn" onclick="omniResearch()" style="width:100%;margin-top:4px;background:linear-gradient(135deg,rgba(16,185,129,.2),rgba(5,150,105,.1));color:#34d399;border:1px solid rgba(16,185,129,.3);padding:8px;border-radius:8px;cursor:pointer;font-weight:700;font-size:.75rem;transition:all .2s">🔬 PESQUISAR TEMA (MiroFishOmni)</button>
      <button class="btn" onclick="runWarRoom()" style="width:100%;margin-top:4px;background:linear-gradient(135deg,rgba(239,68,68,.15),rgba(220,38,38,.08));color:#f87171;border:1px solid rgba(239,68,68,.3);padding:8px;border-radius:8px;cursor:pointer;font-weight:700;font-size:.75rem;transition:all .2s">⚔️ WAR ROOM (10 agentes)</button>
    </div>

    <h2 style="margin-top:14px">📡 Injetar Evento</h2>
    <div class="controls">
      <select id="evtPreset" onchange="loadEventPreset()" style="background:var(--card);border:1px solid var(--border);color:var(--text);padding:6px;border-radius:6px;font-size:.7rem;width:100%">
        <option value="">-- Preset rápido --</option>
        <option value="crise">📉 Crise econômica</option>
        <option value="tech">🚀 Avanço tecnológico</option>
        <option value="ambiental">🌳 Desastre ambiental</option>
        <option value="politica">🏛 Crise política</option>
        <option value="saude">🏥 Emergência sanitária</option>
        <option value="positivo">✨ Notícia positiva</option>
        <option value="custom">✏️ Personalizado...</option>
      </select>
      <input type="text" id="evtTitle" placeholder="Título do evento" value="Nova crise econômica">
      <input type="text" id="evtDesc" placeholder="Descrição do evento" value="Mercado reage a dados negativos de emprego">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px">
        <div><label style="font-size:.65rem">Impacto: <b id="impactVal" style="color:var(--accent)">0.7</b></label>
        <input type="range" id="evtImpact" min="-1" max="1" step="0.1" value="0.7" oninput="document.getElementById('impactVal').textContent=this.value;this.style.background='linear-gradient(to right,#f87171 0%,#fbbf24 50%,#34d399 100%)'.split(',')[Math.round((parseFloat(this.value)+1)*50/2)]||'#fbbf24'"></div>
        <div><label style="font-size:.65rem">Duração: <b id="durVal">3</b> rod</label>
        <input type="range" id="evtDuration" min="1" max="10" step="1" value="3" oninput="document.getElementById('durVal').textContent=this.value"></div>
      </div>
      <div style="display:flex;gap:4px">
        <button class="btn btn-inject" onclick="injectEvent()" style="flex:1">💉 INJETAR</button>
        <button class="btn" onclick="injectRandomEvent()" style="background:var(--card);border:1px solid var(--border);color:var(--text2);font-size:.65rem;padding:4px 8px;border-radius:6px;cursor:pointer" title="Injeta evento aleatório">🎲</button>
      </div>
      <div id="eventHistory" style="max-height:80px;overflow-y:auto;font-size:.6rem;color:var(--text2);margin-top:6px;border-top:1px solid var(--border);padding-top:4px"></div>
    </div>

    <h2 style="margin-top:14px">📊 Sentimento por Tópico</h2>
    <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;font-size:.6rem;color:var(--text2)">
      <span>🟢 positivo</span><span>🔴 negativo</span><span>🟡 neutro</span>
      <span style="margin-left:auto;cursor:help" title="Clique em um tópico para expandir estatísticas detalhadas, evolução por rodada e engajamento por stance">💡 clique para detalhes</span>
    </div>
    <div id="topicAnalysis" style="overflow-y:auto;max-height:340px">
      <div style="color:var(--text2);font-size:.7rem;text-align:center;padding:10px">Inicie simulação</div>
    </div>
  </div>

  <!-- CENTER: Agent Network + Charts -->
  <div class="panel" style="display:flex;flex-direction:column;gap:10px">
    <h2>🔗 Rede de Agentes</h2>
    <div class="canvas-box" id="networkContainer">
      <canvas id="agentCanvas"></canvas>
      <div style="position:absolute;top:4px;right:4px;display:flex;gap:3px;z-index:10">
        <button onclick="zoomNetwork(.2)" title="Zoom +" style="background:rgba(15,23,42,.8);border:1px solid var(--border);color:var(--text);width:22px;height:22px;border-radius:4px;cursor:pointer;font-size:.7rem;line-height:1">+</button>
        <button onclick="zoomNetwork(-.2)" title="Zoom -" style="background:rgba(15,23,42,.8);border:1px solid var(--border);color:var(--text);width:22px;height:22px;border-radius:4px;cursor:pointer;font-size:.7rem;line-height:1">−</button>
        <button onclick="resetNetworkView()" title="Reset" style="background:rgba(15,23,42,.8);border:1px solid var(--border);color:var(--text);width:22px;height:22px;border-radius:4px;cursor:pointer;font-size:.6rem">⌂</button>
        <button onclick="expandNetwork()" title="Tela cheia" style="background:rgba(15,23,42,.8);border:1px solid var(--accent);color:var(--accent);width:22px;height:22px;border-radius:4px;cursor:pointer;font-size:.7rem">⛶</button>
      </div>
    </div>
    <div id="networkLegend" style="display:flex;gap:8px;justify-content:center;font-size:.6rem;margin-top:4px;flex-wrap:wrap">
      <span style="color:#34d399">🟢 Apoiadores</span>
      <span style="color:#f87171">🔴 Críticos</span>
      <span style="color:#22d3ee">🔵 Curiosos</span>
      <span style="color:#94a3b8">⚪ Neutros</span>
    </div>
    <div id="agentTooltip" style="position:absolute;background:rgba(15,23,42,.95);border:1px solid var(--accent);border-radius:6px;padding:6px 10px;font-size:.65rem;pointer-events:none;display:none;z-index:50;white-space:nowrap;box-shadow:0 4px 12px rgba(0,0,0,.4)"></div>
    <div class="chart-box"><canvas id="sentimentChart"></canvas></div>
    <div style="display:flex;gap:8px;justify-content:center;font-size:.6rem;margin-top:-4px;margin-bottom:4px">
      <span style="color:#6366f1">━ Sentimento</span>
      <span style="color:rgba(99,102,241,.3)">▓ Área</span>
      <span style="color:rgba(148,163,184,.4)">--- Neutro (0)</span>
    </div>
    <div id="chartTooltip" style="position:absolute;background:rgba(15,23,42,.95);border:1px solid var(--accent2);border-radius:6px;padding:4px 8px;font-size:.65rem;pointer-events:none;display:none;z-index:50;white-space:nowrap;box-shadow:0 4px 12px rgba(0,0,0,.4)"></div>
    <div class="chart-box" style="position:relative"><canvas id="activityChart"></canvas></div>
    <div style="display:flex;gap:8px;justify-content:center;font-size:.6rem;margin-top:-4px">
      <span style="color:#34d399">▌ Ações/rodada</span>
      <span style="color:#fbbf24">--- Média móvel</span>
    </div>
  </div>

  <!-- RIGHT PANEL: Stats + Agents + Chat -->
  <div class="panel">
    <h2>📈 Métricas</h2>
    <div class="stat-row">
      <div class="stat-card"><div class="val" id="stRound">-</div><div class="lbl">Rodada</div></div>
      <div class="stat-card"><div class="val" id="stActions">-</div><div class="lbl">Ações</div></div>
      <div class="stat-card"><div class="val" id="stActive">-</div><div class="lbl">Ativos</div></div>
      <div class="stat-card"><div class="val" id="stSent">-</div><div class="lbl">Sentimento</div></div>
      <div class="stat-card"><div class="val" id="stSpeed">-</div><div class="lbl">Ações/s</div></div>
      <div class="stat-card"><div class="val" id="stPolar">-</div><div class="lbl">Polarização</div></div>
    </div>

    <h2 style="margin-top:10px">📱 WhatsApp <span id="waStatus" style="font-size:.6rem;color:var(--text2)">pronto</span></h2>
    <div style="background:var(--card);border:1px solid var(--border);border-radius:8px;padding:8px;margin-bottom:10px">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px;margin-bottom:6px">
        <button class="btn" onclick="window.open('https://web.whatsapp.com','_blank')" style="background:#25D366;color:#000;border:none;padding:7px;border-radius:6px;cursor:pointer;font-weight:700;font-size:.7rem">📱 ABRIR WHATSAPP WEB</button>
        <button class="btn" onclick="document.getElementById('waFileInput').click()" style="background:var(--card);border:1px solid var(--border);color:var(--text);padding:7px;border-radius:6px;cursor:pointer;font-size:.65rem">📂 Enviar chat .txt</button>
      </div>
      <input type="file" id="waFileInput" accept=".txt" style="display:none" onchange="whatsappUploadChat(this)">
      <div id="waQR" style="text-align:center;font-size:.6rem;color:var(--text2);padding:4px">
        1. Abra WhatsApp Web → escaneie QR<br>2. No celular: Exportar chat (sem mídia)<br>3. Envie o arquivo .txt aqui
      </div>
      <div id="waActions" style="display:none;margin-top:6px">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px">
          <button class="btn" onclick="whatsappApplyProfiles()" style="background:rgba(251,191,36,.15);color:var(--yellow);border:1px solid rgba(251,191,36,.3);padding:4px;border-radius:4px;cursor:pointer;font-weight:700;font-size:.6rem">🎯 Aplicar perfis</button>
          <button class="btn" onclick="document.getElementById('waFileInput').click()" style="background:var(--card);border:1px solid var(--border);color:var(--text);padding:4px;border-radius:4px;cursor:pointer;font-size:.6rem">📂 Outro chat</button>
        </div>
        <div id="waProfileInfo" style="margin-top:4px;font-size:.6rem;color:var(--text2)"></div>
        <div id="waChatList" style="max-height:80px;overflow-y:auto;margin-top:4px;font-size:.55rem"></div>
      </div>
    </div>

    <h2 style="margin-top:10px">💬 Chat com Agente</h2>
    <select id="chatAgent" style="background:#1a1a3a;border:1px solid var(--border);color:var(--text);padding:6px;border-radius:8px;width:100%;margin-bottom:8px;font-size:.8rem">
      <option value="">Selecione um agente...</option>
    </select>
    <div class="chat-box" id="chatBox"><div style="color:var(--accent2);font-size:.75rem;text-align:center;padding:20px">🤖 Selecione um agente e digite sua mensagem</div></div>
    <div class="chat-input">
      <input type="text" id="chatInput" placeholder="Pergunte algo ao agente..." onkeypress="if(event.key==='Enter')sendChat()">
      <button onclick="sendChat()">➤</button>
    </div>

    <h2 style="margin-top:10px">🤖 Agentes</h2>
    <div style="max-height:150px;overflow-y:auto" id="agentList"><div style="color:var(--text2);font-size:.75rem;text-align:center;padding:10px">Inicie simulação</div></div>

    <h2 style="margin-top:10px;display:flex;justify-content:space-between;align-items:center">📋 Log <button onclick="history=[];renderLog()" style="background:none;border:none;color:var(--text2);cursor:pointer;font-size:.6rem" title="Limpar">limpar</button></h2>
    <div id="logBox" style="max-height:130px;overflow-y:auto;font-size:.6rem;color:var(--text2);font-family:'Cascadia Code',Consolas,monospace;background:rgba(0,0,0,.2);border-radius:6px;padding:4px 8px"><div style="text-align:center;padding:6px">Pronto</div></div>
  </div>
</div>

<script>
const API=''; const WA_API='http://localhost:8766'; let es=null, history=[], simRunning=false, waConnected=false;
const sentimentData=[], activityData=[], colors=['#818cf8','#34d399','#f87171','#fbbf24','#a78bfa','#fb923c','#22d3ee'];

function log(m){
  history.push(`[${new Date().toLocaleTimeString()}] ${m}`);
  if(history.length>100) history.shift();
  renderLog();
}
function renderLog(){
  const box=document.getElementById('logBox');
  if(!box) return;
  box.innerHTML=history.slice().reverse().map(h=>`<div style="padding:1px 0;border-bottom:1px solid rgba(30,41,59,.2)">${h}</div>`).join('')||'<div style="text-align:center;padding:6px">Pronto</div>';
  box.scrollTop=0;
}
function setStatus(s,m){
  const b=document.getElementById('statusBadge'); b.className='status-badge '+s; b.textContent=m||(s==='running'?'⏳ RODANDO':'● PRONTO');
}

// ── Charts with grid, legends, and value annotations ──
function drawSentimentChart(){
  const c=document.getElementById('sentimentChart'), ctx=c.getContext('2d');
  c.width=c.parentElement.clientWidth; c.height=c.parentElement.clientHeight;
  const w=c.width, h=c.height, pad=30, n=sentimentData.length;
  if(n<2){ ctx.fillStyle='#94a3b8'; ctx.font='11px sans-serif'; ctx.textAlign='center'; ctx.fillText('Aguardando dados...',w/2,h/2); return; }
  ctx.clearRect(0,0,w,h);
  // Grid horizontal
  ctx.strokeStyle='rgba(30,41,59,.6)'; ctx.lineWidth=.5;
  for(let i=1;i<=3;i++){ const y=pad+(h-2*pad)*i/4; ctx.beginPath(); ctx.moveTo(pad,y); ctx.lineTo(w-pad,y); ctx.stroke(); }
  // Eixos
  ctx.strokeStyle='#475569'; ctx.lineWidth=1;
  ctx.beginPath(); ctx.moveTo(pad,pad); ctx.lineTo(pad,h-pad); ctx.lineTo(w-pad,h-pad); ctx.stroke();
  // Labels
  ctx.fillStyle='#64748b'; ctx.font='9px sans-serif'; ctx.textAlign='center';
  ctx.fillText('Rodada',w/2,h-2);
  ctx.save(); ctx.translate(8,h/2); ctx.rotate(-Math.PI/2); ctx.fillText('Sentimento',0,0); ctx.restore();
  // Y-axis ticks
  ctx.textAlign='right';
  for(let v=-1;v<=1;v+=.5){ const y=h-pad-(h-2*pad)*(v+1)/2; ctx.fillText(v.toFixed(1),pad-4,y+3); }
  // X-axis ticks
  ctx.textAlign='center';
  for(let i=0;i<n;i+=Math.max(1,Math.floor(n/6))){ const x=pad+(w-2*pad)*i/Math.max(n-1,1); ctx.fillText(i+1,x,h-pad+12); }
  // Zero line
  const zy=h-pad-(h-2*pad)/2; ctx.strokeStyle='rgba(148,163,184,.3)'; ctx.setLineDash([4,4]); ctx.beginPath(); ctx.moveTo(pad,zy); ctx.lineTo(w-pad,zy); ctx.stroke(); ctx.setLineDash([]);
  // Gradient fill
  const grad=ctx.createLinearGradient(0,pad,0,h-pad);
  grad.addColorStop(0,'rgba(99,102,241,.2)'); grad.addColorStop(.5,'rgba(99,102,241,.05)'); grad.addColorStop(1,'rgba(239,68,68,.1)');
  ctx.beginPath();
  for(let i=0;i<n;i++){ const x=pad+(w-2*pad)*i/Math.max(n-1,1), y=h-pad-(h-2*pad)*(sentimentData[i]+1)/2;
    i===0?ctx.moveTo(x,y):ctx.lineTo(x,y); }
  const lastX=pad+(w-2*pad)*(n-1)/Math.max(n-1,1);
  ctx.lineTo(lastX,h-pad); ctx.lineTo(pad,h-pad); ctx.closePath(); ctx.fillStyle=grad; ctx.fill();
  // Line
  ctx.strokeStyle='#6366f1'; ctx.lineWidth=2.5; ctx.lineJoin='round';
  ctx.beginPath();
  for(let i=0;i<n;i++){ const x=pad+(w-2*pad)*i/Math.max(n-1,1), y=h-pad-(h-2*pad)*(sentimentData[i]+1)/2;
    i===0?ctx.moveTo(x,y):ctx.lineTo(x,y); }
  ctx.stroke();
  // Dots + value on last
  for(let i=0;i<n;i++){ const x=pad+(w-2*pad)*i/Math.max(n-1,1), y=h-pad-(h-2*pad)*(sentimentData[i]+1)/2;
    ctx.beginPath(); ctx.arc(x,y,2.5,0,Math.PI*2); ctx.fillStyle= sentimentData[i]>0?'#34d399':sentimentData[i]<0?'#f87171':'#94a3b8'; ctx.fill(); }
  // Last value annotation
  const lx=pad+(w-2*pad)*(n-1)/Math.max(n-1,1), ly=h-pad-(h-2*pad)*(sentimentData[n-1]+1)/2;
  ctx.fillStyle='#e2e8f0'; ctx.font='bold 10px sans-serif'; ctx.textAlign='left';
  ctx.fillText(sentimentData[n-1].toFixed(2),lx+6,ly+4);

  // Hover interactivity — crosshair + tooltip
  c.onmousemove=function(e){
    const rect=c.getBoundingClientRect(), mx=e.clientX-rect.left, my=e.clientY-rect.top;
    const scaleX=w/rect.width, scaleY=h/rect.height;
    const tip=document.getElementById('chartTooltip');
    const idx=Math.round((mx*scaleX-pad)/(w-2*pad)*Math.max(n-1,1));
    if(idx<0||idx>=n){ tip.style.display='none'; return; }
    const val=sentimentData[idx], col=val>0?'#34d399':val<0?'#f87171':'#94a3b8';
    tip.innerHTML='<b>Rodada '+(idx+1)+'</b>: <span style="color:'+col+'">'+(val>=0?'+':'')+val.toFixed(3)+'</span>';
    tip.style.display='block'; tip.style.left=(e.clientX-w/2<0?e.clientX+12:e.clientX-tip.offsetWidth-12)+'px'; tip.style.top=(e.clientY-50)+'px';
  };
  c.onmouseleave=function(){ document.getElementById('chartTooltip').style.display='none'; };
}
function drawActivityChart(){
  const c=document.getElementById('activityChart'), ctx=c.getContext('2d');
  c.width=c.parentElement.clientWidth; c.height=c.parentElement.clientHeight;
  const w=c.width, h=c.height, pad=30, n=activityData.length;
  if(n<2){ ctx.fillStyle='#94a3b8'; ctx.font='11px sans-serif'; ctx.textAlign='center'; ctx.fillText('Aguardando dados...',w/2,h/2); return; }
  ctx.clearRect(0,0,w,h);
  const maxA=Math.max(...activityData,1);
  // Grid horizontal
  ctx.strokeStyle='rgba(30,41,59,.6)'; ctx.lineWidth=.5;
  for(let i=1;i<=3;i++){ const y=pad+(h-2*pad)*i/4; ctx.beginPath(); ctx.moveTo(pad,y); ctx.lineTo(w-pad,y); ctx.stroke(); }
  // Eixos
  ctx.strokeStyle='#475569'; ctx.lineWidth=1;
  ctx.beginPath(); ctx.moveTo(pad,pad); ctx.lineTo(pad,h-pad); ctx.lineTo(w-pad,h-pad); ctx.stroke();
  ctx.fillStyle='#64748b'; ctx.font='9px sans-serif'; ctx.textAlign='center';
  ctx.fillText('Rodada',w/2,h-2);
  ctx.save(); ctx.translate(8,h/2); ctx.rotate(-Math.PI/2); ctx.fillText('Acoes',0,0); ctx.restore();
  ctx.textAlign='right';
  ctx.fillText(maxA,pad-4,pad+4); ctx.fillText(Math.round(maxA/2),pad-4,h/2+3); ctx.fillText('0',pad-4,h-pad+4);
  ctx.textAlign='center'; for(let i=0;i<n;i+=Math.max(1,Math.floor(n/6))){ ctx.fillText(i+1,pad+(w-2*pad)*i/Math.max(n-1,1),h-pad+12); }
  // Bars
  const barW=Math.max(2,(w-2*pad)/n*.7);
  for(let i=0;i<n;i++){ const x=pad+(w-2*pad)*i/Math.max(n-1,1)-barW/2, bh=(h-2*pad)*activityData[i]/maxA;
    ctx.fillStyle='rgba(52,211,153,.7)'; ctx.fillRect(x,h-pad-bh,barW,bh); }
  // Moving average line
  ctx.strokeStyle='#fbbf24'; ctx.lineWidth=1.5; ctx.setLineDash([3,3]); ctx.beginPath();
  const window=Math.max(3,Math.floor(n/8));
  for(let i=window-1;i<n;i++){
    let avg=0; for(let j=i-window+1;j<=i;j++) avg+=activityData[j]; avg/=window;
    const x=pad+(w-2*pad)*i/Math.max(n-1,1), y=h-pad-(h-2*pad)*avg/maxA;
    i===window-1?ctx.moveTo(x,y):ctx.lineTo(x,y);
  }
  ctx.stroke(); ctx.setLineDash([]);
}
// ── Zoom, Pan e Fullscreen da Rede de Agentes ──
let netZoom=1, netPanX=0, netPanY=0, netDragging=false, netDragStart={x:0,y:0};

function zoomNetwork(delta){
  netZoom=Math.max(.3, Math.min(4, netZoom+delta));
  const ags=window._netAgents||[];
  if(ags.length) drawAgentNetwork(ags);
}
function resetNetworkView(){ netZoom=1; netPanX=0; netPanY=0; const ags=window._netAgents||[]; if(ags.length) drawAgentNetwork(ags); }

function expandNetwork(){
  const modal=document.getElementById('networkModal'), mc=document.getElementById('modalNetworkCanvas');
  modal.classList.add('show');
  // Copy current agents to modal
  const ags=window._netAgents||[];
  if(ags.length){ drawAgentNetworkOnCanvas(mc.getContext('2d'), mc, ags); }
  // Update modal legend
  document.getElementById('modalFullLegend').innerHTML=document.getElementById('networkLegend')?.innerHTML||'';
  // Wheel zoom on modal
  mc.parentElement.addEventListener('wheel', function(e){ e.preventDefault(); netZoom=Math.max(.3,Math.min(4,netZoom+(e.deltaY<0?.15:-.15))); drawAgentNetworkOnCanvas(mc.getContext('2d'),mc,ags); }, {passive: false});
  // Pan on modal
  let mdragging=false, mstart={x:0,y:0};
  mc.parentElement.onmousedown=function(e){ mdragging=true; mstart={x:e.clientX-netPanX,y:e.clientY-netPanY}; mc.parentElement.style.cursor='grabbing'; };
  mc.parentElement.onmousemove=function(e){ if(!mdragging) return; netPanX=e.clientX-mstart.x; netPanY=e.clientY-mstart.y; drawAgentNetworkOnCanvas(mc.getContext('2d'),mc,ags); };
  mc.parentElement.onmouseup=function(){ mdragging=false; mc.parentElement.style.cursor='grab'; };
  mc.parentElement.style.cursor='grab';
  // Keyboard: ESC to close
  document.addEventListener('keydown', function escHandler(e){ if(e.key==='Escape'){ closeNetworkModal(); document.removeEventListener('keydown',escHandler); } });
}
function closeNetworkModal(){
  document.getElementById('networkModal').classList.remove('show');
  netZoom=1; netPanX=0; netPanY=0;
  const ags=window._netAgents||[];
  if(ags.length) drawAgentNetwork(ags);
}

// Render helper: draws network on any canvas with current zoom/pan
function drawAgentNetworkOnCanvas(ctx, canvas, agents){
  const w=canvas.width=canvas.parentElement.clientWidth, h=canvas.height=canvas.parentElement.clientHeight;
  ctx.clearRect(0,0,w,h);
  if(!agents||!agents.length){ ctx.fillStyle='#94a3b8'; ctx.font='12px sans-serif'; ctx.textAlign='center'; ctx.fillText('Inicie simulacao',w/2,h/2); return; }

  const sorted=[...agents].sort((a,b)=>{
    const infA=((a.followers||[]).length||0)*2+(a.posts||0);
    const infB=((b.followers||[]).length||0)*2+(b.posts||0);
    return infB-infA;
  });
  const topIds=new Set(sorted.slice(0,30).map(a=>a.id));
  const display=agents.slice(0,80);
  const positions=[];
  const stanceCounts={supportive:0,critical:0,curious:0,neutral:0};

  for(let i=0;i<display.length;i++){
    const a=display[i], s=a.stance||'neutral';
    stanceCounts[s]=(stanceCounts[s]||0)+1;
    const angle=(i/display.length)*Math.PI*2+(i%5)*0.4;
    const r=Math.min(w,h)*.36, cx=w/2+Math.cos(angle)*r, cy=h/2+Math.sin(angle)*r;
    positions.push({x:cx,y:cy,agent:a});
  }

  ctx.save();
  ctx.translate(w/2+netPanX, h/2+netPanY);
  ctx.scale(netZoom, netZoom);
  ctx.translate(-w/2, -h/2);

  // Connections
  for(let i=0;i<positions.length;i++){
    for(let j=i+1;j<positions.length;j++){
      const sameStance=positions[i].agent.stance===positions[j].agent.stance;
      ctx.strokeStyle=sameStance?'rgba(99,102,241,.08)':'rgba(99,102,241,.02)';
      ctx.lineWidth=sameStance?.5:.2;
      ctx.beginPath(); ctx.moveTo(positions[i].x,positions[i].y); ctx.lineTo(positions[j].x,positions[j].y); ctx.stroke();
    }
  }

  for(const p of positions){
    const s=p.agent.stance||'neutral';
    const col=s==='supportive'?'#34d399':s==='critical'?'#f87171':s==='curious'?'#22d3ee':'#94a3b8';
    const followers=(p.agent.followers||[]).length||0;
    const r=Math.min(4+followers*.12+(p.agent.posts||0)*.02, 14);
    ctx.beginPath(); ctx.arc(p.x,p.y,r+4,0,Math.PI*2); ctx.fillStyle=col+'15'; ctx.fill();
    ctx.beginPath(); ctx.arc(p.x,p.y,r,0,Math.PI*2); ctx.fillStyle=col; ctx.fill();
    ctx.strokeStyle=topIds.has(p.agent.id)?'rgba(255,255,255,.3)':'rgba(255,255,255,.1)';
    ctx.lineWidth=topIds.has(p.agent.id)?1.2:.6; ctx.stroke();
    if(topIds.has(p.agent.id)){
      const name=p.agent.name.length>16?p.agent.name.substring(0,15)+'...':p.agent.name;
      ctx.font='bold 7px sans-serif'; ctx.textAlign='center';
      const lw=ctx.measureText(name).width+6, ly=p.y+r+10;
      ctx.fillStyle='rgba(15,23,42,.85)'; ctx.fillRect(p.x-lw/2,ly-8,lw,11);
      ctx.strokeStyle=col+'60'; ctx.lineWidth=.5; ctx.strokeRect(p.x-lw/2,ly-8,lw,11);
      ctx.fillStyle=col; ctx.fillText(name,p.x,ly+1);
    }
  }
  ctx.restore();

  // Hover tooltip in modal
  canvas.onmousemove=function(e){
    const rect=canvas.getBoundingClientRect(), mx=e.clientX-rect.left, my=e.clientY-rect.top;
    // Transform back through zoom/pan
    const cx=mx-w/2-netPanX, cy=my-h/2-netPanY;
    const tx=cx/netZoom+w/2, ty=cy/netZoom+h/2;
    const tip=document.getElementById('agentTooltip');
    let found=null;
    for(const p of positions){
      if(Math.hypot(tx-p.x, ty-p.y)<18){ found=p; break; }
    }
    if(found){
      const a=found.agent, s=a.stance||'neutral';
      const col=s==='supportive'?'#34d399':s==='critical'?'#f87171':s==='curious'?'#22d3ee':'#94a3b8';
      tip.innerHTML='<b style="color:'+col+'">'+a.name+'</b><br>Stance: <b>'+s+'</b> | Posts: '+(a.posts||0)+'<br>Seguidores: '+((a.followers||[]).length||0)+' | Sent: <span style="color:'+(a.emotional_state>0?'#34d399':'#f87171')+'">'+(a.emotional_state||0).toFixed(2)+'</span>';
      tip.style.display='block'; tip.style.left=(e.clientX-w/2<0?e.clientX+12:e.clientX-tip.offsetWidth-12)+'px'; tip.style.top=(e.clientY-70)+'px';
    }else{ tip.style.display='none'; }
  };
}

function drawAgentNetwork(agents){
  window._netAgents=agents;
  const c=document.getElementById('agentCanvas'), ctx=c.getContext('2d');
  c.width=c.parentElement.clientWidth; c.height=c.parentElement.clientHeight;
  const w=c.width, h=c.height;
  if(!agents||!agents.length){ ctx.fillStyle='#94a3b8'; ctx.font='12px sans-serif'; ctx.textAlign='center'; ctx.fillText('Inicie simulacao',w/2,h/2); return; }

  // Wheel zoom on the canvas container
  const container=document.getElementById('networkContainer');
  container.addEventListener('wheel', function(e){ e.preventDefault(); zoomNetwork(e.deltaY<0?.15:-.15); }, {passive: false});

  // Sort by influence (followers + posts), top 30 get labels
  const sorted=[...agents].sort((a,b)=>{
    const infA=((a.followers||[]).length||0)*2+(a.posts||0);
    const infB=((b.followers||[]).length||0)*2+(b.posts||0);
    return infB-infA;
  });
  const topIds=new Set(sorted.slice(0,30).map(a=>a.id));
  const display=agents.slice(0,80);
  const positions=[];
  const stanceCounts={supportive:0,critical:0,curious:0,neutral:0};
  const animTime=Date.now()*.001; // For pulsating

  for(let i=0;i<display.length;i++){
    const a=display[i], s=a.stance||'neutral';
    stanceCounts[s]=(stanceCounts[s]||0)+1;
    const angle=(i/display.length)*Math.PI*2+(i%5)*0.4;
    const r=Math.min(w,h)*.36, cx=w/2+Math.cos(angle)*r, cy=h/2+Math.sin(angle)*r;
    positions.push({x:cx,y:cy,agent:a});
  }

  window._netPositions=positions; window._netCanvas=c;

  // Store for animation
  if(!window._netAnimFrame) window._netAnimFrame=0;
  window._netAnimFrame++;

  function render(){
    ctx.clearRect(0,0,w,h);
    ctx.save();
    // Apply zoom/pan transform
    ctx.translate(w/2+netPanX, h/2+netPanY);
    ctx.scale(netZoom, netZoom);
    ctx.translate(-w/2, -h/2);
    const pulse=Math.sin(window._netAnimFrame*.02)*.3+.7; // 0.4-1.0

    // Connections — thicker for similar stance
    for(let i=0;i<positions.length;i++){
      for(let j=i+1;j<positions.length;j++){
        const sameStance=positions[i].agent.stance===positions[j].agent.stance;
        ctx.strokeStyle=sameStance?'rgba(99,102,241,.08)':'rgba(99,102,241,.02)';
        ctx.lineWidth=sameStance?.5:.2;
        ctx.beginPath(); ctx.moveTo(positions[i].x,positions[i].y); ctx.lineTo(positions[j].x,positions[j].y); ctx.stroke();
      }
    }

    // Nodes — size by followers+posts, color by stance
    for(const p of positions){
      const s=p.agent.stance||'neutral';
      const col=s==='supportive'?'#34d399':s==='critical'?'#f87171':s==='curious'?'#22d3ee':'#94a3b8';
      const followers=(p.agent.followers||[]).length||0;
      const r=Math.min(4+followers*.12+(p.agent.posts||0)*.02, 14);
      const isTop=topIds.has(p.agent.id);
      // Pulsating glow for top agents
      const glowR=r+4+(isTop?pulse*4:1);
      ctx.beginPath(); ctx.arc(p.x,p.y,glowR,0,Math.PI*2); ctx.fillStyle=col+(isTop?'25':'10'); ctx.fill();
      // Node
      ctx.beginPath(); ctx.arc(p.x,p.y,r,0,Math.PI*2); ctx.fillStyle=col; ctx.fill();
      ctx.strokeStyle=isTop?'rgba(255,255,255,.4)':'rgba(255,255,255,.1)';
      ctx.lineWidth=isTop?1.4:.6; ctx.stroke();
      // Label for top 30
      if(isTop){
        const name=p.agent.name.length>16?p.agent.name.substring(0,15)+'...':p.agent.name;
        ctx.font='bold 7px sans-serif'; ctx.textAlign='center';
        const labelW=ctx.measureText(name).width+6;
        const labelY=p.y+r+10;
        ctx.fillStyle='rgba(15,23,42,.85)'; ctx.fillRect(p.x-labelW/2,labelY-8,labelW,11);
        ctx.strokeStyle=col+'60'; ctx.lineWidth=.5; ctx.strokeRect(p.x-labelW/2,labelY-8,labelW,11);
        ctx.fillStyle=col; ctx.fillText(name,p.x,labelY+1);
      }
    }
    ctx.restore(); // End zoom/pan transform

    // Legend
    const leg=document.getElementById('networkLegend');
    if(leg) leg.innerHTML=[
      '<span style="color:#34d399">🟢 Apoiadores ('+stanceCounts.supportive+')</span>',
      '<span style="color:#f87171">🔴 Criticos ('+stanceCounts.critical+')</span>',
      '<span style="color:#22d3ee">🔵 Curiosos ('+stanceCounts.curious+')</span>',
      '<span style="color:#94a3b8">⚪ Neutros ('+stanceCounts.neutral+')</span>',
    ].join(' &nbsp;');
  }

  render();

  // Pan (drag) handler
  c.onmousedown=function(e){
    if(e.target!==c) return;
    netDragging=true;
    netDragStart={x:e.clientX-netPanX, y:e.clientY-netPanY};
    c.style.cursor='grabbing';
  };
  c.onmousemove=function(e){
    // Pan drag
    if(netDragging){
      netPanX=e.clientX-netDragStart.x;
      netPanY=e.clientY-netDragStart.y;
      render();
      return;
    }
    // Hover detection
    const rect=c.getBoundingClientRect(), mx=e.clientX-rect.left, my=e.clientY-rect.top;
    const scaleX=w/rect.width, scaleY=h/rect.height;
    // Transform through zoom/pan
    const cx=mx*scaleX-w/2-netPanX, cy=my*scaleY-h/2-netPanY;
    const tx=cx/netZoom+w/2, ty=cy/netZoom+h/2;
    const tip=document.getElementById('agentTooltip');
    let found=null;
    for(const p of positions){
      if(Math.hypot(tx-p.x, ty-p.y)<18/netZoom){ found=p; break; }
    }
    if(found){
      const a=found.agent, s=a.stance||'neutral';
      const col=s==='supportive'?'#34d399':s==='critical'?'#f87171':s==='curious'?'#22d3ee':'#94a3b8';
      const followers=(a.followers||[]).length||0;
      // Buscar perfil psicológico expandido quando disponível
      let psychHTML='';
      if(window._omenData?.predictions){
        psychHTML='<br><span style="font-size:.55rem;color:var(--accent2)">🧠 Perfil Psicológico</span>';
      }
      tip.innerHTML='<b style="color:'+col+'">'+a.name+'</b> ('+(a.labels||['?']).join(', ')+')<br>Stance: <b>'+s+'</b> | Posts: '+(a.posts||0)+'<br>Seguidores: '+followers+(a.emotional_state!==undefined?' | Sent: <span style="color:'+(a.emotional_state>0?'#34d399':'#f87171')+'">'+(a.emotional_state||0).toFixed(2)+'</span>':'')+psychHTML;
      tip.style.display='block'; tip.style.left=(e.clientX-w/2<0?e.clientX+12:e.clientX-tip.offsetWidth-12)+'px'; tip.style.top=(e.clientY-70)+'px';
      // Redraw with highlight
      ctx.clearRect(0,0,w,h);
      for(let i=0;i<positions.length;i++){
        for(let j=i+1;j<positions.length;j++){
          const sameStance=positions[i].agent.stance===positions[j].agent.stance;
          const connToHighlighted=(positions[i]===found||positions[j]===found);
          ctx.strokeStyle=connToHighlighted?(sameStance?'rgba(99,102,241,.25)':'rgba(99,102,241,.12)'):'rgba(99,102,241,.02)';
          ctx.lineWidth=connToHighlighted?1.0:.2;
          ctx.beginPath(); ctx.moveTo(positions[i].x,positions[i].y); ctx.lineTo(positions[j].x,positions[j].y); ctx.stroke();
        }
      }
      for(const p of positions){
        const s2=p.agent.stance||'neutral', isTop2=topIds.has(p.agent.id);
        const col2=s2==='supportive'?'#34d399':s2==='critical'?'#f87171':s2==='curious'?'#22d3ee':'#94a3b8';
        const f2=(p.agent.followers||[]).length||0;
        const r2=Math.min(4+f2*.12+(p.agent.posts||0)*.02,14);
        const opacityHex=Math.round((p===found?1:.25)*255).toString(16).padStart(2,'0');
        ctx.beginPath(); ctx.arc(p.x,p.y,r2+3,0,Math.PI*2); ctx.fillStyle=col2+(p===found?'35':'08'); ctx.fill();
        ctx.beginPath(); ctx.arc(p.x,p.y,r2,0,Math.PI*2); ctx.fillStyle=col2+opacityHex; ctx.fill();
        if(p===found){ ctx.strokeStyle='#fff'; ctx.lineWidth=2; ctx.stroke(); }
        else{ ctx.strokeStyle='rgba(255,255,255,.06)'; ctx.lineWidth=.5; ctx.stroke(); }
        if(isTop2&&p!==found){
          const name2=p.agent.name.length>16?p.agent.name.substring(0,15)+'...':p.agent.name;
          ctx.font='bold 6px sans-serif'; ctx.textAlign='center';
          const lw2=ctx.measureText(name2).width+4, ly2=p.y+r2+8;
          ctx.fillStyle='rgba(15,23,42,.5)'; ctx.fillRect(p.x-lw2/2,ly2-7,lw2,10);
          ctx.fillStyle=col2+'40'; ctx.fillText(name2,p.x,ly2+1);
        }
      }
    }else{
      tip.style.display='none';
    }
  };
  c.onmouseleave=function(){ document.getElementById('agentTooltip').style.display='none'; render(); };
  document.onmouseup=function(){ if(netDragging){ netDragging=false; c.style.cursor='grab'; } };
}
function drawTopicBars(topics){ renderTopicAnalysis(topics, null); }

// ── Análise Multi-Dimensional de Tópicos ──
let topicAnalysisData = null;  // topic_analysis from sim engine
let topicCorrData = null;      // topic_correlations
let selectedTopic = null;      // tópico expandido

function renderTopicAnalysis(topics, enriched){
  const box = document.getElementById('topicAnalysis');
  if(enriched){ topicAnalysisData = enriched; topicCorrData = null; }
  if(!topicAnalysisData && (!topics||!Object.keys(topics).length)){
    box.innerHTML='<div style="color:var(--text2);font-size:.7rem;text-align:center;padding:10px">Inicie simulação</div>'; return;
  }

  const td = topicAnalysisData || {};
  let html = '';

  // ── TABELA PRINCIPAL: Tópico | Sentimento | Sparkline | Volume | Tendência | Std | Stance ──
  const entries = td ? Object.entries(td) : Object.entries(topics).map(([k,v])=>[k,{mean:v,volume:0,std:0,trend:0,dominant_stance:'n/a'}]);
  const colStyle = 'padding:4px 6px;font-size:.7rem;vertical-align:middle';

  html += '<table style="width:100%;border-collapse:collapse;font-size:.7rem">';
  html += '<thead><tr style="color:var(--accent2);border-bottom:1px solid var(--border)">';
  html += '<th style="'+colStyle+'text-align:left">Tópico</th>';
  html += '<th style="'+colStyle+'">Sent</th>';
  html += '<th style="'+colStyle+'">Evolução</th>';
  html += '<th style="'+colStyle+'">Vol</th>';
  html += '<th style="'+colStyle+'">Δ</th>';
  html += '<th style="'+colStyle+'">σ</th>';
  html += '<th style="'+colStyle+'">Stance</th>';
  html += '</tr></thead><tbody>';

  for(const [topic, data] of entries){
    const mean = data.mean||0, vol = data.volume||0, std = data.std||0, trend = data.trend||0;
    const dominant = data.dominant_stance||'n/a';
    const sentCol = mean > 0.05 ? '#34d399' : mean < -0.05 ? '#f87171' : '#fbbf24';
    const trendIcon = trend > 0.03 ? '🟢' : trend < -0.03 ? '🔴' : '🟡';
    const trendCol = trend > 0 ? '#34d399' : trend < 0 ? '#f87171' : '#fbbf24';
    const stanceCol = dominant==='supportive'?'#34d399':dominant==='critical'?'#f87171':'#fbbf24';
    const spark = data.evolution ? data.evolution.map(e=>e.mean) : [];
    const sparkSvg = buildSparkline(spark, 60, 18, mean > 0 ? '#34d399' : mean < 0 ? '#f87171' : '#fbbf24');

    html += '<tr onclick="expandTopic(\''+topic+'\')" style="cursor:pointer;border-bottom:1px solid rgba(30,41,59,.5)" onmouseover="this.style.background=\'rgba(99,102,241,.08)\'" onmouseout="this.style.background=\'\'">';
    html += '<td style="'+colStyle+'text-align:left;font-weight:600">'+topicLabel(topic)+'</td>';
    html += '<td style="'+colStyle+';color:'+sentCol+';font-weight:700">'+(mean>=0?'+':'')+mean.toFixed(3)+'</td>';
    html += '<td style="'+colStyle+'">'+sparkSvg+'</td>';
    html += '<td style="'+colStyle+'">'+vol+'</td>';
    html += '<td style="'+colStyle+';color:'+trendCol+'">'+trendIcon+' '+(trend>=0?'+':'')+trend.toFixed(3)+'</td>';
    html += '<td style="'+colStyle+'">'+std.toFixed(3)+'</td>';
    html += '<td style="'+colStyle+';color:'+stanceCol+'">'+dominant+'</td>';
    html += '</tr>';

    // Linha expandida (detalhes)
    if(selectedTopic === topic){
      const sb = data.stance_breakdown || {};
      const totalStance = Object.values(sb).reduce((a,b)=>a+b,0)||1;
      const cCount = sb.critical||0, sCount = sb.supportive||0, curCount = sb.curious||0, nCount = sb.neutral||0;
      const dominance = cCount>sCount+curCount ? 'Oposicao domina' : sCount>cCount+curCount ? 'Apoio domina' : curCount>sCount+cCount ? 'Curiosidade prevalece' : 'Debate equilibrado';
      const polScore = Math.abs(cCount-sCount)/totalStance;
      const polLabel = polScore>0.5 ? 'Alta polarizacao' : polScore>0.3 ? 'Polarizacao moderada' : 'Baixa polarizacao';
      const nRatio = nCount/totalStance;

      html += '<tr><td colspan="7" style="padding:10px 14px;background:rgba(15,23,42,.5);border-left:3px solid #6366f1;font-size:.68rem;line-height:1.5">';

      // ── BANNER: Resumo interpretativo ──
      const sentimentWord = mean>0.15?'positivo':mean<-0.15?'negativo':'neutro';
      const trendWord = trend>0.05?'melhorando':trend<-0.05?'piorando':'estavel';
      const volWord = std>1.5?'alta volatilidade (opinioes divergentes)':std>0.5?'volatilidade moderada':'opinioes estaveis';
      html += '<div style="background:rgba(99,102,241,.1);border-radius:6px;padding:8px 10px;margin-bottom:10px;border-left:3px solid #6366f1">';
      html += '<div style="font-weight:700;color:var(--accent);margin-bottom:2px">📋 Interpretacao</div>';
      html += '<div style="color:#cbd5e1">O sentimento sobre <b>'+topicLabel(topic)+'</b> e <b style="color:'+(mean>0?'#34d399':'#f87171')+'">'+sentimentWord+'</b> (media '+mean.toFixed(2)+'), ';
      html += 'com tendencia <b style="color:'+(trend>0?'#34d399':'#f87171')+'">'+trendWord+'</b> ao longo das rodadas. ';
      html += 'Ha <b>'+volWord+'</b>. ';
      html += '<b>'+dominance.toLowerCase()+'</b> entre os agentes ('+polLabel.toLowerCase()+').';
      if(nRatio>0.4) html += ' Grande parcela de neutros ('+Math.round(nRatio*100)+'%) sugere que o tema ainda nao gerou engajamento forte.';
      html += '</div></div>';

      html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">';

      // ── COLUNA 1: Engajamento por stance com barras visuais ──
      html += '<div>';
      html += '<div style="font-weight:700;color:var(--accent2);margin-bottom:4px">👥 Quem falou sobre este tema?</div>';
      for(const [st,c] of Object.entries(sb)){
        const sc = st==='supportive'?'#34d399':st==='critical'?'#f87171':st==='curious'?'#22d3ee':'#94a3b8';
        const pct = Math.round(c/totalStance*100);
        const label = st==='supportive'?'Apoiadores':st==='critical'?'Criticos':st==='curious'?'Curiosos':'Neutros';
        html += '<div style="margin-bottom:4px"><div style="display:flex;justify-content:space-between;font-size:.65rem"><span style="color:'+sc+'">'+label+'</span><span>'+c+' ('+pct+'%)</span></div>';
        html += '<div style="height:4px;background:var(--border);border-radius:2px;overflow:hidden"><div style="height:100%;width:'+pct+'%;background:'+sc+';border-radius:2px"></div></div></div>';
      }
      html += '<div style="font-size:.6rem;color:#64748b;margin-top:4px">'+polLabel+' | '+dominance+'</div>';
      html += '</div>';

      // ── COLUNA 2: Estatísticas com explicações ──
      html += '<div>';
      html += '<div style="font-weight:700;color:var(--accent2);margin-bottom:4px">📐 O que os numeros revelam?</div>';
      html += '<table style="width:100%;font-size:.63rem;line-height:1.6">';
      html += '<tr><td style="color:#64748b;padding-right:8px;white-space:nowrap">🔹 Min/Max</td><td>'+((data.min||0).toFixed(2))+' / '+((data.max||0).toFixed(2))+'</td><td style="color:#64748b;font-size:.58rem">Faixa de sentimento</td></tr>';
      html += '<tr><td style="color:#64748b">🔹 Amostras (n)</td><td>'+(data.n||0)+'</td><td style="color:#64748b;font-size:.58rem">Posts analisados</td></tr>';
      html += '<tr><td style="color:#64748b">🔹 Volatilidade</td><td>σ='+std.toFixed(2)+'</td><td style="color:#64748b;font-size:.58rem">'+(std>1?'Opinioes muito dispersas':'Opinioes convergentes')+'</td></tr>';
      const cv = (mean!=0?std/Math.abs(mean):0);
      html += '<tr><td style="color:#64748b">🔹 Consistencia</td><td>CV='+cv.toFixed(2)+'</td><td style="color:#64748b;font-size:.58rem">'+(cv>2?'Sentimento instavel':cv>1?'Moderadamente consistente':'Sentimento consistente')+'</td></tr>';
      html += '<tr><td style="color:#64748b">🔹 Direcao</td><td style="color:'+(trend>0?'#34d399':'#f87171')+'">Δ='+(trend>=0?'+':'')+trend.toFixed(2)+'</td><td style="color:#64748b;font-size:.58rem">'+(Math.abs(trend)<0.05?'Estavel':trend>0?'Aquecendo':'Esfriando')+'</td></tr>';
      html += '</table>';
      html += '</div>';

      // ── Sentimento por rodada (full width) ──
      if(spark.length > 0){
        html += '<div style="grid-column:1/-1">';
        html += '<div style="font-weight:700;color:var(--accent2);margin-bottom:4px">📈 Evolucao do sentimento ao longo das rodadas</div>';
        html += '<div style="margin:4px 0">'+buildSparkline(spark, 200, 30, '#6366f1')+'</div>';
        html += '<div style="display:flex;justify-content:space-between;font-size:.58rem;color:#64748b">';
        html += '<span>Rodada 1: '+(spark[0]||0).toFixed(2)+'</span>';
        html += '<span>Pico: '+(data.max||0).toFixed(2)+'</span>';
        html += '<span>Vale: '+(data.min||0).toFixed(2)+'</span>';
        html += '<span>Rodada '+(spark.length)+': '+(spark[spark.length-1]||0).toFixed(2)+'</span>';
        html += '</div></div>';
      }

      html += '</div></td></tr>';
    }
  }
  html += '</tbody></table>';

  // ── CORRELAÇÕES ──
  if(td && Object.keys(td).length >= 2){
    const tv = {};
    for(const [t,d] of Object.entries(td)){
      if(d.evolution && d.evolution.length >= 3) tv[t] = d.evolution.map(e=>e.mean);
    }
    const tkeys = Object.keys(tv);
    if(tkeys.length >= 2){
      // Encontrar correlações mais fortes para destacar
      let strongest = {r:0, pair:''}, pairs = [];
      for(let i=0;i<tkeys.length;i++){
        for(let j=i+1;j<tkeys.length;j++){
          const a=tv[tkeys[i]], b=tv[tkeys[j]], n=Math.min(a.length,b.length);
          const ma=a.slice(0,n).reduce((s,v)=>s+v,0)/n, mb=b.slice(0,n).reduce((s,v)=>s+v,0)/n;
          let num=0, da=0, db=0;
          for(let k=0;k<n;k++){ num+=(a[k]-ma)*(b[k]-mb); da+=(a[k]-ma)**2; db+=(b[k]-mb)**2; }
          const r = (da>0&&db>0) ? num/Math.sqrt(da*db) : 0;
          if(Math.abs(r)>Math.abs(strongest.r)) strongest = {r, pair: tkeys[i]+' <-> '+tkeys[j]};
          pairs.push({a:tkeys[i], b:tkeys[j], r});
        }
      }

      html += '<div style="margin-top:12px;font-size:.65rem">';
      html += '<div style="font-weight:700;color:var(--accent2);margin-bottom:4px">🔗 Como os temas se relacionam?</div>';
      html += '<div style="color:#94a3b8;font-size:.6rem;margin-bottom:6px">Quanto mais proximo de +1, mais os sentimentos sobem juntos. Quanto mais proximo de -1, mais se movem em direcoes opostas.</div>';

      // Destaque da correlação mais forte
      if(Math.abs(strongest.r) > 0.3){
        const [a,b] = strongest.pair.split(' <-> ');
        const interpretation = strongest.r > 0.6 ? 'fortemente conectados' : strongest.r > 0.3 ? 'moderadamente relacionados' : 'fracamente associados';
        const dir = strongest.r > 0 ? 'Quando o sentimento sobre '+topicLabel(a)+' sobe, o de '+topicLabel(b)+' tende a subir tambem' : 'Quando o sentimento sobre '+topicLabel(a)+' sobe, o de '+topicLabel(b)+' tende a cair';
        html += '<div style="background:rgba(245,158,11,.08);border-radius:4px;padding:6px 8px;margin-bottom:6px;font-size:.6rem;color:#fbbf24">';
        html += '<b>Destaque:</b> '+dir+' (r='+strongest.r.toFixed(2)+', '+interpretation+')</div>';
      }

      // Matriz de correlação
      html += '<table style="width:100%;font-size:.6rem;border-collapse:collapse">';
      html += '<tr><td style="padding:2px 6px;color:#64748b"></td>';
      for(let j=0;j<tkeys.length;j++) html += '<td style="padding:2px 6px;text-align:center;color:#64748b;font-weight:600">'+tkeys[j].substring(0,4)+'</td>';
      html += '</tr>';
      for(let i=0;i<tkeys.length;i++){
        html += '<tr>';
        html += '<td style="padding:2px 6px;color:#64748b;font-weight:600;white-space:nowrap">'+topicLabel(tkeys[i]).substring(0,10)+'</td>';
        for(let j=0;j<tkeys.length;j++){
          if(i===j){ html += '<td style="padding:2px 6px;text-align:center;background:rgba(99,102,241,.1);color:#6366f1">1.0</td>'; continue; }
          const pair = pairs.find(p=>(p.a===tkeys[i]&&p.b===tkeys[j])||(p.a===tkeys[j]&&p.b===tkeys[i]));
          const r = pair ? pair.r : 0;
          const absR = Math.abs(r);
          const bg = absR>0.6 ? 'rgba(245,158,11,.2)' : absR>0.3 ? 'rgba(99,102,241,.1)' : 'transparent';
          const col = absR>0.6 ? '#fbbf24' : absR>0.3 ? '#a5b4fc' : '#475569';
          const symbol = absR>0.6 ? (r>0?'🔶':'🔻') : absR>0.3 ? (r>0?'🔹':'🔸') : '';
          html += '<td style="padding:2px 6px;text-align:center;background:'+bg+';color:'+col+'" title="'+topicLabel(tkeys[i])+' vs '+topicLabel(tkeys[j])+': r='+r.toFixed(2)+'">'+(r>=0?'+':'')+r.toFixed(2)+' '+symbol+'</td>';
        }
        html += '</tr>';
      }
      html += '</table>';

      // Legenda
      html += '<div style="display:flex;gap:12px;margin-top:4px;font-size:.55rem;color:#64748b">';
      html += '<span>🔶 forte (|r|>0.6)</span><span>🔹 moderada (|r|>0.3)</span><span>◻ fraca</span>';
      html += '</div>';
    }
  }

  box.innerHTML = html;
}

function topicLabel(t){ return t.replace(/_/g,' ').replace(/\b\w/g,l=>l.toUpperCase()); }

function expandTopic(topic){
  selectedTopic = (selectedTopic === topic) ? null : topic;
  renderTopicAnalysis(null, topicAnalysisData||{});
}

function buildSparkline(values, w, h, color){
  if(!values||values.length<2) return '';
  let svg = '<svg width="'+w+'" height="'+h+'" style="vertical-align:middle">';
  const min=Math.min(...values), max=Math.max(...values), range=max-min||1;
  let path='';
  for(let i=0;i<values.length;i++){
    const x=(w-4)*i/(values.length-1)+2, y=h-2-(h-4)*(values[i]-min)/range;
    path += (i===0?'M':'L')+x.toFixed(1)+','+y.toFixed(1);
  }
  svg += '<path d="'+path+'" fill="none" stroke="'+color+'" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>';
  // Último ponto
  const lx=(w-4)*(values.length-1)/(values.length-1)+2, ly=h-2-(h-4)*(values[values.length-1]-min)/range;
  svg += '<circle cx="'+lx.toFixed(1)+'" cy="'+ly.toFixed(1)+'" r="2" fill="'+color+'"/>';
  svg += '</svg>';
  return svg;
}

// ── API Calls ──
async function startSim(){
  const agents=document.getElementById('agents').value, rounds=document.getElementById('rounds').value;
  const events=document.getElementById('events').checked;
  setStatus('running','⏳ INICIANDO...'); log(`Iniciando: ${agents} agentes × ${rounds} rodadas`);
  sentimentData.length=0; activityData.length=0;
  if(es) es.close();
  es=new EventSource('/events');
  es.addEventListener('round_update',e=>{
    const d=JSON.parse(e.data);
    document.getElementById('stRound').textContent=`${d.round}/${rounds}`;
    document.getElementById('stActions').textContent=d.actions;
    document.getElementById('stActive').textContent=d.active;
    document.getElementById('stSent').textContent=d.sentiment.toFixed(2);
    sentimentData.push(d.sentiment); activityData.push(d.actions);
    drawSentimentChart(); drawActivityChart();
    if(d.round%5===0) log(`Rodada ${d.round}: ${d.actions} ações, ${d.active} ativos`);
  });
  es.addEventListener('simulation_complete',e=>{
    const d=JSON.parse(e.data); simRunning=false;
    setStatus('idle','✅ CONCLUÍDO');
    document.getElementById('stSpeed').textContent=Math.round(d.actions_per_second)+'/s';
    const pats=d.emergent_patterns||[];
    if(pats.length) document.getElementById('stPolar').textContent=pats[0].score?.toFixed(2)||'?';
    log(`✅ Concluído: ${d.total_actions} ações em ${d.duration_seconds}s`);
    if(pats.length) pats.forEach(p=>log(`🔍 ${p.type}: ${p.interpretation}`));
    setTimeout(() => {
      if(d.topic_analysis) renderTopicAnalysis(d.topic_sentiments, d.topic_analysis);
      if(d.topic_correlations) topicCorrData = d.topic_correlations;
      loadAgents(); es.close();
    }, 10);
  });
  es.addEventListener('simulation_error',e=>{ setStatus('error','✗ ERRO'); log('❌ '+JSON.parse(e.data).error); });
  await fetch('/api/start',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({agents:parseInt(agents),rounds:parseInt(rounds),events:events.toString()})});
  simRunning=true;
}
async function stopSim(){ await fetch('/api/stop',{method:'POST'}); setStatus('idle'); if(es) es.close(); simRunning=false; }
let evtHistory = [];
const PRESETS = {
  crise: {title:'Crise econômica', desc:'Queda do PIB, inflação dispara, desemprego em alta', impact:-0.8, duration:4},
  tech: {title:'Avanço tecnológico', desc:'Nova IA revoluciona setor produtivo', impact:0.7, duration:5},
  ambiental: {title:'Desastre ambiental', desc:'Enchentes e secas extremas atingem múltiplas regiões', impact:-0.9, duration:3},
  politica: {title:'Crise política', desc:'Escândalo de corrupção abala confiança nas instituições', impact:-0.6, duration:4},
  saude: {title:'Emergência sanitária', desc:'Novo surto epidêmico pressiona sistema de saúde', impact:-0.7, duration:5},
  positivo: {title:'Notícia positiva', desc:'Acordo internacional impulsiona comércio e investimentos', impact:0.6, duration:4},
};
function loadEventPreset(){
  const v=document.getElementById('evtPreset').value;
  if(!v||v==='custom') return;
  const p=PRESETS[v];
  document.getElementById('evtTitle').value=p.title;
  document.getElementById('evtDesc').value=p.desc;
  document.getElementById('evtImpact').value=p.impact;
  document.getElementById('impactVal').textContent=p.impact;
  document.getElementById('evtDuration').value=p.duration;
  document.getElementById('durVal').textContent=p.duration;
}
function injectRandomEvent(){
  const keys=Object.keys(PRESETS), p=PRESETS[keys[Math.floor(Math.random()*keys.length)]];
  document.getElementById('evtTitle').value=p.title+' #'+Math.floor(Math.random()*900+100);
  document.getElementById('evtDesc').value=p.desc;
  const impact=(p.impact+(Math.random()-.5)*0.4).toFixed(1);
  document.getElementById('evtImpact').value=impact;
  document.getElementById('impactVal').textContent=impact;
  document.getElementById('evtDuration').value=p.duration;
  document.getElementById('durVal').textContent=p.duration;
  injectEvent();
}
async function injectEvent(){
  if(!simRunning) return log('⚠ Inicie a simulação primeiro');
  const title=document.getElementById('evtTitle').value||'Evento sem título';
  const desc=document.getElementById('evtDesc').value||'';
  const impact=parseFloat(document.getElementById('evtImpact').value)||0;
  const duration=parseInt(document.getElementById('evtDuration').value)||3;
  
  log(`📡 Injetando evento e disparando download de dataset/busca acadêmica...`);
  try {
    const res=await fetch('/api/events/inject',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({title,description:desc,impact:Math.abs(impact),round:1,duration})});
    const data=await res.json();
    const icon=impact>0?'📈':impact<0?'📉':'📊';
    evtHistory.unshift({time:new Date().toLocaleTimeString(), title, impact, duration});
    if(evtHistory.length>20) evtHistory.pop();
    renderEventHistory();
    if(data.message) {
      log(`${icon} Evento '${title}': ${data.message}`);
    } else {
      log(`${icon} Evento: ${title} (impacto: ${impact>0?'+':''}${impact}, ${duration} rod)`);
    }
  } catch(e) {
    log(`❌ Erro ao injetar evento: ${e.message}`);
  }
}
function renderEventHistory(){
  const box=document.getElementById('eventHistory');
  if(!evtHistory.length){ box.innerHTML='<div style="text-align:center;padding:4px">Nenhum evento</div>'; return; }
  box.innerHTML=evtHistory.map(e=>{
    const col=e.impact>0?'#34d399':e.impact<0?'#f87171':'#fbbf24';
    return `<div style="display:flex;justify-content:space-between;align-items:center;padding:2px 0;border-bottom:1px solid rgba(30,41,59,.3)">
      <span style="color:${col};font-weight:600">${e.impact>0?'+':''}${e.impact}</span>
      <span style="max-width:140px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${e.title}</span>
      <span>${e.time}</span>
    </div>`;
  }).join('');
}
async function generateReport(){
  log('📄 Gerando relatório Qualis A1...');
  document.querySelector('#topicAnalysis').innerHTML='<div style="text-align:center;padding:20px;color:var(--accent)">📄 Gerando relatório com dados reais e citações acadêmicas...</div>';
  try{
    const res=await fetch('/api/report',{method:'POST',headers:{'Content-Type':'application/json'}});
    const data=await res.json();
    if(data.report_url){
      log('✅ Relatório gerado: '+data.report_url);
      window.open(data.report_url,'_blank');
    }else if(data.error){
      log('❌ Erro: '+data.error);
    }
  }catch(e){ log('❌ Falha ao gerar relatório: '+e.message); }
}
async function runOmenPrediction(){
  log('🔮 Executando previsões com 500+ variáveis...');
  try{
    const res=await fetch('/api/omen/predict',{method:'POST'});
    const d=await res.json();
    window._omenData=d;
    if(d.predictions){
      const catEmoji={'economico':'📉','geopolitico':'⚔️','saude':'🏥','climatico':'🌍','tecnologico':'🤖','social':'👥','financeiro':'💰','etnico-cultural':'🧬'};
      let html='<div style="font-size:.65rem">';
      let idx=0;
      for(const [s,p] of Object.entries(d.predictions)){
        const col=p.risk_level==='CRITICO'?'#f87171':p.risk_level==='ALTO'?'#f87171':p.risk_level==='MEDIO'?'#fbbf24':'#34d399';
        const confCol=p.confidence_score>=80?'#34d399':p.confidence_score>=50?'#fbbf24':'#f87171';
        const emoji=catEmoji[p.category]||'📊';
        const ft=p.forecast_table||[];
        const fs=p.forecast_stats||{};
        const fm=p.forecast_metrics||{};
        idx++;
        html+=`<div id="pred_${idx}" style="padding:4px 0;border-bottom:1px solid rgba(30,41,59,.3);cursor:pointer" onclick="togglePrediction(${idx})">
          <div style="display:flex;justify-content:space-between;align-items:center">
            <span>${emoji} <b>${p.label}</b> <span style="background:rgba(52,211,153,0.12);color:${confCol};padding:1px 4px;border-radius:4px;font-size:.5rem;font-weight:bold">🛡️ Confiança: ${p.confidence_score}%</span></span>
            <span style="color:${col};font-weight:700">${p.risk_level}</span>
          </div>
          <div style="font-size:.55rem;color:var(--text2)">
            ${ft.length>0?ft[0].date+' | Prev: '+ft[0].forecast+' ±'+ft[0].margin_of_error:'...'} | ${p.recommendation?.substring(0,60)||''}...
          </div>
          <div id="pred_detail_${idx}" style="display:none;margin-top:6px;padding:6px;background:rgba(0,0,0,.2);border-radius:6px;font-size:.55rem;max-height:200px;overflow-y:auto">
            ${p.gaps_detected && p.gaps_detected.length > 0 ? `
            <div style="margin-bottom:6px;padding:4px 6px;background:rgba(248,113,113,0.15);border:1px solid rgba(248,113,113,0.3);border-radius:4px;color:#f87171">
              <b>⚠️ Lacunas Detectadas (Reversa):</b><br>${p.gaps_detected.join('<br>')}
            </div>` : ''}
            <b>🛡️ Rastreabilidade de Evidências (Reversa):</b><br>
            <div style="margin-bottom:6px;color:var(--accent2);line-height:1.2">
              ${p.traceability ? p.traceability.map(t=>`- <b>${t.label}</b> [<i>Fonte: ${t.source}</i>]`).join('<br>') : 'Nenhuma fonte mapeada.'}
            </div>
            ${ft.length>0?`
            <b>📅 Cronograma:</b><br>
            <table style="width:100%;font-size:.5rem;margin:4px 0">
            <tr style="color:var(--accent2)"><td>Data</td><td>Prev</td><td>IC 80%</td><td>IC 95%</td><td>±Erro</td></tr>
            ${ft.slice(0,6).map(f=>`<tr><td>${f.date}</td><td style="color:${f.forecast>100?'#34d399':'#f87171'}">${f.forecast}</td><td>[${f.lo80},${f.hi80}]</td><td>[${f.lo95},${f.hi95}]</td><td>${f.margin_of_error}</td></tr>`).join('')}
            </table>`:''}
            ${fs.total_change_pct!==undefined?`<b>📊 Estatísticas:</b> Último: ${fs.last_value} → Final: ${fs.horizon_end_value} (${fs.total_change_pct>0?'+':''}${fs.total_change_pct}%) | Erro médio: ±${fs.avg_margin_of_error}<br>`:''}
            ${fm.mape_percent!==undefined?`<b>📐 Métricas:</b> MAPE=${fm.mape_percent}% | RMSE=${fm.rmse} | R²=${fm.r_squared} | ${fm.interpretation||''}<br>`:''}
            <b>🌍 Nações:</b> ${(p.nations_analyzed||[]).map(n=>n.name).join(', ')}<br>
            <b>⚠️ Riscos:</b> ${(p.risk_factors||[]).map(r=>r.factor).join('; ')}<br>
            <b>✅ Vantagens:</b> ${(p.advantage_factors||[]).join('; ')}<br>
            <b>📚 Ref:</b> Hyndman & Athanasopoulos (2021), Box-Jenkins (2015), Makridakis (2020)
          </div>
        </div>`;
      }
      html+=`<div style="margin-top:4px;color:var(--text2);font-size:.5rem">${d.total_scenarios||'?'} cenários · ${d.total_variables||'?'} variáveis · ${d.total_nations||'?'} nações</div></div>`;
      document.getElementById('topicAnalysis').innerHTML='<h2 style="margin-top:10px;font-size:.75rem">🔮 Previsões (clique para expandir)</h2>'+html;
      log('🔮 '+Object.keys(d.predictions).length+' cenários previstos');
    }
  }catch(e){ log('❌ Falha: '+e.message); }
}
function togglePrediction(idx){
  const el=document.getElementById('pred_detail_'+idx);
  if(el) el.style.display=el.style.display==='none'?'block':'none';
}
async function auditOmen(){
  log('🔍 Executando auditoria comparativa (Previsto vs Ocorrido)...');
  try{
    const res=await fetch('/api/omen/audit');
    const d=await res.json();
    if(d.error) {
      log('❌ Erro na auditoria: '+d.error);
      return;
    }
    const audit = d.audit || [];
    if(audit.length === 0){
      log('⚠ Nenhum dado histórico no omen_logs.db para comparação.');
      document.getElementById('topicAnalysis').innerHTML='<div style="color:var(--text2);font-size:.7rem;text-align:center;padding:10px">Nenhum log no omen_logs.db. Execute previsões e simule primeiro!</div>';
      return;
    }
    
    let html='<div style="font-size:.65rem">';
    html += '<h2 style="margin-top:10px;font-size:.75rem">🔍 Auditoria (Previsto vs Ocorrido)</h2>';
    html += '<table style="width:100%;font-size:.55rem;margin:4px 0;border-collapse:collapse">';
    html += '<tr style="color:var(--accent2);border-bottom:1px solid var(--border)"><td>Cenário</td><td>Previsto</td><td>Ocorrido</td><td>Erro</td><td>Grau</td></tr>';
    
    audit.forEach(a => {
      const col = a.accuracy_grade === 'Excelente' ? '#34d399' : a.accuracy_grade === 'Boa' ? '#10b981' : a.accuracy_grade === 'Regular' ? '#fbbf24' : '#f87171';
      const confCol = a.confidence_score >= 80 ? '#34d399' : a.confidence_score >= 50 ? '#fbbf24' : '#f87171';
      const gapIcon = a.gaps_detected && a.gaps_detected.length > 0 ? '⚠️' : '✅';
      
      html += `<tr style="border-bottom:1px solid rgba(255,255,255,0.05)">
        <td>
          <b>${a.scenario}</b> <span style="color:${confCol};font-weight:700" title="Confiança Reversa">${a.confidence_score}%</span> ${gapIcon}
          <br><span style="color:var(--text2)">${a.timestamp.substring(11,19)}</span>
          <div style="font-size:.45rem;color:#888;margin-top:2px">
            🔍 Fontes: ${a.traceability ? a.traceability.map(t=>t.source).filter((v,i,self)=>self.indexOf(v)===i).join(', ') : 'Simulação'}
          </div>
          ${a.gaps_detected && a.gaps_detected.length > 0 ? `<div style="font-size:.45rem;color:#f87171;margin-top:1px">⚠️ Lacunas: ${a.gaps_detected.join('; ')}</div>` : ''}
        </td>
        <td>${a.predicted_change_pct > 0 ? '+' : ''}${a.predicted_change_pct}%</td>
        <td>${a.actual_change_pct > 0 ? '+' : ''}${a.actual_change_pct}%</td>
        <td>${a.error_margin}%</td>
        <td style="color:${col};font-weight:bold">${a.accuracy_grade}</td>
      </tr>`;
    });
    html += '</table></div>';
    document.getElementById('topicAnalysis').innerHTML=html;
    log('🔍 Auditoria concluída: ' + audit.length + ' cenários comparados.');
  }catch(e){ log('❌ Falha na auditoria: '+e.message); }
}
async function omniResearch(){
  const topic=document.getElementById('researchTopic').value||'Impacto da IA no mercado de trabalho brasileiro';
  log('🔬 MiroFishOmni pesquisando: '+topic);
  document.querySelector('#topicAnalysis').innerHTML='<div style="text-align:center;padding:20px;color:#34d399;font-size:.75rem">🔬 MiroFishOmni — Pipeline Completo<br><small>Fase 1/5: Coletando dados reais...</small></div>';
  try{
    const res=await fetch('/api/research',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({topic})});
    const d=await res.json();
    if(d.pipeline){
      let html='<div style="font-size:.65rem">';
      html+=`<b>🔬 Pesquisa: ${d.topic}</b><br>`;
      html+=`<span style="color:var(--accent2)">Pipeline:</span> ${d.pipeline.map(p=>p.replace('phase','Fase')).join(' → ')}<br>`;
      html+=`<span style="color:#34d399">Módulos ativos:</span> ${(d.modules_active||[]).length}<br>`;
      if(d.article) html+=`📄 <a href="${d.article.path.replace(/^.*\\\\\.reversa/,'/api/report/view?path=')}" target="_blank" style="color:#fbbf24">Artigo Qualis A1</a> (${d.article.size_chars}c)<br>`;
      if(d.simulation_summary) html+=`Sim: ${d.simulation_summary.agents} agentes · ${d.simulation_summary.actions} ações · sent ${d.simulation_summary.sentiment?.toFixed(2)||0}<br>`;
      if(d.predictions) html+=`Previsões: ${d.predictions.scenarios} cenários<br>`;
      if(d.ml_analysis) html+=`ML: ${d.ml_analysis.significant_correlations} corr sig · ${d.ml_analysis.anomalies} anomalias<br>`;
      html+='</div>';
      document.getElementById('topicAnalysis').innerHTML='<h2 style="margin-top:10px;font-size:.75rem">🔬 Resultados Omni</h2>'+html;
      log('✅ Pesquisa concluída! '+d.pipeline.length+' fases.');
    }
  }catch(e){ log('❌ Falha na pesquisa: '+e.message); }
}
async function runWarRoom(){
  const topic=document.getElementById('researchTopic').value||'Impacto da IA no mercado de trabalho brasileiro';
  log('⚔️ War Room: 10 agentes analisando...');
  document.querySelector('#topicAnalysis').innerHTML='<div style="text-align:center;padding:20px;color:#f87171;font-size:.75rem">⚔️ Multi-Agent War Room<br><small>10 agentes epistêmicos colaborando...</small></div>';
  try{
    const res=await fetch('/api/warroom',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({problem:topic})});
    const d=await res.json();
    if(d.synthesis){
      let html='<div style="font-size:.65rem">';
      html+=`<b>⚔️ ${d.problem?.substring(0,60)}...</b><br>`;
      html+=`<span style="color:var(--accent2)">Consenso:</span> ${d.synthesis.consensus_level}<br>`;
      html+=`<span style="color:#f87171">🎯 Recomendação:</span> ${d.synthesis.recommendation?.substring(0,150)}...<br>`;
      html+=`<span style="color:var(--text2)">Agentes:</span> ${d.agents_activated?.join(', ')||'10'}<br>`;
      html+=`<b>🔑 Insights (${(d.synthesis.key_insights||[]).length}):</b><br>`;
      (d.synthesis.key_insights||[]).forEach(i=>html+=`- ${i.substring(0,120)}...<br>`);
      html+='</div>';
      document.getElementById('topicAnalysis').innerHTML='<h2 style="margin-top:10px;font-size:.75rem">⚔️ War Room</h2>'+html;
      log('⚔️ War Room: '+d.synthesis.consensus_level+' consenso');
    }
  }catch(e){ log('❌ War Room falhou: '+e.message); }
}
async function loadAgents(){
  const list=document.getElementById('agentList'), sel=document.getElementById('chatAgent');
  try{
    const res=await fetch('/api/agents');
    if(!res.ok){ list.innerHTML='<div style=\"color:var(--red);font-size:.75rem;padding:10px;text-align:center\">Erro HTTP '+res.status+'</div>'; return; }
    const agents=await res.json();
    if(!agents||!agents.length){ list.innerHTML='<div style=\"color:var(--yellow);font-size:.75rem;padding:10px;text-align:center\">Nenhum agente. Inicie uma simulação.<br><button onclick=\"loadAgents()\" style=\"margin-top:6px;background:var(--accent);color:#fff;border:none;padding:4px 12px;border-radius:4px;cursor:pointer;font-size:.7rem\">🔄 Tentar novamente</button></div>'; return; }
    list.innerHTML=''; sel.innerHTML='<option value=\"\">Selecione um agente...</option>';
    agents.slice(0,80).forEach(a=>{
      const div=document.createElement('div'); div.className='agent-mini';
      const col=a.emotional_state>0?'#34d399':a.emotional_state<0?'#f87171':'#94a3b8';
      div.innerHTML='<div class=\"dot\" style=\"background:'+col+'\"></div><div class=\"info\"><div class=\"n\">'+a.name+'</div><div class=\"m\">'+a.stance+' · '+a.posts+' posts</div></div><div class=\"sent\" style=\"color:'+col+'\">'+(a.emotional_state||0).toFixed(1)+'</div>';
      div.onclick=function(){ document.getElementById('chatAgent').value=a.id; document.getElementById('chatInput').focus(); };
      list.appendChild(div);
      const opt=document.createElement('option'); opt.value=a.id; opt.textContent=a.name+' ('+a.stance+')'; sel.appendChild(opt);
    });
    drawAgentNetwork(agents);
  }catch(e){ list.innerHTML='<div style=\"color:var(--red);font-size:.75rem;padding:10px;text-align:center\">Servidor offline: '+e.message+'<br><button onclick=\"loadAgents()\" style=\"margin-top:6px;background:var(--accent);color:#fff;border:none;padding:4px 12px;border-radius:4px;cursor:pointer;font-size:.7rem\">🔄 Tentar novamente</button></div>'; }
}
async function sendChat(){
  const aid=document.getElementById('chatAgent').value, msg=document.getElementById('chatInput').value;
  if(!aid||!msg) return;
  const box=document.getElementById('chatBox');
  box.innerHTML+=`<div class="chat-msg user"><div class="sender user">Você</div>${msg}</div>`;
  box.scrollTop=box.scrollHeight; document.getElementById('chatInput').value='';
  try{
    const res=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({agent_id:aid,message:msg})});
    const d=await res.json();
    box.innerHTML+=`<div class="chat-msg agent"><div class="sender agent">🤖 ${d.agent_name}</div>${d.reply}</div>`;
    box.scrollTop=box.scrollHeight;
  }catch(e){ box.innerHTML+=`<div class="chat-msg agent"><div class="sender agent">⚠ Erro</div>Servidor offline</div>`; }
}
window.addEventListener('resize',()=>{ drawSentimentChart(); drawActivityChart(); });

// ── WhatsApp Integration (upload-based) ──
let waProfiles=null, waSimAgents=null;
function updateWAStatus(t,c){ let e=document.getElementById('waStatus'); if(e){e.textContent=t;e.style.color=c||'var(--text2)';} }
async function whatsappUploadChat(input){
  const file=input.files[0]; if(!file) return;
  document.getElementById('waQR').innerHTML='<span style="color:#fbbf24">Processando '+file.name+'...</span>';
  const reader=new FileReader();
  reader.onload=async function(e){
    const text=e.target.result;
    try{
      const res=await fetch('/api/whatsapp/parse',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({chat_text:text})});
      const d=await res.json();
      if(d.error){ document.getElementById('waQR').innerHTML='<span style="color:#f87171">'+d.error+'</span>'; return; }
      waProfiles=d.profiles; waSimAgents=d.sim_agents;
      document.getElementById('waQR').innerHTML='<span style="color:#25D366">'+d.profile_count+' perfis extraidos de '+d.message_count+' mensagens!</span>';
      document.getElementById('waActions').style.display='block';
      document.getElementById('waProfileInfo').innerHTML='<b>Stances:</b> '+JSON.stringify(d.group_stats?.stance_distribution||{}).replace(/[{}"]/g,'').replace(/,/g,', ');
      // Mostrar mapeamento psicológico expandido
      let chatHTML='';
      const mapping=d.expanded_mapping||{};
      Object.entries(d.profiles||{}).slice(0,12).forEach(([n,p])=>{
        const col=p.dominant_stance==='supportive'?'#34d399':p.dominant_stance==='critical'?'#f87171':'#94a3b8';
        const match=mapping[n];
        const best= match?.best_match;
        chatHTML+='<div style="padding:2px 4px;border-bottom:1px solid rgba(30,41,59,.3)">';
        chatHTML+='<b style="color:'+col+'">'+n+'</b>: '+p.dominant_stance+' ('+p.message_count+' msgs)';
        if(best){
          chatHTML+='<br><span style="font-size:.5rem;color:var(--accent2)">🧠 '+best.profile_name+' ('+best.category+')</span>';
          chatHTML+='<br><span style="font-size:.45rem;color:#64748b">'+best.description.substring(0,80)+'...</span>';
        }
        chatHTML+='</div>';
      });
      document.getElementById('waChatList').innerHTML=chatHTML;
      updateWAStatus(d.profile_count+' perfis','#25D366');
      log('WhatsApp: '+d.profile_count+' perfis de '+d.message_count+' msgs');
    }catch(err){ document.getElementById('waQR').innerHTML='<span style="color:#f87171">Erro: '+err.message+'</span>'; }
  };
  reader.readAsText(file);
}
async function whatsappApplyProfiles(){
  if(!waSimAgents){ log('Nenhum perfil carregado'); return; }
  log('Aplicando '+waSimAgents.length+' perfis reais na simulacao...');
  try{
    const res=await fetch('/api/whatsapp/apply',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({agents:waSimAgents})});
    const d=await res.json();
    log('Simulacao calibrada: '+d.count+' agentes!');
    updateWAStatus(d.count+' agentes','#25D366');
    loadAgents();
  }catch(e){ log('Erro ao aplicar perfis'); }
}
log('🐟 MiroFish Local pronto — configure e inicie a simulação');
loadAgents();  // Carregar agentes pré-carregados ao abrir a página
</script>

<!-- FULLSCREEN NETWORK MODAL -->
<div id="networkModal" style="display:none;position:fixed;top:0;left:0;width:100vw;height:100vh;background:rgba(2,6,23,.96);z-index:9999;flex-direction:column">
  <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 16px;border-bottom:1px solid var(--border)">
    <span style="color:var(--accent);font-weight:700">🔗 Rede de Agentes — Tela Cheia</span>
    <span style="color:var(--text2);font-size:.7rem" id="modalLegend"></span>
    <div style="display:flex;gap:4px;align-items:center">
      <button onclick="zoomNetwork(.2)" title="Zoom +" style="background:rgba(30,41,59,.8);border:1px solid var(--border);color:var(--text);width:24px;height:24px;border-radius:4px;cursor:pointer;font-size:.7rem">+</button>
      <button onclick="zoomNetwork(-.2)" title="Zoom -" style="background:rgba(30,41,59,.8);border:1px solid var(--border);color:var(--text);width:24px;height:24px;border-radius:4px;cursor:pointer;font-size:.7rem">−</button>
      <button onclick="resetNetworkView()" title="Reset" style="background:rgba(30,41,59,.8);border:1px solid var(--border);color:var(--text);width:24px;height:24px;border-radius:4px;cursor:pointer;font-size:.6rem">⌂</button>
      <button onclick="closeNetworkModal()" title="Fechar" style="background:rgba(248,113,113,.2);border:1px solid #f87171;color:#f87171;width:24px;height:24px;border-radius:4px;cursor:pointer;font-size:.8rem;font-weight:700">✕</button>
    </div>
  </div>
  <div style="flex:1;position:relative;overflow:hidden" id="modalCanvasContainer">
    <canvas id="modalNetworkCanvas" style="width:100%;height:100%"></canvas>
  </div>
  <div style="display:flex;gap:8px;justify-content:center;padding:6px;font-size:.6rem;border-top:1px solid var(--border)" id="modalFullLegend"></div>
</div>

<style>
#networkModal.show{display:flex !important}
#networkContainer canvas{cursor:grab}
#networkContainer canvas:active{cursor:grabbing}
</style>

</body>
</html>
"""

# ═══════════════════════════════════════════════════════════════════
# HTTP Request Handler
# ═══════════════════════════════════════════════════════════════════

class MiroFishHandler(http.server.BaseHTTPRequestHandler):
    """Handler HTTP para o MiroFish Local Server."""

    def log_message(self, format, *args):
        pass  # Silencioso

    def handle(self):
        """Suprime erros de conexão abortada na raiz do socket."""
        try:
            super().handle()
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
            pass
        except OSError as e:
            if getattr(e, 'winerror', None) in (10053, 10054, 32):
                pass
            else:
                raise

    def _send_json(self, data, status=200):
        try:
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
            pass

    def _send_html(self, html, status=200):
        try:
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode())
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
            pass

    def do_GET(self):
        try:
            self._do_GET_inner()
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
            pass

    def _do_GET_inner(self):
        path = self.path.split("?")[0]

        if path == "/" or path == "/index.html":
            self._send_html(HTML_FRONTEND)

        elif path == "/favicon.ico":
            try:
                self.send_response(204)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
                pass
            return

        elif path == "/events":
            # SSE endpoint
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            q = queue.Queue(maxsize=100)
            STATE.sse_clients.append(q)

            try:
                self.request.settimeout(5.0)  # Previne travamento de thread por deadlock de buffer SSE
                while True:
                    try:
                        msg = q.get(timeout=30)
                        self.wfile.write(msg.encode())
                        self.wfile.flush()
                    except queue.Empty:
                        # Heartbeat para manter conexao SSE viva
                        try:
                            self.wfile.write(": heartbeat\n\n".encode())
                            self.wfile.flush()
                        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
                            break
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
                pass
            finally:
                if q in STATE.sse_clients:
                    STATE.sse_clients.remove(q)

        elif path == "/api/health":
            try:
                import time
                import shutil
                import sqlite3
                
                health_report = {
                    "status": "healthy",
                    "timestamp": datetime.now(timezone(timedelta(hours=-3))).isoformat(),
                    "services": {},
                    "system": {}
                }
                
                # 1. Testar Latência SQL (Omen DB)
                db_path = os.path.join(_REVERSA_DIR, "omen_logs.db")
                t0 = time.perf_counter()
                try:
                    conn = sqlite3.connect(db_path, timeout=1.0)
                    conn.execute("SELECT 1;").fetchone()
                    conn.close()
                    db_latency = (time.perf_counter() - t0) * 1000
                    health_report["services"]["database_omen"] = {
                        "status": "up",
                        "latency_ms": round(db_latency, 2)
                    }
                except Exception as e:
                    health_report["status"] = "degraded"
                    health_report["services"]["database_omen"] = {
                        "status": "down",
                        "error": str(e)
                    }

                # 2. Testar banco de simulação se ativo
                if getattr(STATE, 'engine', None) and getattr(STATE.engine, 'db_path', None):
                    t0 = time.perf_counter()
                    try:
                        conn = sqlite3.connect(STATE.engine.db_path, timeout=1.0)
                        conn.execute("SELECT 1;").fetchone()
                        integrity = conn.execute("PRAGMA integrity_check;").fetchone()[0]
                        conn.close()
                        sim_db_latency = (time.perf_counter() - t0) * 1000
                        health_report["services"]["database_sim"] = {
                            "status": "up" if integrity == "ok" else "corrupted",
                            "latency_ms": round(sim_db_latency, 2),
                            "integrity": integrity
                        }
                    except Exception as e:
                        health_report["services"]["database_sim"] = {
                            "status": "down",
                            "error": str(e)
                        }

                # 3. Espaço em Disco
                try:
                    total, used, free = shutil.disk_usage(_REVERSA_DIR)
                    health_report["system"]["disk_space"] = {
                        "total_gb": round(total / (1024**3), 2),
                        "used_gb": round(used / (1024**3), 2),
                        "free_gb": round(free / (1024**3), 2),
                        "free_percent": round((free / total) * 100, 2)
                    }
                except Exception as e:
                    health_report["system"]["disk_space"] = {
                        "status": "error",
                        "error": str(e)
                    }

                # 4. Conexões SSE
                health_report["services"]["sse"] = {
                    "active_clients": len(STATE.sse_clients),
                    "simulation_running": getattr(STATE, 'simulation_running', False)
                }

                self._send_json(health_report)
            except Exception as e:
                self._send_json({"status": "error", "message": str(e)}, 500)

        elif path == "/api/omen/audit":
            try:
                db_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", ".reversa", "omen_logs.db")
                if not os.path.exists(db_path):
                    self._send_json({"audit": []})
                    return
                import sqlite3
                conn = sqlite3.connect(db_path)
                conn.execute("PRAGMA journal_mode=WAL;")
                conn.row_factory = sqlite3.Row
                c = conn.cursor()
                try:
                    c.execute("SELECT id, timestamp, scenario, category, risk_level, trend_strength, recommendation, confidence_score, traceability, gaps_detected FROM omen_logs ORDER BY id DESC LIMIT 50")
                    logs = [dict(row) for row in c.fetchall()]
                except sqlite3.OperationalError:
                    # Fallback caso a tabela não tenha as novas colunas
                    c.execute("SELECT id, timestamp, scenario, category, risk_level, trend_strength, recommendation FROM omen_logs ORDER BY id DESC LIMIT 50")
                    logs = [dict(row) for row in c.fetchall()]
                conn.close()

                audit_results = []
                sim_data = STATE.last_summary or {}
                topic_analysis = sim_data.get("topic_analysis", {})

                topic_map = {
                    "recessao_global": "economia",
                    "inflacao_crise": "inflacao",
                    "pandemia_global": "saude",
                    "ia_etica": "ia_regulacao",
                    "automacao": "ia_impacto",
                    "mudancas_climaticas": "meio_ambiente"
                }

                for log in logs:
                    scenario = log["scenario"]
                    predicted_change = log["trend_strength"] or 0.0
                    topic = topic_map.get(scenario, "economia")
                    actual_change_pct = 0.0
                    if topic in topic_analysis:
                        actual_data = topic_analysis[topic]
                        actual_change_pct = actual_data.get("trend", 0.0) * 50.0
                    error = abs(predicted_change - actual_change_pct)
                    
                    try:
                        traceability = json.loads(log.get("traceability", "[]"))
                    except:
                        traceability = []
                    try:
                        gaps = json.loads(log.get("gaps_detected", "[]"))
                    except:
                        gaps = []

                    audit_results.append({
                        "id": log["id"],
                        "timestamp": log["timestamp"],
                        "scenario": scenario,
                        "predicted_change_pct": round(predicted_change, 2),
                        "actual_change_pct": round(actual_change_pct, 2),
                        "error_margin": round(error, 2),
                        "accuracy_grade": "Excelente" if error < 5 else "Boa" if error < 15 else "Regular" if error < 30 else "Inconsistente",
                        "recommendation": log["recommendation"],
                        "confidence_score": log.get("confidence_score", 100.0),
                        "traceability": traceability,
                        "gaps_detected": gaps
                    })
                self._send_json({"audit": audit_results})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)

        elif path == "/api/status":
            self._send_json({
                "running": STATE.simulation_running,
                "agents": len(STATE.engine.agents) if STATE.engine else 0,
                "rounds": STATE.engine.current_round if STATE.engine else 0,
                "stats": STATE.stats,
            })

        elif path == "/api/agents":
            self._send_json(get_agent_list())

        elif path == "/api/chat_history":
            self._send_json(STATE.chat_history[-50:])

        elif path == "/api/report/view":
            report_path = getattr(STATE, 'last_report_path', None)
            if report_path and os.path.exists(report_path):
                with open(report_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/markdown; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(content.encode())
            else:
                self._send_json({"error": "Nenhum relatorio gerado ainda. Execute uma simulacao primeiro."}, 404)

        else:
            self._send_json({"error": "Not found"}, 404)

    def do_POST(self):
        try:
            self._do_POST_inner()
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
            pass

    def _do_POST_inner(self):
        path = self.path.split("?")[0]
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode() if content_length > 0 else "{}"

        try:
            params = json.loads(body) if body else {}
        except:
            params = {}

        if path == "/api/start":
            if STATE.simulation_running:
                self._send_json({"error": "Simulação já está rodando"}, 409)
                return

            STATE.simulation_thread = threading.Thread(
                target=run_simulation_async, args=(params,), daemon=True
            )
            STATE.simulation_thread.start()
            self._send_json({"status": "started", "message": "Simulação iniciada"})

        elif path == "/api/stop":
            STATE.simulation_running = False
            broadcast_sse("simulation_stopped", {"message": "Interrompida pelo usuário"})
            self._send_json({"status": "stopped"})

        elif path == "/api/chat":
            agent_id = params.get("agent_id", "")
            message = params.get("message", "")
            if not agent_id or not message:
                self._send_json({"error": "agent_id e message são obrigatórios"}, 400)
                return

            result = chat_with_agent(agent_id, message)
            self._send_json(result)

        elif path == "/api/events/inject":
            if not STATE.engine:
                self._send_json({"error": "Nenhuma simulação ativa"}, 400)
                return

            title = params.get("title", "Evento")
            desc = params.get("description", "")
            impact = float(params.get("impact", 0.5))
            duration = int(params.get("duration", 3))
            event = STATE.engine.inject_event(
                title,
                desc,
                impact,
                int(params.get("round", STATE.engine.current_round + 1)),
                duration,
            )
            STATE.last_injected_event = {
                "title": title,
                "description": desc,
                "impact": impact,
                "duration": duration,
                "round": STATE.engine.current_round
            }

            # Baixar dados, gerar dataset, buscar artigo base e gerar artigo Qualis A1 em background
            def _download_and_generate_report():
                try:
                    print(f"[EVENT INJECTION] Iniciando coleta de dados e busca acadêmica para '{title}'")
                    from report_generator import ResearchReport  # type: ignore[import-not-found]
                    summary = STATE.last_summary or {
                        "total_agents": len(STATE.engine.agents) if STATE.engine else 0,
                        "total_rounds": STATE.engine.total_rounds if STATE.engine else 0,
                        "total_actions": 0,
                        "avg_sentiment": 0.0,
                        "topic_analysis": {}
                    }
                    report = ResearchReport(summary)
                    report.last_injected_event = STATE.last_injected_event
                    
                    # Baixa os dados e busca as citações (inclusive artigo base)
                    report.collect_data()
                    report.collect_citations()
                    
                    # Deliberação dinâmica do War Room para o novo evento
                    try:
                        from multiagent_warroom import MultiAgentWarRoom  # type: ignore[import-not-found]
                        contexto = {
                            "last_injected_event": STATE.last_injected_event,
                            "stats": getattr(STATE, 'stats', {}),
                            "last_summary": summary,
                            "topic": title
                        }
                        warroom = MultiAgentWarRoom()
                        prob_lower = title.lower()
                        if any(w in prob_lower for w in ["ia", "inteligência artificial", "tecnologia", "tecnológica", "algoritmo", "automação", "digital", "computacional"]):
                            domain = "tecnologia"
                        elif any(w in prob_lower for w in ["renda", "pib", "economia", "econômico", "inflação", "mercado", "emprego", "trabalho", "financeiro", "juros", "desenvolvimento"]):
                            domain = "economia"
                        elif any(w in prob_lower for w in ["crime", "segurança", "violência", "polícia", "pcc", "tráfico", "milícia", "guerra"]):
                            domain = "seguranca"
                        elif any(w in prob_lower for w in ["saúde", "sanitária", "pandemia", "vacina", "médico", "epidemia", "vírus"]):
                            domain = "saude"
                        else:
                            domain = "geral"
                        
                        result = warroom.deliberate(title, domain=domain, simulation_context=contexto)
                        report.warroom_data = result
                        STATE.last_warroom_result = result
                        print(f"[EVENT INJECTION] Deliberação da War Room recalculada dinamicamente para o evento '{title}'")
                    except Exception as wr_err:
                        print(f"[EVENT INJECTION] Erro ao recalcular warroom para o evento: {wr_err}")
                        if hasattr(STATE, 'last_warroom_result'):
                            report.warroom_data = STATE.last_warroom_result
                    
                    if hasattr(STATE, 'last_omen_result'):
                        report.omen_data = STATE.last_omen_result
                        
                    path = report.save()
                    STATE.last_report_path = path
                    STATE.base_article = getattr(report, 'base_article', None)
                    print(f"[EVENT INJECTION] Dataset e Relatório gerados com sucesso em: {path}")
                except Exception as e:
                    print(f"[EVENT INJECTION] Erro ao processar dados/relatório: {e}")
                    import traceback; traceback.print_exc()

            threading.Thread(target=_download_and_generate_report, daemon=True).start()

            self._send_json({
                "status": "injected",
                "event_id": event.id,
                "message": "Evento injetado. Download de dados, busca acadêmica e geração de relatório iniciados em background."
            })

        elif path == "/api/report":
            # Gera em background thread (threading importado no topo do modulo)
            def _gen():
                try:
                    from report_generator import ResearchReport  # type: ignore[import-not-found]
                    summary = STATE.last_summary or {}
                    report = ResearchReport(summary)
                    if hasattr(STATE, 'last_injected_event'):
                        report.last_injected_event = STATE.last_injected_event
                    if hasattr(STATE, 'last_omen_result'):
                        report.omen_data = STATE.last_omen_result
                        
                    # Recalcular warroom dinamicamente se houver dados
                    if hasattr(STATE, 'last_warroom_result') and STATE.last_warroom_result:
                        try:
                            from multiagent_warroom import MultiAgentWarRoom  # type: ignore[import-not-found]
                            problem = STATE.last_warroom_result.get("synthesis", {}).get("problem", "Tema de Pesquisa")
                            contexto = {
                                "last_injected_event": getattr(STATE, 'last_injected_event', None),
                                "stats": getattr(STATE, 'stats', {}),
                                "last_summary": summary,
                                "topic": problem
                            }
                            warroom = MultiAgentWarRoom()
                            result = warroom.deliberate(problem, simulation_context=contexto)
                            report.warroom_data = result
                            STATE.last_warroom_result = result
                            print(f"[REPORT] Deliberação da War Room recalculada com sucesso")
                        except Exception as wr_err:
                            print(f"[REPORT] Erro ao recalcular warroom dinâmico: {wr_err}")
                            report.warroom_data = STATE.last_warroom_result
                    elif hasattr(STATE, 'last_warroom_result'):
                        report.warroom_data = STATE.last_warroom_result
                        
                    path = report.save()
                    STATE.last_report_path = path
                    print(f"[REPORT] Relatório salvo: {path}")
                except Exception as e:
                    print(f"[REPORT] Erro: {e}")
                    import traceback; traceback.print_exc()
            threading.Thread(target=_gen, daemon=True).start()
            self._send_json({
                "status": "generated",
                "report_url": "/api/report/view",
                "message": "Relatório sendo gerado em background. Consulte /api/report/view quando concluído."
            })

        elif path == "/api/report/view":
            report_path = getattr(STATE, 'last_report_path', None)
            if report_path and os.path.exists(report_path):
                with open(report_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/markdown; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(content.encode())
            else:
                self._send_json({"error": "Nenhum relatório gerado ainda. Execute uma simulação primeiro."}, 404)

        elif path == "/api/whatsapp/parse":
            chat_text = params.get("chat_text", "")
            if not chat_text:
                self._send_json({"error": "Texto do chat vazio"}, 400)
                return
            try:
                sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "..", "..", "data-collector", "scripts"))
                sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "..", "..", "simulation-runner", "scripts"))
                from whatsapp_profiler import WhatsAppProfiler  # type: ignore[import-not-found]
                from profile_manager import get_profile_manager  # type: ignore[import-not-found]

                profiler = WhatsAppProfiler()
                profiler.parse_chat(chat_text)
                profiles = profiler.build_profiles()
                sim_agents = profiler.to_sim_agents()
                group_stats = profiler.group_stats

                # Mapeamento para perfis psicológicos expandidos
                expanded_mapping = profiler.map_to_expanded_profiles()

                # Salvar TODOS os perfis no banco unificado
                pm = get_profile_manager()
                saved = pm.import_whatsapp_profiles(profiles)
                total = pm.count()

                # Salvar também no STATE para uso imediato
                STATE.wa_sim_agents = sim_agents
                STATE.wa_profiles = profiles

                self._send_json({
                    "profiles": profiles, "sim_agents": sim_agents,
                    "group_stats": group_stats,
                    "expanded_mapping": expanded_mapping,
                    "profile_count": len(profiles),
                    "message_count": len(profiler.messages),
                    "saved_to_db": saved,
                    "total_profiles_db": total,
                    "status": "parsed"
                })
            except Exception as e:
                self._send_json({"error": f"Erro ao processar chat: {str(e)}"}, 500)

        elif path == "/api/research":
            topic = params.get("topic", "Pesquisa sem titulo")
            def _research():
                try:
                    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "..", "simulation-runner", "scripts"))
                    from mirofish_omni import omni_research  # type: ignore[import-not-found]
                    result = omni_research(topic, last_injected_event=getattr(STATE, 'last_injected_event', None))
                    STATE.last_omni_result = result
                except Exception as e:
                    STATE.last_omni_result = {"error": str(e), "topic": topic}
            threading.Thread(target=_research, daemon=True).start()
            self._send_json({"status": "started", "topic": topic,
                "message": f"Pesquisa iniciada: {topic}. Aguarde ~5s e consulte /api/research/status"})

        elif path == "/api/research/status":
            result = getattr(STATE, 'last_omni_result', None)
            if result:
                self._send_json(result)
            else:
                self._send_json({"status": "running", "message": "Pesquisa em andamento..."})

        elif path == "/api/warroom":
            problem = params.get("problem", "Tema não especificado")
            try:
                sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "..", "..", "simulation-runner", "scripts"))
                from multiagent_warroom import MultiAgentWarRoom  # type: ignore[import-not-found]
                contexto = {
                    "last_injected_event": getattr(STATE, 'last_injected_event', None),
                    "stats": getattr(STATE, 'stats', {}),
                    "last_summary": getattr(STATE, 'last_summary', {}),
                    "topic": problem
                }
                warroom = MultiAgentWarRoom()
                result = warroom.deliberate(problem, simulation_context=contexto)
                STATE.last_warroom_result = result
                
                # --- Retroalimentação Autônoma com Prevenção de Duplicados ---
                if getattr(STATE, 'engine', None) and getattr(STATE, 'simulation_running', False):
                    synth = result.get("synthesis", {})
                    rec = synth.get("recommendation", "")
                    if rec:
                        title_evt = "Diretriz Estratégica (War Room)"
                        already_active = any(
                            e.title == title_evt and e.round_injected + e.duration_rounds > STATE.engine.current_round
                            for e in STATE.engine.events
                        )
                        if not already_active:
                            try:
                                STATE.engine.inject_event(
                                    title=title_evt,
                                    description=rec[:255],
                                    impact=0.6 if synth.get("consensus_level", "Baixo") in ["Alto", "Muito Alto"] else 0.3,
                                    round_num=STATE.engine.current_round + 1,
                                    duration=5
                                )
                                print("[WAR ROOM] Retroalimentação Autônoma injetada com sucesso na simulação.")
                            except Exception as e:
                                print(f"[WAR ROOM] Falha na Retroalimentação Autônoma: {e}")
                        else:
                            print("[WAR ROOM] Ignorando injeção de diretriz: diretriz anterior já ativa.")
                # -------------------------------------------------------------
                
                self._send_json(result)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)

        elif path == "/api/omen/predict":
            try:
                sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "..", "..", "simulation-runner", "scripts"))
                from omen_engine import OmenPredictionEngine, ForecastEngine, FORECAST_REFERENCES  # type: ignore[import-not-found]
                import random, math

                engine = OmenPredictionEngine()
                result = engine.predict_all()

                # G3: Usar dados REAIS da simulação para previsões
                sim_data = STATE.last_summary or {}
                topic_analysis = sim_data.get("topic_analysis", {})

                fe = ForecastEngine()
                for scenario_key, pred in result.get("predictions", {}).items():
                    config = engine.scenarios.get(scenario_key, {})

                    # Buscar séries reais dos tópicos relacionados ao cenário
                    real_values = None
                    for var_key in config.get("variables", [])[:3]:
                        for t, d in topic_analysis.items():
                            evol = d.get("evolution", [])
                            if evol and len(evol) >= 8:
                                real_values = [e["mean"] for e in evol]
                                break
                        if real_values:
                            break

                    if real_values and len(real_values) >= 5:
                        values = real_values
                        pred["_used_fallback"] = False
                    else:
                        # Fallback: sintético calibrado
                        trends = {"recessao_global": -0.04, "inflacao_crise": 0.03, "pandemia_global": -0.05}
                        trend = trends.get(scenario_key, 0)
                        values = [100 + i*trend + 8*math.sin(i*0.4) + random.gauss(0,2) for i in range(20)]
                        pred["_used_fallback"] = True

                    dated = fe.forecast_series(values, len(values)//2, "rodada")

                    # Garantir defaults para evitar undefined
                    pred["forecast_table"] = dated.get("forecast_table", [])
                    pred["forecast_stats"] = dated.get("forecast_stats", {"last_value":0,"horizon_end_value":0,"total_change_pct":0,"avg_margin_of_error":0,"max_margin_of_error":0})
                    pred["forecast_metrics"] = dated.get("metrics", {"mae":0,"rmse":0,"mape_percent":0,"r_squared":0,"interpretation":"N/A"})
                    pred["decomposition"] = dated.get("decomposition", {})
                    
                    # --- Cálculos Reversa ---
                    n_inferred = len(pred["forecast_table"])
                    n_hist = len(values)
                    if pred["_used_fallback"]:
                        confirmed = 0
                        gaps = n_hist
                        inferred = n_inferred
                        gap_list = [f"Dado histórico ausente, usando fallback sintético calibrado."]
                    else:
                        confirmed = n_hist
                        gaps = 0
                        inferred = n_inferred
                        gap_list = []
                    total_claims = confirmed + inferred + gaps
                    pred["confidence_score"] = round(((confirmed + 0.5 * inferred) / max(total_claims, 1)) * 100, 1)
                    pred["gaps_detected"] = gap_list
                    
                    # Rastreabilidade
                    try:
                        from omen_engine import REAL_VARIABLES, ETHNIC_DIMENSIONS  # type: ignore[import-not-found]
                        var_metadata = {}
                        for dom, v_dict in REAL_VARIABLES.items():
                            for k, v in v_dict.items():
                                var_metadata[f"{dom}.{k}"] = v
                        for k, v in ETHNIC_DIMENSIONS.items():
                            var_metadata[f"ethnic.{k}"] = v
                    except:
                        var_metadata = {}
                        
                    raw_vars = config.get("variables", [])
                    traceability_list = []
                    for v_key in raw_vars:
                        meta = var_metadata.get(v_key, {})
                        traceability_list.append({
                            "variable": v_key,
                            "label": meta.get("label", v_key),
                            "source": meta.get("source", "Simulação Interna")
                        })
                    pred["traceability"] = traceability_list

                    # Garantir fields para frontend
                    pred["_nations_analyzed"] = pred.get("nations_analyzed", [])
                    pred["_risk_factors"] = pred.get("risk_factors", [])
                    pred["_advantage_factors"] = pred.get("advantage_factors", [])
                    pred["_category"] = pred.get("category", "geral")
                    pred["_risk_level"] = pred.get("risk_level", "MEDIO")
                    pred["_recommendation"] = pred.get("recommendation", "")

                result["forecast_references"] = FORECAST_REFERENCES[:5]
                result["generated_at"] = datetime.now(timezone(timedelta(hours=-3))).isoformat()
                STATE.last_omen_result = result
                
                # --- Serialização Vetorial ---
                threading.Thread(target=save_omen_prediction, args=(result,), daemon=True).start()
                # ------------------------------
                
                self._send_json(result)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)

        elif path == "/api/whatsapp/apply":
            agents = params.get("agents") or getattr(STATE, 'wa_sim_agents', None)
            if not agents:
                self._send_json({"error": "Nenhum perfil carregado"}, 400)
                return
            try:
                if STATE.engine:
                    for agent_data in agents:
                        STATE.engine.create_agent(
                            agent_data.get("name", "WA_Agent"),
                            agent_data
                        )
                    self._send_json({"status": "applied", "count": len(agents),
                        "message": f"{len(agents)} agentes WhatsApp adicionados a simulacao"})
                else:
                    # Salva para quando a simulação iniciar
                    calib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "..", "..", ".reversa", "whatsapp_calibration.json")
                    os.makedirs(os.path.dirname(calib_path), exist_ok=True)
                    with open(calib_path, "w", encoding="utf-8") as f:
                        json.dump({"agents": agents}, f, indent=2, ensure_ascii=False)
                    self._send_json({"status": "saved", "count": len(agents),
                        "message": f"{len(agents)} perfis salvos. Inicie a simulacao."})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)

        else:
            self._send_json({"error": "Not found"}, 404)

    def do_OPTIONS(self):
        try:
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
            pass


# ═══════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════

def main():
    import argparse, random
    parser = argparse.ArgumentParser(description="MiroFish Local Server")
    parser.add_argument("--port", type=int, default=8765, help="Porta (default: 8765)")
    parser.add_argument("--browser", action="store_true", help="Abrir navegador")
    args = parser.parse_args()

    # SO_REUSEADDR no Windows não evita conflito imediato;
    # usamos allow_reuse_address e tratamos o erro explicitamente.
    try:
        server = http.server.ThreadingHTTPServer(("0.0.0.0", args.port), MiroFishHandler)
        server.allow_reuse_address = True
    except OSError as e:
        wcode = getattr(e, 'winerror', None)
        if wcode in (10048,) or 'address' in str(e).lower():
            print(f"\n\u274c Porta {args.port} já está em uso!")
            print(f"   Descubra o PID com:")
            print(f"   netstat -ano | findstr :{args.port}")
            print(f"   Depois mate APENAS esse processo:")
            print(f"   taskkill /PID <PID> /F")
            print(f"   (não mate todos os Python — isso afeta o OpenCode)")
        else:
            print(f"\n❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)

    print("═" * 60)
    print("🐟  MIROFISH LOCAL SERVER — OpenCode Ecosystem v4.2")
    print("═" * 60)
    print(f"   Local:    http://localhost:{args.port}")
    print(f"   API:      http://localhost:{args.port}/api/status")
    print(f"   SSE:      http://localhost:{args.port}/events")
    print(f"   Agents:   http://localhost:{args.port}/api/agents")
    print(f"   Chat:     POST http://localhost:{args.port}/api/chat")

    # ── Pre-load default agents for immediate chat ──
    try:
        from sim_engine import SimulationEngine  # type: ignore[import-not-found]
        engine = SimulationEngine(name="MiroFish_Local", db_path=".reversa/mirofish_local.db")
        profiles = [
            {"name": "Ministro da Fazenda", "labels": ["Official"],
             "activity_config": {"activity_level": 0.3, "influence_weight": 3.0, "stance": "supportive", "sentiment_bias": 0.2, "posts_per_hour": 0.3}},
            {"name": "Presidente do BC", "labels": ["Official"],
             "activity_config": {"activity_level": 0.2, "influence_weight": 2.8, "stance": "neutral", "posts_per_hour": 0.2}},
            {"name": "CEO Startup IA", "labels": ["Person"],
             "activity_config": {"activity_level": 0.7, "influence_weight": 2.0, "stance": "supportive", "sentiment_bias": 0.5, "posts_per_hour": 1.5}},
            {"name": "Sindicalista CUT", "labels": ["Person"],
             "activity_config": {"activity_level": 0.8, "influence_weight": 1.5, "stance": "critical", "sentiment_bias": -0.3, "posts_per_hour": 2.0}},
            {"name": "Pesquisador Unicamp", "labels": ["Professor"],
             "activity_config": {"activity_level": 0.5, "influence_weight": 2.2, "stance": "curious", "sentiment_bias": 0.1, "posts_per_hour": 0.8}},
            {"name": "Jornalista Econômico", "labels": ["MediaOutlet"],
             "activity_config": {"activity_level": 0.8, "influence_weight": 2.5, "stance": "neutral", "sentiment_bias": 0, "posts_per_hour": 3.0}},
            {"name": "Empresário do Agro", "labels": ["Person"],
             "activity_config": {"activity_level": 0.6, "influence_weight": 1.8, "stance": "supportive", "sentiment_bias": 0.3, "posts_per_hour": 1.0}},
            {"name": "Ambientalista da Amazônia", "labels": ["Person", "Environment"],
             "activity_config": {"activity_level": 0.9, "influence_weight": 2.0, "stance": "critical", "sentiment_bias": -0.5, "posts_per_hour": 2.5}},
        ]
        engine.create_agents_from_profiles(profiles)
        STATE.engine = engine
        print(f"   🤖 {len(engine.agents)} agentes pré-carregados para chat imediato")
    except Exception as e:
        print(f"   ⚠️ Agentes pré-carregados indisponíveis: {e}")
    print(f"   Timezone: BRAZIL (UTC-3)")
    print(f"   DB:       .reversa/mirofish_local.db")
    print(f"   Modelo:   opencode/big-pickle (via Agent Forum)")
    print(f"   Zero dependências externas — Python stdlib only")
    print(f"\n   Pressione Ctrl+C para parar")
    print("═" * 60)

    if args.browser:
        import webbrowser
        threading.Timer(1.0, lambda: webbrowser.open(f"http://localhost:{args.port}")).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Servidor encerrado.")
        server.shutdown()


if __name__ == "__main__":
    main()
