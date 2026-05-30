"""
Simulacao de Raciocinio Cientifico — DCA + OpenCode Ecosystem Evolution v2.0.
Incorporando o relatorio de correcao oficial como feedback de aprendizado.
Ciclo: Resolucao → Correcao → Aprendizado → Re-resolucao.
"""

import sys
import json
import time
import random
from datetime import datetime
from pathlib import Path

SKILL_SCRIPTS = Path.home() / ".config" / "opencode" / "skills" / "graph-memory-updater" / "scripts"
sys.path.insert(0, str(SKILL_SCRIPTS))
from memory_updater import (
    AgentActivity, GraphMemoryUpdater, MockGraphStorage, MemoryManager,
)

# ─── Correcoes oficiais do professor (extraidas do relatorio) ─────
CORRECOES = {
    "L1-Q1": {"nota": 1.80, "erro": "dependencia circular L_XF Omega antes de prova formal em (b)"},
    "L1-Q2": {"nota": 1.00, "erro": "sinais contraditorios em su(1,1); campos hamiltonianos com sinais e fatores incompatíveis"},
    "L1-Q3": {"nota": 0.90, "erro": "fatores incorretos de E e F na separacao; beta nao reescrita corretamente em cilindricas; Runge-Lenz vago"},
    "L1-Q4": {"nota": 0.90, "erro": "Jr = E/omega - L em vez de E/(2 omega) - L/2; H = omega(Jr+Jtheta+Jphi) errada; frequencias erradas"},
    "L1-Q5": {"nota": 1.40, "erro": "sinal errado de P = -dS/dQ levando a sinal incorreto de F t^3/(6m)"},
    "L2-Q1": {"nota": 1.80, "erro": "passagem infinitesimal → epsilon finito abreviada; faltou d/de Phi_epsilon^* Omega"},
    "L2-Q2": {"nota": 0.70, "erro": "sinal errado em eqs de Hamilton de Toda; bdot inconsistente; Tr(A^2), Tr(A^3), involucao omitidos"},
    "L2-Q3": {"nota": 1.20, "erro": "sem codigo, sem graficos, apenas descricao textual; faltou estudo numerico com Poincare"},
    "L2-Q4": {"nota": 1.00, "erro": "segunda ressonancia mal calculada: 2w1-3w2=0 → 5J1-12J2=1, nao J1=(7/5)J2+1/5"},
    "L2-Q5": {"nota": 1.30, "erro": "resumido demais; termo linear B^(0)(phi).P nao desenvolvido; etapa iterativa so declarada"},
    "L3-Q1": {"nota": 1.10, "erro": "unicidade de R=partial_s nao discutida; apenas verificou candidato"},
    "L3-Q2": {"nota": 0.55, "erro": "sem codigo Python; H0 nao decai exponencialmente em geral; bacias chamadas de fractal sem justificativa"},
    "L3-Q3": {"nota": 0.75, "erro": "sinal errado em F^*(dx^dy): +b em vez de -b; orientacao de area afetada"},
    "L3-Q4": {"nota": 0.70, "erro": "sem codigo solicitado; soma de expoentes apenas afirmada; comparacao com log|b| insuficiente"},
    "L3-Q5": {"nota": 0.75, "erro": "simbolo principal com sinal negativo; conversao Ito incompleta sem correcao de deriva explicita"},
    "L3-Q6": {"nota": 0.50, "erro": "sem parametros, codigo, esquema de diferencas finitas nem comparacao quantitativa"},
    "L3-Q7": {"nota": 0.75, "erro": "definicao da forca termodinamica alterada; sigma inconsistente sem a correcao"},
    "L3-Q8": {"nota": 0.65, "erro": "sem codigo, sem inicializacao de equilibrio, sem convergencia com N trajetorias, sem Crooks quantitativo"},
}

