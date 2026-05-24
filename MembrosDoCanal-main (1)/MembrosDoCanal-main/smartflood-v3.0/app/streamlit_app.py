# streamlit_app.py — SmartFlood v4.7
import os, sys, json, time, random, joblib, math
from pathlib import Path
from datetime import datetime, timedelta

import numpy as np
import streamlit as st
import pandas as pd
import pydeck as pdk
from shapely.geometry import Point, mapping
from shapely.ops import transform
import pyproj

from streamlit_folium import st_folium
import folium

# --- import simulador
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sim.simulator import RainSoilDrainSimulator

# ------------------ CONFIG BÁSICA
st.set_page_config(page_title="SmartFlood v4.7", layout="wide")
st.title("🌧️ SmartFlood – Heatmap de Risco + Sensores (IoT) + IA")
st.caption("Clique no mapa para definir o centro. Gera previsão, heatmap e sensores simulados.")

# ------------------ SIDEBAR
st.sidebar.header("⚙️ Configuração")
mode = st.sidebar.radio(
    "Modo do simulador de chuva:",
    ["Simulação contínua (realista)", "Dados reais via API (OpenWeather)"],
)
refresh_secs = st.sidebar.slider("⏱ Intervalo de atualização (s)", 10, 120, 30)
auto_refresh = st.sidebar.checkbox("Ativar atualização automática", True, help="Recarrega a cada N segundos")
radius_m = st.sidebar.slider("📏 Raio da área monitorada (m)", 50, 500, 300, step=25)

st.sidebar.markdown("---")
show_heatmap = st.sidebar.checkbox("🔥 Mostrar Heatmap de risco", True)
grid_res = st.sidebar.slider("🔳 Resolução do heatmap (metros por célula)", 30, 150, 80, 10)

show_sensors = st.sidebar.checkbox("📡 Mostrar sensores urbanos (simulados)", True)
n_sensors = st.sidebar.slider("Quantidade de sensores", 3, 30, 12)

st.sidebar.markdown("---")
st.sidebar.subheader("📍 Localização / API")
api_key = st.sidebar.text_input("🔑 OpenWeather API Key (opcional)", type="password")

# ------------------ ESTADO INICIAL
if "lat" not in st.session_state:
    st.session_state.lat = -3.096271
if "lon" not in st.session_state:
    st.session_state.lon = -60.020850

# ------------------ MODELO (opcional)
model_path = Path(__file__).resolve().parents[1] / "ml" / "flood_model.pkl"
model = joblib.load(model_path) if model_path.exists() else None

# ------------------ utilidades
def make_circle_geojson(lat: float, lon: float, radius_m: float) -> dict:
    wgs84 = pyproj.CRS("EPSG:4326")
    aeqd = pyproj.Proj(proj="aeqd", lat_0=lat, lon_0=lon)
    to_aeqd = pyproj.Transformer.from_proj(wgs84, aeqd, always_xy=True).transform
    to_wgs84 = pyproj.Transformer.from_proj(aeqd, wgs84, always_xy=True).transform

    pt = Point(lon, lat)
    circ_m = transform(to_aeqd, pt).buffer(radius_m)
    circ_ll = transform(to_wgs84, circ_m)
    return {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "geometry": mapping(circ_ll),
            "properties": {"center": [lat, lon], "radius_m": radius_m},
        }],
    }

def save_geojson(d: dict, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f)

# ------------------ MAPA DE SELEÇÃO (Folium)
st.markdown("### 🗺️ 1) Clique no mapa para definir o centro da área")
m = folium.Map(
    location=[st.session_state.lat, st.session_state.lon],
    zoom_start=14,
    tiles="CartoDB dark_matter",
)


folium.CircleMarker(
    location=[st.session_state.lat, st.session_state.lon],
    radius=6, color="#00ff88", fill=True, fill_opacity=0.9
).add_to(m)
ret = st_folium(m, width="100%", height=420)
if ret and ret.get("last_clicked"):
    st.session_state.lat = float(ret["last_clicked"]["lat"])
    st.session_state.lon = float(ret["last_clicked"]["lng"])

