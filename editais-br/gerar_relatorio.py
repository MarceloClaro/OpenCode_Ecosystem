import json, os

SCORES_PATH = r"C:\Users\marce\.config\opencode\skills\research\editais-br\curated\CURATED_EDITAIS_SCORES.json"
OUTPUT_PATH = r"C:\Users\marce\.config\opencode\editais-br\relatorio_complementar.md"

with open(SCORES_PATH, encoding="utf-8") as f:
    data = json.load(f)

scores = data["scores"]
top2 = data["top_2_per_profile"]
profiles = data["metadata"]["profiles"]

top2_ids = set()
for p in profiles:
    for t in top2[p]:
        top2_ids.add(t["id"])

other = [s for s in scores if s["id"] not in top2_ids]

lines = []

def w(s=""):
    lines.append(s)

w("# Relat\u00f3rio Complementar: An\u00e1lise Detalhada do Ecossistema de Editais Brasileiros (2026)")
w("")
w("> Gerado em 16 de maio de 2026 | Base: {} editais 2026, 4 perfis de proponente".format(len(scores)))
w("> Editais top-2 por perfil encaminhados aos Workers A e B para extra\u00e7\u00e3o profunda")
w("")
w("---")
w("")
w("## 1. Resumo Executivo")
w("")
w("Este relat\u00f3rio analisa os **{} editais mapeados** no ecossistema brasileiro de fomento \u00e0 pesquisa, inova\u00e7\u00e3o, cultura e impacto social para 2026. Os editais foram pontuados em quatro perfis de proponente (pesquisa, mestrado, doutorado, startup) em escala 0-100. Os dois melhores colocados de cada perfil foram encaminhados para extra\u00e7\u00e3o aprofundada pelos Workers A e B, restando **{} editais** para an\u00e1lise complementar.".format(len(scores), len(other)))
w("")
w("### Estat\u00edsticas Gerais")
w("")
w("| M\u00e9trica | Pesquisa | Mestrado | Doutorado | Startup |")
w("|---------|----------|----------|-----------|---------|")

import statistics
for label, fn in [("M\u00e9dia", statistics.mean), ("Mediana", statistics.median), ("Desvio Padr\u00e3o", statistics.stdev), ("M\u00ednimo", min), ("M\u00e1ximo", max)]:
    vals = [fn([s[p] for s in scores]) for p in profiles]
    vals_str = " | ".join("{:.1f}".format(v) if isinstance(v, float) else str(v) for v in vals)
    w("| {} | {} |".format(label, vals_str))

w("")
w("### Distribui\u00e7\u00e3o por Faixa de Score")
w("")
w("| Faixa | Pesquisa | Mestrado | Doutorado | Startup |")
w("|-------|----------|----------|-----------|---------|")
for lo, hi in [(0,20),(21,40),(41,60),(61,80),(81,100)]:
    counts = [sum(1 for s in scores if lo <= s[p] <= hi) for p in profiles]
    w("| {}-{} | {} | {} | {} | {} |".format(lo, hi, *counts))

w("")
w("---")
w("")
w("## 2. Top 2 por Perfil (Workers A e B)")
w("")

for p in profiles:
    emoji_map = {"pesquisa": "### Perfil Pesquisa", "mestrado": "### Perfil Mestrado", "doutorado": "### Perfil Doutorado", "startup": "### Perfil Startup"}
    w(emoji_map[p])
    w("| Rank | Edital | Score |")
    w("|------|--------|-------|")
    for t in top2[p]:
        w("| {} | {} | {} |".format(t["rank"], t["nome"], t["score"]))
    w("")

w("---")
w("")
w("## 3. Joias Escondidas (Hidden Gems)")
w("")
w("Editais com alta pontua\u00e7\u00e3o no perfil (>= 75) que N\u00c3O est\u00e3o entre os top 2.")
w("")

for p in profiles:
    gems = sorted([s for s in other if s[p] >= 75], key=lambda x: x[p], reverse=True)
    if gems:
        w("### Para {}".format(p.capitalize()))
        w("| Edital | Score | ID |")
        w("|--------|-------|----|")
        for g in gems:
            w("| {} | {} | {} |".format(g["nome"][:50], g[p], g["id"]))
        w("")