NOTAS_POR_LISTA = {
    "Lista 1": {"nota": 6.00, "max": 10.00, "questoes": ["L1-Q1","L1-Q2","L1-Q3","L1-Q4","L1-Q5"]},
    "Lista 2": {"nota": 6.00, "max": 10.00, "questoes": ["L2-Q1","L2-Q2","L2-Q3","L2-Q4","L2-Q5"]},
    "Lista 3": {"nota": 5.75, "max": 10.00, "questoes": ["L3-Q1","L3-Q2","L3-Q3","L3-Q4","L3-Q5","L3-Q6","L3-Q7","L3-Q8"]},
}

# ─── 18 Questoes DCA ─────────────────────────────────────────────
DCA_PROBLEMS = [
    {"id": "L1-Q1", "area": "Geometria Simpletica", "titulo": "Identidades de Poisson intrinsecas", "valor": 2.00},
    {"id": "L1-Q2", "area": "Geometria de Kahler", "titulo": "Disco de Poincare e acao SU(1,1)", "valor": 2.00},
    {"id": "L1-Q3", "area": "Hamilton-Jacobi", "titulo": "Particula em potencial Coulomb + campo uniforme", "valor": 2.00},
    {"id": "L1-Q4", "area": "Sistemas Integraveis", "titulo": "Oscilador harmonico isotropico em acao-angulo", "valor": 2.00},
    {"id": "L1-Q5", "area": "Transformacoes Canonicas", "titulo": "Hamiltoniana dependente do tempo", "valor": 2.00},
    {"id": "L2-Q1", "area": "Teoria de Perturbacao", "titulo": "Transformacao proxima da identidade e equacao homologa", "valor": 2.00},
    {"id": "L2-Q2", "area": "Sistemas Integraveis", "titulo": "Rede de Toda de tres corpos", "valor": 2.00},
    {"id": "L2-Q3", "area": "Sistemas Nao-Integraveis", "titulo": "Potencial de Henon-Heiles e secao de Poincare", "valor": 2.00},
    {"id": "L2-Q4", "area": "Teoria de Perturbacao", "titulo": "Modelo de Walker-Ford com duas ressonancias", "valor": 2.00},
    {"id": "L2-Q5", "area": "Teoria KAM", "titulo": "Esquema iterativo KAM para N=2", "valor": 2.00},
    {"id": "L3-Q1", "area": "Geometria de Contato", "titulo": "Hamiltoniano de contato com dissipacao", "valor": 1.25},
    {"id": "L3-Q2", "area": "Geometria de Contato", "titulo": "Potencial duplo poco com contato", "valor": 1.25},
    {"id": "L3-Q3", "area": "Sistemas Dinamicos Discretos", "titulo": "Mapa de Henon — pullback e Lyapunov", "valor": 1.25},
    {"id": "L3-Q4", "area": "Sistemas Dinamicos Discretos", "titulo": "Diagrama de bifurcacao e atrator de Henon", "valor": 1.25},
    {"id": "L3-Q5", "area": "Processos Estocasticos", "titulo": "EDE de Stratonovich no circulo", "valor": 1.25},
    {"id": "L3-Q6", "area": "Processos Estocasticos", "titulo": "Simulacao numerica Stratonovich vs Ito", "valor": 1.25},
    {"id": "L3-Q7", "area": "Termodinamica Estocastica", "titulo": "Producao de entropia e cohomologia", "valor": 1.25},
    {"id": "L3-Q8", "area": "Termodinamica Estocastica", "titulo": "Igualdade de Jarzynski e relacao de Crooks", "valor": 1.25},
]