# gera/salva área
area_geo = make_circle_geojson(st.session_state.lat, st.session_state.lon, radius_m)
save_geojson(area_geo, Path(__file__).resolve().parents[1] / "data" / "area_user.geojson")

# ------------------ SIMULAÇÃO/REAL
start_time = datetime.now() - timedelta(hours=1)
mode_key = "api" if "API" in mode else "simulated"
sim = RainSoilDrainSimulator(
    start=start_time, mode=mode_key,
    lat=st.session_state.lat, lon=st.session_state.lon, api_key=api_key,
    seed=random.randint(0, 999999),
)
df = sim.get_history(datetime.now())
rain_now = float(df["rain_mm"].iloc[-1])
soil_now = float(df["soil_sat"].iloc[-1])      # 0..1
drain_now = float(df["drain_cap"].iloc[-1])    # 0..1

# ------------------ PREVISÃO + RISCO APRIMORADO
def hydro_risk_score(rain_mm: float, soil: float, drain: float) -> float:
    """
    Score 0..1 combinando chuva, solo e drenagem.
    Curva mais agressiva para extremos + reforço quando todos altos.
    """
    rain_factor  = min(1.0, rain_mm / 50.0)   # >50mm/h ≈ saturação
    soil_factor  = min(1.0, soil)             # 0..1
    drain_factor = 1.0 - drain                # bueiro cheio = 1.0

    base = 0.45*rain_factor + 0.35*soil_factor + 0.20*drain_factor
    amplified = base ** 1.8
    if rain_factor > 0.8 and soil_factor > 0.8 and drain_factor > 0.8:
        amplified = min(1.0, amplified * 1.25)
    return float(np.clip(amplified, 0, 1))

# cálculo único (sem duplicidades)
try:
    hydro_score = hydro_risk_score(rain_now, soil_now, drain_now)

    if model:
        X = pd.DataFrame([[rain_now, soil_now, drain_now]],
                         columns=["rain_mm", "soil_sat", "drain_cap"])
        pred = float(model.predict(X)[0])         # livre conforme treino
        nivel_prev = round(pred * 100.0, 2)       # ajuste de escala comum
        nivel_norm = min(1.0, nivel_prev / 30.0)  # cap a 30 cm
        risco_prev = min(100.0, round((0.60 * hydro_score + 0.40 * nivel_norm) * 100.0, 1))
    else:
        nivel_prev = round((hydro_score ** 0.5) * 25.0, 2)
        risco_prev = round(hydro_score * 100.0, 1)

except Exception as e:
    st.warning(f"⚠️ Erro na previsão: {e}")
    nivel_prev = round(random.uniform(0, 20), 2)
    risco_prev = round(min(100.0, nivel_prev * 4), 1)

# ------------------ KPIs
c1, c2, c3, c4 = st.columns(4)
c1.metric("🌧️ Chuva atual (mm/h)", f"{rain_now:.1f}")
c2.metric("🪴 Solo saturado", f"{soil_now*100:.0f}%")
c3.metric("🌀 Capacidade do bueiro", f"{drain_now*100:.0f}%")
c4.metric("🌊 Nível previsto (3h)", f"{nivel_prev:.1f} cm")

st.markdown(f"### 🔮 Risco previsto: **{risco_prev:.0f}%**")

# ------------------ 2D → 3D (PyDeck)
# estilo com fallback: MAPBOX (se houver) → Carto (sem chave)
map_style = (
    "mapbox://styles/mapbox/satellite-streets-v12"
    if os.getenv("MAPBOX_API_KEY")
    else "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"
)

# === Paleta consistente (4 faixas) ===
def risk_color_rgb(risk_percent: float) -> list[int]:
    """Retorna [R,G,B] para a % de risco."""
    r = float(risk_percent)
    if r < 30:   # verde
        return [0, 200, 0]
    elif r < 60: # amarelo
        return [255, 220, 0]
    elif r < 85: # laranja
        return [255, 140, 0]
    else:        # vermelho
        return [255, 0, 0]