w("### Multi-Perfil (>= 70 em 2+ perfis)")
w("| Edital | Perfis Altos | Soma |")
w("|--------|-------------|------|")
multi = [(s, [p for p in profiles if s[p] >= 70]) for s in other if len([p for p in profiles if s[p] >= 70]) >= 2]
for s, high in sorted(multi, key=lambda x: sum(x[0][p] for p in x[1]), reverse=True):
    scores_str = ", ".join("{}: {}".format(p, s[p]) for p in high)
    total = sum(s[p] for p in high)
    w("| {} | {} | {} |".format(s["nome"][:50], scores_str, total))

w("")
w("---")
w("")
w("## 4. Quick Wins (Menor Barreira de Entrada)")
w("")
w("| Edital | Perfil | Score | Vantagem |")
w("|--------|--------|-------|----------|")
quick_wins = [
    ("Demanda Espont\u00e2nea FAPERJ", "Pesquisa", 80, "Fluxo cont\u00ednuo, submiss\u00e3o simplificada"),
    ("Capital Semente SEBRAE", "Startup", 84, "Processo 100% digital, prazo curto"),
    ("InovAtiva Brasil", "Startup", 86, "Acelera\u00e7\u00e3o, n\u00e3o exige CNPJ"),
    ("Bolsa Produtividade CNPq", "Pesquisa", 92, "Fluxo cont\u00ednuo (avalia\u00e7\u00e3o quadrienal)"),
    ("Bolsa Mestrado FAPEPI", "Mestrado", 72, "Baixa concorr\u00eancia regional"),
    ("Chamada Cerrado Agtechs", "Startup", 82, "Edital tem\u00e1tico com baixo n\u00famero hist\u00f3rico de inscritos"),
    ("Startup FAPEAL", "Startup", 58, "Mercado pouco explorado em AL"),
]
for nome, perfil, score, vant in quick_wins:
    w("| {} | {} | {} | {} |".format(nome, perfil, score, vant))

w("")
w("---")
w("")
w("## 5. Compara\u00e7\u00e3o com Top 2 vs. Demais Editais")
w("")

comparisons = {
    "pesquisa": "Os top 2 (FAPEMIG Universal 95, CNPq Produtividade 92) s\u00e3o programas consolidados. Os principais concorrentes (PROSUL 82, FAPERJ Espont\u00e2nea 80, FAPESP-ERC 78) oferecem vantagens complementares: coopera\u00e7\u00e3o internacional ou fluxo cont\u00ednuo simplificado. O salto de 92 para 82 (10 pontos) indica uma elite clara de editais de pesquisa.",
    "mestrado": "O dom\u00ednio da FAPERJ no top 2 (Nota 10 = 92, Bolsas = 85) reflete o or\u00e7amento generoso do RJ para bolsas. Fora do eixo RJ-SP, as melhores op\u00e7\u00f5es s\u00e3o FAPEMIG (82), FAPEPI (72) e FAPEMA (68). O gap entre a 2\u00aa e a 3\u00aa colocada \u00e9 de apenas 3 pontos (85 \u2192 82).",
    "doutorado": "Brasil-China Beihang (85) lidera pela oportunidade \u00fanica de interc\u00e2mbio com institui\u00e7\u00e3o chinesa de ponta. Bolsas FAPERJ (83) e FAPEMIG (80) completam o p\u00f3dio. O gap para o 4\u00ba colocado (FAPEPI 70) \u00e9 significativo (10 pontos).",
    "startup": "O segmento mais competitivo: PIPE FAPESP (95) e BNDES Garagem (92) s\u00e3o refer\u00eancias. Abaixo, Subven\u00e7\u00e3o FINEP (88), InovAtiva (86), FUNTEC (85), EMBRAPII (85) e Capital Semente (84) formam um pelot\u00e3o compacto com diferen\u00e7as marginais (4 pontos entre 3\u00ba e 7\u00ba). **Esta \u00e9 a faixa com maior potencial de descoberta de gems.**",
}
for p, text in comparisons.items():
    w("### Perfil {}".format(p.capitalize()))
    w("")
    w(text)
    w("")