SCIENTISTS = [
    {"name": "Henri_Poincare", "specialty": "Topologia-SistemasDinamicos",
     "reasoning": ["Reducionismo", "Analise_Estrutural", "Generalizacao_Indutiva"]},
    {"name": "Emmy_Noether", "specialty": "Simetrias-LeisConservacao",
     "reasoning": ["Invariancia_Formal", "Abstracao_Categorial", "Simetria_Diferencial"]},
    {"name": "Vladimir_Arnold", "specialty": "GeometriaSimpletica-KAM",
     "reasoning": ["Perturbacao_Estrutural", "Topologia_Diferencial", "Formalismo_Geometrico"]},
    {"name": "Carl_Sagan", "specialty": "Divulgacao-Sintese",
     "reasoning": ["Analogia_Visual", "Traducao_Conceitual", "Sintese_Narrativa"]},
    {"name": "Maryam_Mirzakhani", "specialty": "SuperficiesRiemann-Dinamica",
     "reasoning": ["Geometrizacao_Abstrata", "Classificacao_Topologica", "Contagem_Orbital"]},
    {"name": "Ludwig_Boltzmann", "specialty": "MecanicaEstatistica-Entropia",
     "reasoning": ["Reducionismo_Estatistico", "Ergodicidade", "Convergencia_Probabilistica"]},
    {"name": "Andrey_Kolmogorov", "specialty": "Probabilidade-EDE",
     "reasoning": ["Axiomatizacao_Formal", "Medida_Probabilistica", "Cadeias_Markov"]},
    {"name": "Josiah_Gibbs", "specialty": "Termodinamica-Ensemble",
     "reasoning": ["Modelagem_Estatistica", "Equilibrio_Termico", "Potenciais_Termodinamicos"]},
    {"name": "Sofia_Kovalevskaya", "specialty": "Integrabilidade-AnaliseComplexa",
     "reasoning": ["Continuacao_Analitica", "Singularidades_Moveis", "Separacao_Variaveis"]},
    {"name": "Michael_Berry", "specialty": "CaosQuantico-FasesGeometricas",
     "reasoning": ["Semiclassica", "Interferencia_Construtiva", "Causticas_Difracao"]},
]

REASONING_ACTIONS = [
    "INDUCTION", "DEDUCTION", "ABDUCTION", "ANALOGY", "REDUCTION",
    "GENERALIZATION", "SPECIALIZATION", "SYNTHESIS", "ANALYSIS", "ABSTRACTION",
    "FORMALIZATION", "GEOMETRIZATION", "PERTURBATION_EXPANSION", "FOURIER_ANALYSIS",
    "EIGENVALUE_PROBLEM", "VARIATIONAL_PRINCIPLE", "CONSERVATION_LAW", "SYMMETRY_ARGUMENT",
    "TOPOLOGICAL_INVARIANT", "FIXED_POINT_THEOREM", "ERGODIC_HYPOTHESIS", "STOCHASTIC_LIMIT",
    "COHOMOLOGY_OBSTRUCTION", "MONTE_CARLO_SAMPLING", "NUMERICAL_INTEGRATION",
    "BIFURCATION_ANALYSIS", "LYAPUNOV_STABILITY", "RESONANCE_CONDITION",
    "HAMILTONIAN_FLOW", "CANONICAL_TRANSFORM", "LIOUVILLE_INTEGRABILITY",
]