# círculo principal
color_pt = risk_color_rgb(risco_prev)
layer_circle = pdk.Layer(
    "GeoJsonLayer",
    area_geo,
    opacity=0.55,
    stroked=True,
    filled=True,
    get_fill_color=color_pt,
    get_line_color=[210, 210, 210],
)

layers = [layer_circle]

# ------------------ Heatmap de risco (malha)
def gen_grid_points(lat0, lon0, radius_m, step_m, base_score: float) -> pd.DataFrame:
    """Gera pontos em grade ao redor do centro, devolvendo lat/lon e 'weight' (0..1)."""
    wgs84 = pyproj.CRS("EPSG:4326")
    aeqd = pyproj.Proj(proj="aeqd", lat_0=lat0, lon_0=lon0)
    to_aeqd = pyproj.Transformer.from_proj(wgs84, aeqd, always_xy=True).transform
    to_wgs84 = pyproj.Transformer.from_proj(aeqd, wgs84, always_xy=True).transform

    pts = []
    rng = range(-radius_m, radius_m + 1, step_m)
    for x in rng:
        for y in rng:
            if (x**2 + y**2) ** 0.5 <= radius_m:
                lon, lat = to_wgs84(x + 0.0, y + 0.0)
                # risco por distância ao centro (diminui na borda) + ruído leve
                dist = (abs(x) + abs(y)) / (2 * radius_m)  # 0 no centro → 1 borda
                weight = base_score * (1 - 0.7 * dist) + random.uniform(-0.04, 0.04)
                weight = max(0.0, min(1.0, weight))
                pts.append({"lat": lat, "lon": lon, "weight": weight})
    return pd.DataFrame(pts)

if show_heatmap:
    grid_df = gen_grid_points(st.session_state.lat, st.session_state.lon, radius_m, grid_res, hydro_score)
    # ColorRange coerente com as 4 faixas (verde → amarelo → laranja → vermelho)
    color_range = [
        [0,   200,   0],   # verde
        [255, 220,   0],   # amarelo
        [255, 140,   0],   # laranja
        [255,   0,   0],   # vermelho
    ]
    
    # Normaliza pesos para reforçar contraste (evita heatmap todo verde)
    if not grid_df.empty:
        w_min, w_max = grid_df["weight"].min(), grid_df["weight"].max()
        if w_max - w_min > 0:
            grid_df["weight_norm"] = (grid_df["weight"] - w_min) / (w_max - w_min)
        else:
            grid_df["weight_norm"] = grid_df["weight"]
    else:
        grid_df["weight_norm"] = 0.0

    heat = pdk.Layer(
        "HeatmapLayer",
        data=grid_df,
        get_position=["lon", "lat"],
        get_weight="weight_norm",
        radiusPixels=35,
        colorRange=color_range,
        aggregation=pdk.types.String("SUM"),
    )

    # pequenas colunas para dar relevo (opcional e leve) – usam laranja translúcido
    cols = pdk.Layer(
        "ColumnLayer",
        data=grid_df.sample(min(500, len(grid_df))),
        get_position=["lon", "lat"],
        get_elevation="weight * 30",
        elevationScale=1,
        radius=6,
        get_fill_color=[255, 140, 0, 130],
        pickable=False,
    )
    layers += [heat, cols]

