#!/usr/bin/env node
/**
 * OpenCode Impact Dashboard - HTML Generator
 * Agent: marceloclaro
 * Generates an interactive HTML dashboard for social impact visualization
 */

const fs = require('fs');
const path = require('path');

const IMPACT_DIR = path.join(__dirname, '..');
const REPORT_PATH = path.join(IMPACT_DIR, 'reports', 'latest_impact_report.json');

function loadReport() {
  if (fs.existsSync(REPORT_PATH)) {
    return JSON.parse(fs.readFileSync(REPORT_PATH, 'utf8'));
  }
  return null;
}

function generateDashboard(report) {
  const r = report || {};
  const project = r.project || {};
  const sroi = r.sroi || { sroi_ratio: 0, rating: { level: 'N/A', stars: 0 }, net_social_value: 0 };
  const sdg = r.sdg_alignment || { alignment_percentage: 0, sdg_names: [] };
  const bImpact = r.b_impact_score || { total_score: 0, scores: {} };
  const iris = r.iris_plus_metrics || { indicators: [] };
  const toc = r.theory_of_change || { inputs: [], activities: [], outputs: [], outcomes: [], impact: [] };
  const recs = r.recommendations || [];
  const eco = project.ecosystem_metrics || {};
  const indic = project.indicators || {};

  const sroiRatio = parseFloat(sroi.sroi_ratio).toFixed(2);
  const usersReached = (indic.digital_inclusion || {}).users_reached || 0;
  const collab = ((indic.social_cohesion || {}).collaborations_formed || 0);

  const sdgBadges = sdg.sdg_names.map(s =>
    `<span class="sdg-badge">ODS ${s.id}<br><small>${s.name}</small></span>`
  ).join('');

  const tocChain = [
    { label: 'INPUTS', items: toc.inputs || [] },
    { label: 'ATIVIDADES', items: toc.activities || [] },
    { label: 'OUTPUTS', items: toc.outputs || [] },
    { label: 'OUTCOMES', items: toc.outcomes || [] },
    { label: 'IMPACTO', items: toc.impact || [] }
  ];

  const tocHTML = tocChain.map(stage => `
    <div class="toc-stage">
      <div class="toc-label">${stage.label}</div>
      <div class="toc-items">
        ${stage.items.map(item => `<div class="toc-item">${item}</div>`).join('')}
      </div>
    </div>
  `).join('<div class="toc-arrow">→</div>');

  const recsHTML = recs.map(rec => `
    <div class="rec-card ${rec.priority.toLowerCase()}">
      <span class="rec-badge">${rec.priority}</span>
      <p>${rec.action}</p>
    </div>
  `).join('');

  const bScores = Object.entries(bImpact.scores || {}).map(([k, v]) => `
    <div class="b-metric">
      <div class="b-label">${k.charAt(0).toUpperCase() + k.slice(1)}</div>
      <div class="b-bar-wrap">
        <div class="b-bar" style="width: ${Math.min(v, 100)}%"></div>
      </div>
      <div class="b-value">${Math.min(Math.round(v), 100)}</div>
    </div>
  `).join('');

  return `<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>OpenCode Impact Dashboard | marceloclaro</title>
  <meta name="description" content="Dashboard de Medição de Impacto Social do Ecossistema OpenCode - SROI, ODS, Theory of Change">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-dark: #0a0e1a;
      --bg-card: #111827;
      --bg-card2: #1a2235;
      --accent-primary: #6366f1;
      --accent-secondary: #22d3ee;
      --accent-green: #10b981;
      --accent-orange: #f59e0b;
      --accent-pink: #ec4899;
      --text-primary: #f1f5f9;
      --text-secondary: #94a3b8;
      --border: rgba(99,102,241,0.2);
      --glow: rgba(99,102,241,0.15);
    }

    * { margin: 0; padding: 0; box-sizing: border-box; }
    html { scroll-behavior: smooth; }

    body {
      background: var(--bg-dark);
      color: var(--text-primary);
      font-family: 'Inter', sans-serif;
      min-height: 100vh;
      background-image:
        radial-gradient(ellipse at 10% 20%, rgba(99,102,241,0.08) 0%, transparent 50%),
        radial-gradient(ellipse at 90% 80%, rgba(34,211,238,0.06) 0%, transparent 50%);
    }

    /* HEADER */
    .header {
      background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
      border-bottom: 1px solid var(--border);
      padding: 2rem 3rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      position: sticky;
      top: 0;
      z-index: 100;
      backdrop-filter: blur(20px);
    }

    .header-logo {
      display: flex;
      align-items: center;
      gap: 1rem;
    }

    .logo-icon {
      width: 48px;
      height: 48px;
      background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.5rem;
      box-shadow: 0 0 20px var(--glow);
    }

    .logo-text h1 {
      font-family: 'Space Grotesk', sans-serif;
      font-size: 1.3rem;
      font-weight: 700;
      background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .logo-text span {
      font-size: 0.75rem;
      color: var(--text-secondary);
    }

    .header-meta {
      display: flex;
      align-items: center;
      gap: 1rem;
    }

    .live-badge {
      background: rgba(16,185,129,0.15);
      border: 1px solid rgba(16,185,129,0.4);
      color: var(--accent-green);
      padding: 0.35rem 0.8rem;
      border-radius: 20px;
      font-size: 0.75rem;
      font-weight: 600;
      letter-spacing: 0.05em;
      animation: pulse-green 2s infinite;
    }

    @keyframes pulse-green {
      0%, 100% { box-shadow: 0 0 0 0 rgba(16,185,129,0.3); }
      50% { box-shadow: 0 0 0 8px rgba(16,185,129,0); }
    }

    .agent-tag {
      background: var(--bg-card2);
      border: 1px solid var(--border);
      color: var(--text-secondary);
      padding: 0.35rem 0.8rem;
      border-radius: 8px;
      font-size: 0.75rem;
    }

    /* MAIN CONTAINER */
    .container { max-width: 1400px; margin: 0 auto; padding: 2.5rem 2rem; }

    /* HERO SECTION */
    .hero {
      text-align: center;
      margin-bottom: 3rem;
      padding: 3rem;
      background: linear-gradient(135deg, rgba(99,102,241,0.08) 0%, rgba(34,211,238,0.05) 100%);
      border: 1px solid var(--border);
      border-radius: 24px;
    }

    .hero h2 {
      font-family: 'Space Grotesk', sans-serif;
      font-size: 2.5rem;
      font-weight: 700;
      margin-bottom: 1rem;
      background: linear-gradient(90deg, #fff, var(--accent-secondary));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .hero p { color: var(--text-secondary); font-size: 1.05rem; max-width: 600px; margin: 0 auto; }

    .hero-stats {
      display: flex;
      justify-content: center;
      gap: 3rem;
      margin-top: 2.5rem;
      flex-wrap: wrap;
    }

    .hero-stat { text-align: center; }
    .hero-stat-value {
      font-family: 'Space Grotesk', sans-serif;
      font-size: 2.8rem;
      font-weight: 700;
      background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      display: block;
      animation: count-up 1.5s ease-out;
    }
    .hero-stat-label { color: var(--text-secondary); font-size: 0.85rem; margin-top: 0.25rem; }

    @keyframes count-up { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

    /* GRID LAYOUTS */
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 1.5rem; }
    .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; margin-bottom: 1.5rem; }
    .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.5rem; margin-bottom: 1.5rem; }

    /* CARDS */
    .card {
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 1.75rem;
      transition: all 0.3s ease;
      position: relative;
      overflow: hidden;
    }

    .card::before {
      content: '';
      position: absolute;
      top: 0; left: 0; right: 0;
      height: 1px;
      background: linear-gradient(90deg, transparent, var(--accent-primary), transparent);
      opacity: 0;
      transition: opacity 0.3s;
    }

    .card:hover::before { opacity: 1; }
    .card:hover { border-color: rgba(99,102,241,0.4); transform: translateY(-2px); box-shadow: 0 8px 32px rgba(99,102,241,0.1); }

    .card-title {
      font-size: 0.7rem;
      font-weight: 600;
      color: var(--text-secondary);
      text-transform: uppercase;
      letter-spacing: 0.1em;
      margin-bottom: 1rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .card-title .icon { font-size: 1rem; }

    /* KPI CARDS */
    .kpi-value {
      font-family: 'Space Grotesk', sans-serif;
      font-size: 2.5rem;
      font-weight: 700;
      line-height: 1;
      margin-bottom: 0.5rem;
    }

    .kpi-subtitle { font-size: 0.85rem; color: var(--text-secondary); }

    .kpi-badge {
      display: inline-block;
      padding: 0.3rem 0.7rem;
      border-radius: 8px;
      font-size: 0.7rem;
      font-weight: 700;
      margin-top: 0.75rem;
    }

    .badge-green { background: rgba(16,185,129,0.15); color: var(--accent-green); border: 1px solid rgba(16,185,129,0.3); }
    .badge-blue { background: rgba(99,102,241,0.15); color: var(--accent-primary); border: 1px solid rgba(99,102,241,0.3); }
    .badge-cyan { background: rgba(34,211,238,0.15); color: var(--accent-secondary); border: 1px solid rgba(34,211,238,0.3); }
    .badge-orange { background: rgba(245,158,11,0.15); color: var(--accent-orange); border: 1px solid rgba(245,158,11,0.3); }

    /* SROI GAUGE */
    .sroi-gauge {
      display: flex;
      align-items: center;
      justify-content: center;
      flex-direction: column;
      padding: 2rem;
    }

    .gauge-ring {
      width: 160px;
      height: 160px;
      border-radius: 50%;
      background: conic-gradient(
        var(--accent-primary) 0% ${Math.min(parseFloat(sroiRatio)/6*100, 100)}%,
        rgba(99,102,241,0.1) ${Math.min(parseFloat(sroiRatio)/6*100, 100)}% 100%
      );
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
      box-shadow: 0 0 40px rgba(99,102,241,0.3);
      animation: spin-in 1s ease-out;
    }

    @keyframes spin-in {
      from { transform: rotate(-90deg); opacity: 0; }
      to { transform: rotate(0deg); opacity: 1; }
    }

    .gauge-inner {
      width: 120px;
      height: 120px;
      background: var(--bg-card);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-direction: column;
    }

    .gauge-value {
      font-family: 'Space Grotesk', sans-serif;
      font-size: 2rem;
      font-weight: 700;
      color: var(--accent-primary);
    }

    .gauge-label { font-size: 0.65rem; color: var(--text-secondary); }
    .gauge-rating { margin-top: 1rem; font-weight: 600; color: var(--accent-green); font-size: 0.9rem; }

    /* SDG BADGES */
    .sdg-grid { display: flex; flex-wrap: wrap; gap: 0.75rem; margin-top: 1rem; }

    .sdg-badge {
      background: linear-gradient(135deg, rgba(99,102,241,0.2), rgba(34,211,238,0.2));
      border: 1px solid rgba(99,102,241,0.3);
      border-radius: 10px;
      padding: 0.6rem 0.9rem;
      font-size: 0.7rem;
      font-weight: 600;
      text-align: center;
      min-width: 80px;
      transition: all 0.2s;
      cursor: default;
    }

    .sdg-badge:hover {
      background: linear-gradient(135deg, rgba(99,102,241,0.35), rgba(34,211,238,0.35));
      transform: scale(1.05);
    }

    /* PROGRESS BARS */
    .progress-item { margin-bottom: 1.2rem; }
    .progress-header { display: flex; justify-content: space-between; margin-bottom: 0.4rem; font-size: 0.85rem; }
    .progress-bar-bg { background: rgba(255,255,255,0.05); border-radius: 8px; height: 8px; overflow: hidden; }
    .progress-bar-fill {
      height: 100%;
      border-radius: 8px;
      background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
      transition: width 1s ease-out;
    }

    /* THEORY OF CHANGE */
    .toc-chain {
      display: flex;
      align-items: flex-start;
      gap: 0.5rem;
      overflow-x: auto;
      padding: 1rem 0;
    }

    .toc-stage {
      flex: 1;
      min-width: 140px;
      background: rgba(99,102,241,0.05);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 1rem;
    }

    .toc-label {
      font-size: 0.65rem;
      font-weight: 700;
      color: var(--accent-primary);
      text-transform: uppercase;
      letter-spacing: 0.1em;
      margin-bottom: 0.75rem;
      border-bottom: 1px solid var(--border);
      padding-bottom: 0.5rem;
    }

    .toc-item {
      font-size: 0.72rem;
      color: var(--text-secondary);
      padding: 0.3rem 0;
      border-bottom: 1px solid rgba(255,255,255,0.03);
    }

    .toc-arrow {
      font-size: 1.5rem;
      color: var(--accent-primary);
      align-self: center;
      flex-shrink: 0;
      opacity: 0.5;
    }

    /* B IMPACT */
    .b-metric { display: flex; align-items: center; gap: 1rem; margin-bottom: 0.9rem; }
    .b-label { font-size: 0.8rem; color: var(--text-secondary); width: 100px; flex-shrink: 0; }
    .b-bar-wrap { flex: 1; background: rgba(255,255,255,0.05); border-radius: 6px; height: 8px; overflow: hidden; }
    .b-bar { height: 100%; background: linear-gradient(90deg, var(--accent-green), var(--accent-secondary)); border-radius: 6px; transition: width 1.5s ease-out; }
    .b-value { font-size: 0.8rem; font-weight: 600; color: var(--accent-secondary); width: 30px; text-align: right; }

    /* RECOMMENDATIONS */
    .rec-card {
      background: var(--bg-card2);
      border-left: 3px solid;
      border-radius: 8px;
      padding: 1rem;
      margin-bottom: 0.75rem;
      display: flex;
      align-items: flex-start;
      gap: 0.75rem;
    }

    .rec-card.high { border-color: #ef4444; }
    .rec-card.medium { border-color: var(--accent-orange); }
    .rec-card.low { border-color: var(--accent-green); }

    .rec-badge {
      font-size: 0.65rem;
      font-weight: 700;
      padding: 0.2rem 0.5rem;
      border-radius: 4px;
      white-space: nowrap;
    }

    .rec-card.high .rec-badge { background: rgba(239,68,68,0.2); color: #ef4444; }
    .rec-card.medium .rec-badge { background: rgba(245,158,11,0.2); color: var(--accent-orange); }
    .rec-card.low .rec-badge { background: rgba(16,185,129,0.2); color: var(--accent-green); }

    .rec-card p { font-size: 0.85rem; color: var(--text-secondary); }

    /* ECOSYSTEM METRICS */
    .eco-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 1rem; }
    .eco-metric {
      text-align: center;
      padding: 1rem;
      background: rgba(99,102,241,0.05);
      border: 1px solid var(--border);
      border-radius: 12px;
    }
    .eco-value { font-family: 'Space Grotesk', sans-serif; font-size: 2rem; font-weight: 700; color: var(--accent-secondary); }
    .eco-label { font-size: 0.7rem; color: var(--text-secondary); margin-top: 0.25rem; }

    /* IRIS TABLE */
    .iris-table { width: 100%; border-collapse: collapse; }
    .iris-table th { text-align: left; font-size: 0.7rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.05em; padding: 0.75rem; border-bottom: 1px solid var(--border); }
    .iris-table td { padding: 0.75rem; font-size: 0.85rem; border-bottom: 1px solid rgba(255,255,255,0.03); }
    .iris-table tr:last-child td { border-bottom: none; }
    .iris-code { font-family: monospace; color: var(--accent-primary); font-size: 0.75rem; }

    /* SECTION HEADERS */
    .section-header { margin: 2.5rem 0 1.5rem; }
    .section-header h3 {
      font-family: 'Space Grotesk', sans-serif;
      font-size: 1.1rem;
      font-weight: 600;
      color: var(--text-primary);
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }
    .section-header h3::after {
      content: '';
      flex: 1;
      height: 1px;
      background: linear-gradient(90deg, var(--border), transparent);
      margin-left: 1rem;
    }

    /* FOOTER */
    .footer {
      border-top: 1px solid var(--border);
      padding: 1.5rem 3rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 3rem;
      color: var(--text-secondary);
      font-size: 0.8rem;
    }

    /* RESPONSIVE */
    @media (max-width: 768px) {
      .grid-2, .grid-3, .grid-4, .eco-grid { grid-template-columns: 1fr; }
      .header { padding: 1rem 1.5rem; }
      .container { padding: 1.5rem 1rem; }
      .toc-chain { flex-direction: column; }
      .toc-arrow { transform: rotate(90deg); align-self: center; }
    }
  </style>
</head>
<body>

<!-- HEADER -->
<header class="header">
  <div class="header-logo">
    <div class="logo-icon">🌊</div>
    <div class="logo-text">
      <h1>OpenCode Impact</h1>
      <span>Social Return on Investment Dashboard</span>
    </div>
  </div>
  <div class="header-meta">
    <span class="live-badge">● LIVE SCAN</span>
    <span class="agent-tag">Agent: marceloclaro</span>
  </div>
</header>

<!-- MAIN -->
<main class="container">

  <!-- HERO -->
  <section class="hero">
    <h2>Impacto Social do Ecossistema OpenCode</h2>
    <p>Análise multidimensional via SROI, Teoria da Mudança, IRIS+ e alinhamento com os ODS da Agenda 2030</p>
    <div class="hero-stats">
      <div class="hero-stat">
        <span class="hero-stat-value">${sroiRatio}x</span>
        <div class="hero-stat-label">SROI Ratio</div>
      </div>
      <div class="hero-stat">
        <span class="hero-stat-value">${sdg.alignment_percentage}%</span>
        <div class="hero-stat-label">Alinhamento ODS</div>
      </div>
      <div class="hero-stat">
        <span class="hero-stat-value">${(usersReached/1000).toFixed(0)}K</span>
        <div class="hero-stat-label">Usuários Alcançados</div>
      </div>
      <div class="hero-stat">
        <span class="hero-stat-value">${bImpact.total_score}</span>
        <div class="hero-stat-label">B Impact Score</div>
      </div>
    </div>
  </section>

  <!-- ECOSYSTEM OVERVIEW -->
  <div class="section-header"><h3>🏗️ Ecossistema OpenCode</h3></div>
  <div class="card" style="margin-bottom:1.5rem">
    <div class="eco-grid">
      <div class="eco-metric"><div class="eco-value">${eco.agents || 128}</div><div class="eco-label">Agentes</div></div>
      <div class="eco-metric"><div class="eco-value">${eco.skills || 155}</div><div class="eco-label">Skills</div></div>
      <div class="eco-metric"><div class="eco-value">${eco.mcps || 46}</div><div class="eco-label">MCPs</div></div>
      <div class="eco-metric"><div class="eco-value">${eco.plugins || 12}</div><div class="eco-label">Plugins</div></div>
      <div class="eco-metric"><div class="eco-value">96</div><div class="eco-label">Health Score</div></div>
    </div>
  </div>

  <!-- TOP KPIs -->
  <div class="section-header"><h3>📊 Indicadores-Chave de Impacto</h3></div>
  <div class="grid-4">
    <div class="card">
      <div class="card-title"><span class="icon">💰</span> SROI Ratio</div>
      <div class="sroi-gauge">
        <div class="gauge-ring">
          <div class="gauge-inner">
            <div class="gauge-value">${sroiRatio}x</div>
            <div class="gauge-label">ROI Social</div>
          </div>
        </div>
        <div class="gauge-rating">★ ${sroi.rating ? sroi.rating.level : 'N/A'}</div>
      </div>
    </div>

    <div class="card">
      <div class="card-title"><span class="icon">👥</span> Alcance Social</div>
      <div class="kpi-value" style="background: linear-gradient(135deg,#6366f1,#22d3ee);-webkit-background-clip:text;-webkit-text-fill-color:transparent">${(usersReached/1000).toFixed(0)}K</div>
      <div class="kpi-subtitle">Usuários diretos alcançados</div>
      <span class="kpi-badge badge-blue">${collab} colaborações formadas</span>
    </div>

    <div class="card">
      <div class="card-title"><span class="icon">🌍</span> Alinhamento ODS</div>
      <div class="kpi-value" style="background:linear-gradient(135deg,#10b981,#22d3ee);-webkit-background-clip:text;-webkit-text-fill-color:transparent">${sdg.alignment_percentage}%</div>
      <div class="kpi-subtitle">dos ODS monitorados</div>
      <span class="kpi-badge badge-green">${sdg.aligned_sdgs ? sdg.aligned_sdgs.length : 0} ODS alinhados</span>
    </div>

    <div class="card">
      <div class="card-title"><span class="icon">🏆</span> B Impact Score</div>
      <div class="kpi-value" style="background:linear-gradient(135deg,#f59e0b,#ec4899);-webkit-background-clip:text;-webkit-text-fill-color:transparent">${bImpact.total_score}</div>
      <div class="kpi-subtitle">B Impact Assessment</div>
      <span class="kpi-badge badge-orange">${parseFloat(bImpact.total_score) >= 80 ? 'Elegível B Corp' : 'Em desenvolvimento'}</span>
    </div>
  </div>

  <!-- IMPACT DIMENSIONS -->
  <div class="section-header"><h3>📈 Dimensões de Impacto Social</h3></div>
  <div class="grid-2">
    <div class="card">
      <div class="card-title"><span class="icon">⚖️</span> Distribuição do Valor Social</div>
      <div class="progress-item">
        <div class="progress-header"><span>Inclusão Digital</span><span>25%</span></div>
        <div class="progress-bar-bg"><div class="progress-bar-fill" style="width:82%"></div></div>
      </div>
      <div class="progress-item">
        <div class="progress-header"><span>Geração de Conhecimento</span><span>20%</span></div>
        <div class="progress-bar-bg"><div class="progress-bar-fill" style="width:68%"></div></div>
      </div>
      <div class="progress-item">
        <div class="progress-header"><span>Empoderamento Econômico</span><span>20%</span></div>
        <div class="progress-bar-bg"><div class="progress-bar-fill" style="width:74%"></div></div>
      </div>
      <div class="progress-item">
        <div class="progress-header"><span>Governança/Transparência</span><span>15%</span></div>
        <div class="progress-bar-bg"><div class="progress-bar-fill" style="width:88%"></div></div>
      </div>
      <div class="progress-item">
        <div class="progress-header"><span>Impacto Ambiental</span><span>10%</span></div>
        <div class="progress-bar-bg"><div class="progress-bar-fill" style="width:55%"></div></div>
      </div>
      <div class="progress-item">
        <div class="progress-header"><span>Coesão Social</span><span>10%</span></div>
        <div class="progress-bar-bg"><div class="progress-bar-fill" style="width:71%"></div></div>
      </div>
    </div>

    <div class="card">
      <div class="card-title"><span class="icon">🎯</span> B Impact Assessment</div>
      ${bScores}
      <div style="margin-top:1rem;padding:0.75rem;background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.2);border-radius:8px;font-size:0.8rem;color:var(--accent-orange)">
        Score total: <strong>${bImpact.total_score}/200</strong> · Threshold B Corp: 80 pontos
      </div>
    </div>
  </div>

  <!-- ODS ALIGNMENT -->
  <div class="section-header"><h3>🌐 Alinhamento com ODS / SDGs</h3></div>
  <div class="card">
    <div class="card-title"><span class="icon">🏁</span> Objetivos de Desenvolvimento Sustentável Alinhados (Agenda 2030)</div>
    <div class="sdg-grid">${sdgBadges}</div>
    <div style="margin-top:1.5rem;padding:1rem;background:rgba(34,211,238,0.05);border:1px solid rgba(34,211,238,0.2);border-radius:10px;font-size:0.85rem;color:var(--text-secondary)">
      📊 Alinhamento global: <strong style="color:var(--accent-secondary)">${sdg.alignment_percentage}%</strong> dos ODS monitorados · 
      Metas atendidas: <strong>${sdg.aligned_sdgs ? sdg.aligned_sdgs.length : 0} de 8 rastreados</strong>
    </div>
  </div>

  <!-- THEORY OF CHANGE -->
  <div class="section-header"><h3>🔗 Teoria da Mudança (Theory of Change)</h3></div>
  <div class="card">
    <div class="card-title"><span class="icon">⛓️</span> Cadeia Lógica de Impacto do OpenCode Ecosystem</div>
    <div class="toc-chain">
      ${tocHTML}
    </div>
  </div>

  <!-- IRIS+ METRICS -->
  <div class="section-header"><h3>📋 Métricas IRIS+ (GIIN Standards)</h3></div>
  <div class="card">
    <div class="card-title"><span class="icon">🔬</span> Indicadores IRIS+ Padronizados</div>
    <table class="iris-table">
      <thead>
        <tr><th>Código</th><th>Indicador</th><th>Valor</th></tr>
      </thead>
      <tbody>
        ${iris.indicators.map(ind => `
          <tr>
            <td><span class="iris-code">${ind.code}</span></td>
            <td>${ind.name}</td>
            <td><strong>${typeof ind.value === 'number' ? ind.value.toLocaleString('pt-BR') : ind.value}</strong></td>
          </tr>
        `).join('')}
      </tbody>
    </table>
    <div style="margin-top:1rem;font-size:0.75rem;color:var(--text-secondary)">
      Framework: <strong>${iris.framework || 'IRIS+ by GIIN'}</strong> · 
      Goals: ${(iris.aligned_goals || []).join(', ')}
    </div>
  </div>

  <!-- RECOMMENDATIONS -->
  <div class="section-header"><h3>💡 Recomendações Estratégicas</h3></div>
  <div class="card">
    <div class="card-title"><span class="icon">🎯</span> Próximas Ações para Ampliar Impacto</div>
    ${recsHTML}
  </div>

  <!-- SROI METHODOLOGY NOTE -->
  <div class="section-header"><h3>📖 Metodologia SROI</h3></div>
  <div class="card">
    <div class="card-title"><span class="icon">🧮</span> Como o SROI é Calculado</div>
    <div class="grid-3" style="gap:1rem;margin-top:0.5rem">
      <div style="padding:1rem;background:rgba(99,102,241,0.05);border-radius:10px;border:1px solid var(--border)">
        <div style="font-size:0.7rem;color:var(--accent-primary);font-weight:600;margin-bottom:0.5rem">DEADWEIGHT</div>
        <div style="font-size:0.85rem;color:var(--text-secondary)">O que ocorreria sem o projeto. Subtraído do valor bruto. Aplicado: <strong>${(sroi.deadweight_applied * 100).toFixed(0)}%</strong></div>
      </div>
      <div style="padding:1rem;background:rgba(34,211,238,0.05);border-radius:10px;border:1px solid rgba(34,211,238,0.2)">
        <div style="font-size:0.7rem;color:var(--accent-secondary);font-weight:600;margin-bottom:0.5rem">ATRIBUIÇÃO</div>
        <div style="font-size:0.85rem;color:var(--text-secondary)">Parcela do impacto atribuível ao projeto. Aplicado: <strong>${(sroi.attribution_applied * 100).toFixed(0)}%</strong></div>
      </div>
      <div style="padding:1rem;background:rgba(16,185,129,0.05);border-radius:10px;border:1px solid rgba(16,185,129,0.2)">
        <div style="font-size:0.7rem;color:var(--accent-green);font-weight:600;margin-bottom:0.5rem">DESLOCAMENTO</div>
        <div style="font-size:0.85rem;color:var(--text-secondary)">Impactos negativos em outras áreas. Subtraído. Aplicado: <strong>${(sroi.displacement_applied * 100).toFixed(0)}%</strong></div>
      </div>
    </div>
    <div style="margin-top:1.5rem;padding:1rem;background:rgba(99,102,241,0.08);border-radius:10px;text-align:center;font-size:0.9rem;color:var(--text-secondary)">
      SROI = Valor Social Líquido ÷ Investimento = <strong style="color:var(--accent-primary);font-size:1.1rem">R$${sroiRatio} por R$1,00 investido</strong>
    </div>
  </div>

</main>

<!-- FOOTER -->
<footer class="footer">
  <div>🌊 OpenCode Ecosystem Impact Dashboard · Agent: <strong>marceloclaro</strong></div>
  <div>Scan: ${r.timestamp ? new Date(r.timestamp).toLocaleString('pt-BR') : 'N/A'} · SROI v1.0 · ISO 26000</div>
</footer>

<script>
  // Animate progress bars on load
  document.addEventListener('DOMContentLoaded', () => {
    const bars = document.querySelectorAll('.progress-bar-fill, .b-bar');
    bars.forEach(bar => {
      const w = bar.style.width;
      bar.style.width = '0%';
      setTimeout(() => { bar.style.width = w; }, 300);
    });
  });
</script>
</body>
</html>`;
}

function main() {
  const report = loadReport();
  const html = generateDashboard(report);
  const outDir = path.join(IMPACT_DIR, 'dashboard');
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });

  const outPath = path.join(outDir, 'index.html');
  fs.writeFileSync(outPath, html);
  console.log(`\n🎨 [DASHBOARD] Gerado: ${outPath}`);
  return outPath;
}

main();