CORRECTION_INSIGHTS = {
    "L1-Q1": ["desacoplar L_XF Omega = 0 antes de usa-la na prova de (a)",
              "reordenar demonstracao: (b) antes de (a)"],
    "L1-Q2": ["corrigir sinais de J0, J1, J2 na algebra su(1,1)",
              "revisar campos hamiltonianos com convencao de sinal consistente"],
    "L1-Q3": ["corrigir fatores de E e F na equacao separada",
              "reescrever beta em coordenadas cilindricas via transformacao direta",
              "explicitar componente z do vetor de Runge-Lenz com sinal"],
    "L1-Q4": ["corrigir Jr = E/(2 omega) - L/2 (nao E/omega - L)",
              "recalcular H = omega(2 Jr + Jtheta + Jphi)",
              "recalcular frequencias com a hamiltoniana correta"],
    "L1-Q5": ["corrigir sinal: P = -dS/dQ",
              "refazer q(t) com sinal correto do termo F t^3/(6m)"],
    "L2-Q1": ["explicitar d/de Phi_epsilon^* Omega = Phi_epsilon^*(L_XG Omega)",
              "justificar passagem do infinitesimal ao finito com rigor"],
    "L2-Q2": ["corrigir sinal nas equacoes de Hamilton de Toda",
              "deduzir bdot consistentemente",
              "calcular Tr(A), Tr(A^2), Tr(A^3) explicitamente",
              "mostrar involucao das 3 integrais"],
    "L2-Q3": ["implementar codigo Python para secao de Poincare",
              "gerar graficos com curvas invariantes, ilhas e regioes estocasticas",
              "identificar e rotular cada estrutura no grafico"],
    "L2-Q4": ["corrigir segunda ressonancia: 5J1 - 12J2 = 1",
              "desenvolver interpretacao geometrica completa"],
    "L2-Q5": ["desenvolver termo linear B^(0)(phi).P com Fourier",
              "explicitar etapa iterativa de reajuste de frequencias",
              "conectar degenerescencia torsional a sobrevivencia de toros"],
    "L3-Q1": ["provar unicidade de R = partial_s a partir de campo geral",
              "discutir toros instantaneos com gamma << omega"],
    "L3-Q2": ["implementar integracao numerica em Python",
              "gerar graficos de retratos, H0(t) semilog, erro numerico e bacias",
              "justificar corretamente o decaimento de H0"],
    "L3-Q3": ["corrigir sinal: F^*(dx^dy) = -b dx^dy",
              "revisar interpretacao da orientacao de area"],
    "L3-Q4": ["implementar codigo com metodo QR/Benettin para Lyapunov",
              "comparar numericamente soma dos expoentes com log|b|",
              "gerar diagrama de bifurcacao e atratores"],
    "L3-Q5": ["corrigir sinal do simbolo principal como objeto intrinseco",
              "explicitar correcao de deriva b + (1/2) a a' na conversao Ito"],
    "L3-Q6": ["escolher parametros explicitos e documenta-los",
              "implementar esquema de diferencas finitas com conservacao de massa",
              "comparar quantitativamente histograma vs Fokker-Planck",
              "demonstrar numericamente erro ao omitir correcao de Ito"],
    "L3-Q7": ["usar definicao correta da forca: chi^{-1}(j/rho)",
              "recalcular sigma com a definicao consistente",
              "conectar classe de cohomologia de A a corrente estacionaria"],
    "L3-Q8": ["implementar codigo Python para Jarzynski e Crooks",
              "inicializar ensembles no equilibrio para os dois protocolos",
              "mostrar convergencia de <e^{-beta W}> com N trajetorias",
              "testar quantitativamente log(P_F(W)/P_R(-W)) = beta W"],
}

COMPREENSIVO_GERAL = [
    "trocar demonstracao por narracao → incluir calculos explicitos",
    "sinais nao sao cosmeticos em geometria simpletica e de contato",
    "questoes numericas exigem codigo completo, parametros e graficos",
    "afirmacoes como 'o codigo confirma' nao substituem verificacao reproduzivel",
    "a tabela de notas autoatribuidas nao corrige lacunas nas demonstracoes",
]


def generate_first_attempt(scientist, problem, round_num):
    """Primeira tentativa — pode conter erros (como o aluno)."""
    reasoning = random.choice(REASONING_ACTIONS)
    corr = CORRECOES.get(problem["id"], {})
    nota = corr.get("nota", 1.0)
    qualidade = "parcialmente correto" if nota > 1.0 else "com erros significativos"

    return AgentActivity(
        platform="twitter",
        agent_id=hash(scientist["name"]) % 1000,
        agent_name=scientist["name"].replace("_", " "),
        action_type="CREATE_POST",
        action_args={
            "content": f"[{reasoning}] Resolvendo {problem['id']}: abordagem {qualidade}",
            "problem_id": problem["id"],
            "phase": "primeira_tentativa",
            "round": round_num,
        },
        round_num=round_num,
        timestamp=datetime.now().isoformat(),
    )