# ------------------ Sensores simulados
def gen_sensors(lat0, lon0, n, radius_m, base_level_cm: float, base_rain: float, base_drain: float, base_risk_score: float):
    wgs84 = pyproj.CRS("EPSG:4326")
    aeqd = pyproj.Proj(proj="aeqd", lat_0=lat0, lon_0=lon0)
    to_wgs84 = pyproj.Transformer.from_proj(aeqd, wgs84, always_xy=True).transform
    sensors = []
    for _ in range(n):
        # ponto aleatório em disco
        r = radius_m * (random.random() ** 0.5)
        ang = random.uniform(0, 2 * math.pi)
        x, y = r * math.cos(ang), r * math.sin(ang)
        lon, lat = to_wgs84(x, y)

        # variações locais
        nivel  = max(0.0, min(30.0, random.gauss(base_level_cm, 3)))
        bueiro = max(0.0, min(100.0, 100 * (1 - max(0.0, min(1.0, random.gauss(base_drain, 0.12))))))  # %
        chuva  = max(0.0, random.gauss(base_rain, 5))

        # risco coerente com heurística + ruído leve
        local_risk = max(0.0, min(1.0, base_risk_score + random.uniform(-0.05, 0.05)))
        risco = round(local_risk * 100.0, 1)

        sensors.append({"lat": lat, "lon": lon, "nivel": nivel, "chuva": chuva, "bueiro": bueiro, "risco": risco})
    return pd.DataFrame(sensors)

if show_sensors:
    s_df = gen_sensors(
        st.session_state.lat, st.session_state.lon,
        n_sensors, radius_m,
        base_level_cm=nivel_prev, base_rain=rain_now, base_drain=drain_now, base_risk_score=hydro_score
    )

    s_df["color"] = s_df["risco"].apply(risk_color_rgb)
    sensors_layer = pdk.Layer(
        "ScatterplotLayer",
        data=s_df,
        get_position=["lon", "lat"],
        get_color="color",
        get_radius=35,
        pickable=True,
    )
    layers.append(sensors_layer)
    tooltip = {"html": "<b>Sensor</b><br/>Nível: {nivel} cm<br/>Chuva: {chuva} mm/h<br/>Bueiro: {bueiro}%<br/>Risco: {risco} %"}
else:
    tooltip = None

view = pdk.ViewState(
    latitude=st.session_state.lat,
    longitude=st.session_state.lon,
    zoom=14,
    pitch=45,
)
st.markdown("### 🗺️ 2) Visualização 3D e camadas (heatmap/sensores)")
st.pydeck_chart(pdk.Deck(layers=layers, initial_view_state=view, map_style=map_style, tooltip=tooltip))

# ------------------ LEGENDA DE RISCO (dentro do fluxo, abaixo do mapa)
st.markdown("### 🧭 Legenda de Risco")
st.markdown("""
<div style="
    display: flex;
    justify-content: space-around;
    align-items: center;
    background-color: rgba(25,25,25,0.9);
    border: 1px solid rgba(120,120,120,0.4);
    border-radius: 10px;
    padding: 10px;
    margin-top: 10px;
    margin-bottom: 15px;
    color: #f0f0f0;
    font-size: 13px;
">
    <div>🟢 <b>0–30%</b>: Sem chuva / risco baixo (~5%)</div>
    <div>🟡 <b>30–60%</b>: Chuva moderada + solo úmido (~60%)</div>
    <div>🟠 <b>60–85%</b>: Alerta elevado (atenção operacional)</div>
    <div>🔴 <b>>85%</b>: Chuva forte + solo saturado + bueiro cheio (>95%)</div>
</div>
""", unsafe_allow_html=True)


# ------------------ HISTÓRICO
st.subheader("📈 Histórico recente de chuva")
st.line_chart(df["rain_mm"], height=200, use_container_width=True)


# ------------------ CHAT FLOTANTE DE IA (Ollama integrado)
import ollama

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# HTML e CSS do chat estilo "janela flutuante" (compacta e sem sobreposição)
st.markdown("""
<style>
.chat-container {
    position: fixed;
    bottom: 35px;
    left: 25px;
    background-color: rgba(25, 25, 25, 0.95);
    color: #f0f0f0;
    border-radius: 10px;
    padding: 10px 12px;
    width: 260px;
    font-size: 13px;
    line-height: 1.4em;
    border: 1px solid rgba(100,100,100,0.5);
    z-index: 1000;
    box-shadow: 0 0 10px rgba(0,0,0,0.4);
}
.chat-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: bold;
    margin-bottom: 4px;
}
.chat-body {
    max-height: 160px;
    overflow-y: auto;
    background-color: rgba(40,40,40,0.6);
    border-radius: 6px;
    padding: 6px;
    margin-bottom: 4px;
    border: 1px solid rgba(80,80,80,0.5);
}
/* Campo de entrada compacto */
[data-testid="stChatInputContainer"] {
    width: 260px !important;
    position: fixed !important;
    bottom: 10px !important;
    left: 25px !important;
    z-index: 999 !important;
}
[data-testid="stChatInputTextarea"] {
    font-size: 13px !important;
    min-height: 32px !important;
}
</style>

<div class="chat-container">
    <div class="chat-header">
        <span>💬 Assistente SmartFlood</span>
    </div>
    <div id="chat-body" class="chat-body">
""", unsafe_allow_html=True)

