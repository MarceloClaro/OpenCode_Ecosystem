"""Tela de Graph view — visualiza a wiki como grafo de páginas e wikilinks."""
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network
import tempfile
from pathlib import Path

from src import storage


CATEGORY_COLORS = {
    "topicos": "#7F77DD",      # roxo
    "entidades": "#1D9E75",    # teal
    "conceitos": "#D85A30",    # coral
    "sinteses": "#D4537E",     # pink
    "fontes": "#888780",       # gray
}
DEFAULT_COLOR = "#5F5E5A"


def render():
    st.header("Graph view")
    st.caption("Visualização interativa da wiki como rede de páginas conectadas por wikilinks. Cores indicam categoria.")

    data = storage.get_graph_data()
    nodes = data["nodes"]
    edges = data["edges"]

    if not nodes:
        st.info("A wiki ainda está vazia. Ingira algumas fontes para gerar páginas.")
        return

    # Estatísticas
    col1, col2, col3 = st.columns(3)
    col1.metric("Nós (páginas)", len(nodes))
    col2.metric("Arestas (links)", len(edges))
    cats = set(n["category"] for n in nodes)
    col3.metric("Categorias", len(cats))

    # Legenda
    legend_cols = st.columns(min(len(cats), 5))
    for i, cat in enumerate(sorted(cats)):
        with legend_cols[i % len(legend_cols)]:
            color = CATEGORY_COLORS.get(cat, DEFAULT_COLOR)
            st.markdown(
                f"<span style='color:{color}; font-size:1.5em'>●</span> {cat}",
                unsafe_allow_html=True,
            )

    st.divider()

    # Constrói o grafo
    net = Network(
        height="600px",
        width="100%",
        bgcolor="#ffffff",
        font_color="#222222",
        directed=False,
        notebook=False,
        cdn_resources="remote",
    )
    net.set_options("""
    var options = {
      "physics": {
        "forceAtlas2Based": {
          "gravitationalConstant": -50,
          "centralGravity": 0.01,
          "springLength": 120,
          "springConstant": 0.08
        },
        "minVelocity": 0.75,
        "solver": "forceAtlas2Based"
      },
      "nodes": {
        "shape": "dot",
        "scaling": { "min": 10, "max": 30 }
      },
      "edges": {
        "color": { "color": "#aaaaaa", "highlight": "#222222" },
        "smooth": { "enabled": false }
      },
      "interaction": { "hover": true, "tooltipDelay": 100 }
    }
    """)

    # Calcula grau de cada nó (para tamanho)
    degree = {}
    for e in edges:
        degree[e["from"]] = degree.get(e["from"], 0) + 1
        degree[e["to"]] = degree.get(e["to"], 0) + 1

    for n in nodes:
        size = 12 + min(degree.get(n["id"], 0) * 3, 30)
        color = CATEGORY_COLORS.get(n["category"], DEFAULT_COLOR)
        net.add_node(
            n["id"],
            label=n["label"],
            color=color,
            size=size,
            title=f"{n['category']}/{n['label']}",
        )

    for e in edges:
        net.add_edge(e["from"], e["to"])

    # Renderiza em HTML temporário
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8") as tmp:
        net.write_html(tmp.name, notebook=False, open_browser=False)
        html_path = Path(tmp.name)
    html_content = html_path.read_text(encoding="utf-8")
    html_path.unlink(missing_ok=True)

    components.html(html_content, height=620, scrolling=False)