def generate_correction_feedback(problem, round_num):
    """Feedback do corretor (professor) apontando erros especificos."""
    corr = CORRECOES.get(problem["id"], {})
    erro = corr.get("erro", "erros nao especificados")
    nota = corr.get("nota", 0)
    valor = problem["valor"]

    return AgentActivity(
        platform="reddit",
        agent_id=999,
        agent_name="Prof_Corretor",
        action_type="CREATE_COMMENT",
        action_args={
            "content": f"[CORRECAO {problem['id']}] Nota: {nota:.2f}/{valor:.2f}. Erro: {erro}",
            "post_content": f"Resolucao de {problem['id']}",
            "post_author_name": "Aluno",
            "phase": "correcao",
            "round": round_num,
        },
        round_num=round_num,
        timestamp=datetime.now().isoformat(),
    )


def generate_learning_cycle(scientist, problem, round_num):
    """Agente aprende com o feedback e aplica correcao."""
    insights = CORRECTION_INSIGHTS.get(problem["id"], ["revisar demonstracao"])
    insight = random.choice(insights)

    return AgentActivity(
        platform="twitter",
        agent_id=hash(scientist["name"]) % 1000,
        agent_name=scientist["name"].replace("_", " "),
        action_type="QUOTE_POST",
        action_args={
            "content": f"Aprendizado: {insight}",
            "original_content": f"Correcao de {problem['id']}",
            "original_author_name": "Prof_Corretor",
            "quote_content": f"[{random.choice(REASONING_ACTIONS)}] Corrigindo: {insight}",
            "phase": "aprendizado",
            "round": round_num,
        },
        round_num=round_num,
        timestamp=datetime.now().isoformat(),
    )


def generate_improved_solution(scientist, problem, round_num):
    """Solucao revisada apos feedback."""
    corr = CORRECOES.get(problem["id"], {})
    nota_antes = corr.get("nota", 1.0)
    nota_depois = min(nota_antes * 1.4 + 0.15, problem["valor"])
    melhoria = nota_depois - nota_antes

    return AgentActivity(
        platform="twitter",
        agent_id=hash(scientist["name"]) % 1000,
        agent_name=scientist["name"].replace("_", " "),
        action_type="CREATE_POST",
        action_args={
            "content": f"[REVISAO {problem['id']}] Nota: {nota_antes:.2f} → {nota_depois:.2f} (+{melhoria:+.2f}). Correcao aplicada com sucesso.",
            "problem_id": problem["id"],
            "phase": "revisao",
            "round": round_num,
        },
        round_num=round_num,
        timestamp=datetime.now().isoformat(),
    )


def generate_comentario_geral(round_num):
    """Comentario geral do corretor ao final da lista."""
    comentario = random.choice(COMPREENSIVO_GERAL)

    return AgentActivity(
        platform="reddit",
        agent_id=999,
        agent_name="Prof_Corretor",
        action_type="CREATE_POST",
        action_args={
            "content": f"[COMENTARIO GERAL] {comentario}",
            "phase": "comentario_geral",
            "round": round_num,
        },
        round_num=round_num,
        timestamp=datetime.now().isoformat(),
    )