# Mostrar o histórico da conversa (últimas 8 trocas)
for msg in st.session_state.chat_history[-8:]:
    role = "👤 Você" if msg["role"] == "user" else "🤖 IA"
    st.markdown(f"**{role}:** {msg['content']}")

st.markdown("""
    </div>
</div>
""", unsafe_allow_html=True)

# Campo de entrada (Streamlit padrão, mas ajustado por CSS)
user_msg = st.chat_input("Digite sua pergunta sobre o clima ou risco...")

if user_msg:
    st.session_state.chat_history.append({"role": "user", "content": user_msg})

    # --- Contexto atual + histórico (3h) para IA hidrológica ---

    # Extrai as últimas 3h de dados (caso o intervalo seja de 5min = 36 pontos)
    df_recent = df.tail(36) if len(df) > 36 else df.copy()

    # Estatísticas históricas básicas
    rain_avg = df_recent["rain_mm"].mean() if "rain_mm" in df_recent else rain_now
    rain_max = df_recent["rain_mm"].max() if "rain_mm" in df_recent else rain_now
    soil_trend = df_recent["soil_sat"].diff().mean() if "soil_sat" in df_recent else 0
    drain_trend = df_recent["drain_cap"].diff().mean() if "drain_cap" in df_recent else 0

    # Construção do contexto descritivo e interpretável
    context = (
        f"Últimas 3h: chuva média {rain_avg:.1f} mm/h (máxima {rain_max:.1f} mm/h). "
        f"Saturação do solo {'aumentando' if soil_trend > 0 else 'diminuindo' if soil_trend < 0 else 'estável'} "
        f"({soil_now*100:.1f}%). "
        f"Capacidade do bueiro {'reduzindo' if drain_trend < 0 else 'aumentando' if drain_trend > 0 else 'estável'} "
        f"({drain_now*100:.1f}%). "
        f"Nível previsto: {nivel_prev:.1f} cm. "
        f"Risco atual de alagamento: {risco_prev:.1f}%. "
    )

    # Prompt estruturado com instruções hidrológicas
    messages = [
        {
            "role": "system",
            "content": (
                "Você é o assistente hidrológico do sistema SmartFlood. "
                "Analise os dados atuais e históricos de chuva, saturação do solo e capacidade de drenagem. "
                "Com base nas tendências (últimas 3 horas), avalie se o risco está aumentando, estável ou diminuindo. "
                "Responda de forma clara e explicativa, destacando alertas de risco crescente."
            ),
        },
        {"role": "user", "content": f"Contexto hidrológico atual: {context}"},
    ] + st.session_state.chat_history[-5:]

    # --- Consulta ao modelo LLaMA 3.1:8b via Ollama ---
    try:
        with st.spinner("Consultando modelo LLaMA 3.1:8b..."):
            resp = ollama.chat(model="llama3.1:8b", messages=messages)
            answer = resp["message"]["content"]
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
            st.rerun()
    except Exception as e:
        st.error(f"Erro ao conectar com o modelo Ollama: {e}")




# ------------------ AUTOREFRESH
if auto_refresh:
    st.caption(f"🔄 Atualiza automaticamente a cada {refresh_secs}s")
    time.sleep(refresh_secs)
    st.rerun()