w("---")
w("")
w("## 6. Recomenda\u00e7\u00f5es Estrat\u00e9gicas")
w("")
w("### Para Pesquisadores Doutores")
w("1. **FAPEMIG Universal** e **CNPq Produtividade** s\u00e3o essenciais \u2014 mantenha submiss\u00f5es ativas.")
w("2. Explore **PROSUL Pepe Mujica** e **FAPESP-ERC** se tiver colabora\u00e7\u00e3o internacional.")
w("3. **Horizon Europe** exige parceria europeia, mas o retorno em prest\u00edgio e funding \u00e9 incompar\u00e1vel.")
w("4. FAPs de menor or\u00e7amento (FAPAC, FAPT, FAPERO) oferecem baixa concorr\u00eancia \u2014 ideal para primeiros projetos.")
w("")
w("### Para Estudantes de Mestrado/Doutorado")
w("1. Priorize bolsas FAPERJ (Nota 10) e FAPEMIG se estiver no Sudeste.")
w("2. **CAPES Brasil-China** \u00e9 a melhor oportunidade de interc\u00e2mbio de alto n\u00edvel.")
w("3. Para estudantes fora do eixo RJ-SP, FAPEPI, FAPEMA e FAPESQ oferecem bolsas com concorr\u00eancia regional reduzida.")
w("")
w("### Para Startups e Empreendedores")
w("1. **PIPE FAPESP** \u00e9 o padr\u00e3o ouro \u2014 submeta obrigatoriamente se estiver em SP.")
w("2. **BNDES Garagem** e **InovAtiva** s\u00e3o portas de entrada com baixa burocracia.")
w("3. **Subven\u00e7\u00e3o FINEP** e **FUNTEC** exigem contrapartida, mas o volume de recursos \u00e9 5-10x maior que programas de acelera\u00e7\u00e3o.")
w("4. Editais tem\u00e1ticos regionais (Cerrado Agtechs, Bioeconomia Amaz\u00f4nica) t\u00eam concorr\u00eancias baixas e alto alinhamento com ESG.")
w("5. **Startup FAPEMIG**, **Startup FAPEG** e **Startup FAPERJ** s\u00e3o gems pouco conhecidas fora de seus estados.")
w("")
w("### Gerais")
w("1. **Diversifique perfis:** Pesquisadores podem se beneficiar de editais de startup se tiverem spin-offs.")
w("2. **Aproveite fluxo cont\u00ednuo:** FAPERJ Espont\u00e2nea, CNPq Produtividade e Capital Semente SEBRAE.")
w("3. **Monitore prazos:** Editais internacionais (Horizon Europe, Wellcome) t\u00eam janelas espec\u00edficas.")
w("")
w("---")
w("")
w("## 7. Metodologia de Pontua\u00e7\u00e3o")
w("")
w("Cada edital foi pontuado em 4 perfis (0-100) considerando:")
w("")
w("- **Pesquisa:** Valor do projeto, prazo, exig\u00eancia de produ\u00e7\u00e3o cient\u00edfica, abrang\u00eancia multidisciplinar, reputa\u00e7\u00e3o da ag\u00eancia")
w("- **Mestrado:** Valor da bolsa, dura\u00e7\u00e3o, requisitos de ingresso, v\u00ednculo com programa de p\u00f3s")
w("- **Doutorado:** Valor da bolsa, dura\u00e7\u00e3o, exig\u00eancias acad\u00eamicas, prest\u00edgio, interc\u00e2mbio")
w("- **Startup:** Valor do aporte, TRL exigido, contrapartida, prazo, setor-alvo, flexibilidade")
w("")
w("### Limita\u00e7\u00f5es")
w("- Pontua\u00e7\u00f5es refletem a base de maio/2026")
w("- Editais de fluxo cont\u00ednuo foram pontuados com base em valores hist\u00f3ricos")
w("- Editais internacionais podem ter valores em moeda estrangeira n\u00e3o ajustados")
w("")
w("---")
w("")
w("## 8. Pr\u00f3ximos Passos")
w("")
w("1. **Workers A e B** est\u00e3o extraindo dados aprofundados dos 7 editais top-2")
w("2. Incorporar dados dos workers para recalibrar pontua\u00e7\u00f5es dos demais editais")
w("3. Validar pontua\u00e7\u00f5es com especialistas por perfil")
w("4. Integrar dados de prazos reais via conectores (SIGEPE, SEBRAE, Prosas, FINEP, FAPEG, CNPq)")
w("5. Expandir base para incluir editais municipais e fundos setoriais")
w("6. Automatizar atualiza\u00e7\u00e3o semanal com alertas de novos editais por perfil")
w("")
w("---")
w("")
w("*Relat\u00f3rio gerado automaticamente pelo pipeline editais-br v7.1*")
w("*Ferramenta: OpenCode CLI + Python 3.12 + MCP editais-br*")
w("*Base: curated/CURATED_EDITAIS.json + curated/CURATED_EDITAIS_SCORES.json*")

content = "\n".join(lines)
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("OK: {} lines, {} chars".format(len(lines), len(content)))
print("Path: " + OUTPUT_PATH)