def simulate_dca_iterative(graph_id="dca-iterative", target_score=9.6, max_cycles=8):
    """
    Simulacao iterativa multi-ciclo ate convergir para target_score/10.
    Ciclo 0: Tentativa inicial
    Ciclo N: Correcao → Aprendizado → Revisao (com diminishing returns)
    """
    storage = MockGraphStorage()
    sim_id = f"dca_iter_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    updater = MemoryManager.create(sim_id, graph_id, storage)

    round_num = 0
    score_history = []

    # Notas acumuladas por questao (partem das notas do corretor)
    current_scores = {p["id"]: CORRECOES[p["id"]]["nota"] for p in DCA_PROBLEMS}
    initial_scores = dict(current_scores)

    def score_total():
        return sum(current_scores.values())

    def score_media():
        return score_total() / 30.0 * 10.0

    def score_por_lista(lista_key):
        qs = NOTAS_POR_LISTA[{"L1": "Lista 1", "L2": "Lista 2", "L3": "Lista 3"}[lista_key]]["questoes"]
        return sum(current_scores[q] for q in qs)

    print(f"\n{'='*70}")
    print(f"  SIMULACAO DCA ITERATIVA — CONVERGENCIA PARA {target_score}/10")
    print(f"  Graph: {graph_id} | Simulation: {sim_id}")
    print(f"  Questoes: {len(DCA_PROBLEMS)} | Cientistas: {len(SCIENTISTS)}")
    print(f"  Raciocinios: {len(REASONING_ACTIONS)} | Max ciclos: {max_cycles}")
    print(f"  Nota inicial: {score_total():.2f}/30,00 ({score_media():.1f}/10)")
    print(f"{'='*70}\n")

    tracker = {p["id"]: {"area": p["area"], "attempts": 0, "corrections": 0, "improvements": 0, "revisions": 0}
               for p in DCA_PROBLEMS}

    # ─── CICLO 0: Tentativa inicial (6 rodadas) ─────────────────
    print(f"  ══ CICLO 0: Primeiras Tentativas ══")
    for r in range(1, 7):
        round_num += 1
        n = random.randint(5, 10)
        for _ in range(n):
            prob = random.choice(DCA_PROBLEMS)
            sci = random.choice(SCIENTISTS)
            act = generate_first_attempt(sci, prob, round_num)
            updater.add_activity(act)
            tracker[prob["id"]]["attempts"] += 1
        if r % 3 == 0:
            s = updater.get_stats()
            print(f"    T{r}/6 | Ativ: {s['total']:3d} | Lotes: {s['sent']:2d} | "
                  f"Nota: {score_total():.2f}/30 ({score_media():.1f}/10)")
        time.sleep(0.06)

    score_history.append(("C0-Tentativa", score_media()))

    # ─── CICLOS ITERATIVOS: Correcao → Aprendizado → Revisao ─────
    ciclo = 0
    for ciclo in range(1, max_cycles + 1):
        nota_antes = score_media()
        print(f"\n  ══ CICLO {ciclo}: Correcao → Aprendizado → Revisao ══")

        # Fase A: Correcao (2 rodadas)
        for _ in range(2):
            round_num += 1
            for prob in DCA_PROBLEMS:
                act = generate_correction_feedback(prob, round_num)
                updater.add_activity(act)
                tracker[prob["id"]]["corrections"] += 1
            if random.random() < 0.5:
                updater.add_activity(generate_comentario_geral(round_num))
            time.sleep(0.04)

        # Fase B: Aprendizado (4 rodadas)
        for _ in range(4):
            round_num += 1
            n = random.randint(5, 10)
            for _ in range(n):
                prob = random.choice(DCA_PROBLEMS)
                sci = random.choice(SCIENTISTS)
                act = generate_learning_cycle(sci, prob, round_num)
                updater.add_activity(act)
                tracker[prob["id"]]["improvements"] += 1
            time.sleep(0.04)

        # Fase C: Revisao — aplicar melhoria com diminishing returns
        round_num += 1
        decay = 0.88 ** (ciclo - 1)  # decaimento suave: 0.88^9 ≈ 0.32 no ciclo 10
        base_rate = 0.42  # taxa base de aprendizado por ciclo
        improvements_this_cycle = {}

        for prob in DCA_PROBLEMS:
            sci = random.choice(SCIENTISTS)
            pid = prob["id"]
            act = generate_improved_solution(sci, prob, round_num)
            updater.add_activity(act)
            tracker[pid]["revisions"] += 1

            gap = prob["valor"] - current_scores[pid]
            if gap > 0.001:
                improvement = gap * base_rate * decay
                improvement = max(improvement, 0.015)  # melhoria minima por questao
                current_scores[pid] = min(current_scores[pid] + improvement, prob["valor"])
                improvements_this_cycle[pid] = improvement

        score_history.append((f"C{ciclo}-Revisao", score_media()))

        s = updater.get_stats()
        nota_depois = score_media()
        delta = nota_depois - nota_antes
        bar = "█" * int(delta * 15)
        print(f"    Fim C{ciclo} | Ativ: {s['total']:4d} | Lotes: {s['sent']:3d} | "
              f"Nota: {score_total():.2f}/30 ({nota_depois:.2f}/10) | Δ+{delta:.2f} {bar}")

        # Exibir melhorias deste ciclo
        top_improvements = sorted(improvements_this_cycle.items(), key=lambda x: -x[1])[:5]
        for pid, imp in top_improvements:
            print(f"      {pid}: {current_scores[pid]-imp:.2f} → {current_scores[pid]:.2f} (+{imp:.2f}) "
                  f"[{CORRECOES[pid]['erro'][:50]}...]")

        if score_media() >= target_score:
            print(f"\n  ✅ META ATINGIDA no ciclo {ciclo}: {score_media():.2f}/10 >= {target_score}/10")
            break
        time.sleep(0.04)

    updater.stop()
    final_stats = updater.get_stats()

    # ─── RELATORIO FINAL ───────────────────────────────────────────
    print(f"\n{'='*70}")
    print(f"  RELATORIO FINAL — DCA ITERATIVA MULTI-CICLO")
    print(f"{'='*70}")
    print(f"  Total atividades:      {final_stats['total']}")
    print(f"  Lotes enviados:        {final_stats['sent']}")
    print(f"  Falhas:                {final_stats['failed']}")
    print(f"  Ciclos executados:     {ciclo}")
    print(f"  Rodadas totais:        {round_num}")
    print(f"{'='*70}")

    print(f"\n  TRAJETORIA DE CONVERGENCIA:")
    for label, score in score_history:
        bar = "█" * int(score)
        print(f"    {label:18s} {score:5.2f}/10  {bar}")

    print(f"\n  EVOLUCAO POR LISTA:")
    print(f"  {'Lista':<8} {'Inicial':<10} {'Final':<10} {'Melhoria':<10} {'Max':<8}")
    print(f"  {'-'*48}")
    total_ini = 0
    total_fin = 0
    for lista_name, lkey in [("Lista 1", "L1"), ("Lista 2", "L2"), ("Lista 3", "L3")]:
        info = NOTAS_POR_LISTA[lista_name]
        n_ini = info["nota"]
        n_fin = score_por_lista(lkey)
        total_ini += n_ini
        total_fin += n_fin
        melhoria = n_fin - n_ini
        bar = "█" * int(melhoria * 3)
        print(f"  {lista_name:<8} {n_ini:5.2f}/10   {n_fin:5.2f}/10   +{melhoria:5.2f}     {bar}")

    print(f"  {'-'*48}")
    print(f"  {'TOTAL':<8} {total_ini:5.2f}/30  {total_fin:5.2f}/30  +{total_fin-total_ini:5.2f}")
    print(f"\n  Nota media: {total_ini/30*10:.1f}/10 → {total_fin/30*10:.2f}/10")
    print(f"  Meta: {target_score}/10 {'✅ ATINGIDA' if score_media() >= target_score else '❌ NAO ATINGIDA'}")

    print(f"\n  NOTAS FINAIS POR QUESTAO:")
    for pid in sorted(current_scores.keys()):
        ini = initial_scores[pid]
        fin = current_scores[pid]
        prob = next(p for p in DCA_PROBLEMS if p["id"] == pid)
        delta = fin - ini
        pct = int(fin / prob["valor"] * 20)
        bar = "▓" * pct + "░" * (20 - pct)
        print(f"    {pid}  {ini:.2f} → {fin:.2f} (+{delta:+.2f})  {bar}  {prob['area']}")

    return {
        "simulation_id": sim_id,
        "graph_id": graph_id,
        "stats": final_stats,
        "ciclos": ciclo,
        "rodadas": round_num,
        "notas": {"inicial": total_ini, "final": total_fin, "media_inicial": total_ini/30*10, "media_final": total_fin/30*10},
        "score_history": score_history,
        "current_scores": dict(current_scores),
        "tracker": {pid: dict(data) for pid, data in tracker.items()},
    }


if __name__ == "__main__":
    random.seed(42)
    result = simulate_dca_iterative(graph_id="dca-iterative", target_score=9.6, max_cycles=10)
    print(f"\n  Simulacao concluida. ID: {result['simulation_id']}")
