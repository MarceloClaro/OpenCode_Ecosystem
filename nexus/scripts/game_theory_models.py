# -*- coding: utf-8 -*-
"""
Game Theory Models & Solvers — SPEC-060
=======================================
Implementa resolvedores matemáticos para 10 jogos clássicos da Teoria dos Jogos.
Integra os resultados estratégicos com o analisador lógico ARCHE RLT
e o motor causal RUMI.

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any

logger = logging.getLogger("game-theory-models")

# ═══════════════════════════════════════════════════════════════════════
# GAME SOLVER UTILITIES
# ═══════════════════════════════════════════════════════════════════════

class GameTheorySolver:
    """Biblioteca central de modelos de jogos e resolvedores de equilíbrios."""

    # 1. Dilema do Prisioneiro
    @staticmethod
    def solve_prisoners_dilemma(
        r: float = 3.0, t: float = 5.0, s: float = 0.0, p: float = 1.0
    ) -> Dict[str, Any]:
        """
        Dilema do Prisioneiro (2x2).
        R: Recompensa por cooperação, T: Tentação de trair, S: Custo de ser otário, P: Punição.
        """
        # Matriz: Cooperar (C), Desertar (D)
        # Linha: Jogador 1, Coluna: Jogador 2
        # Payoffs format: (P1, P2)
        payoffs = {
            ("C", "C"): (r, r),
            ("C", "D"): (s, t),
            ("D", "C"): (t, s),
            ("D", "D"): (p, p)
        }
        
        # PNE (Pure Nash Equilibria)
        # Sempre é (D, D) se T > R > P > S
        pne = []
        if t > r and p > s:
            pne.append(("D", "D"))
            
        return {
            "game": "Prisoner's Dilemma",
            "parameters": {"R": r, "T": t, "S": s, "P": p},
            "payoffs": {str(k): v for k, v in payoffs.items()},
            "nash_equilibria_pure": pne,
            "pareto_efficient": [("C", "C")],
            "social_optimum": ("C", "C")
        }

    # 2. Batalha dos Sexos
    @staticmethod
    def solve_battle_of_sexes(
        p1_pref: float = 3.0, p2_pref: float = 3.0, coop_val: float = 1.0
    ) -> Dict[str, Any]:
        """
        Batalha dos Sexos (2x2).
        Coordenar na opção favorita do J1 dá (p1_pref, coop_val).
        Coordenar na opção favorita do J2 dá (coop_val, p2_pref).
        Descoordenação dá (0, 0).
        """
        payoffs = {
            ("OpcaoA", "OpcaoA"): (p1_pref, coop_val),
            ("OpcaoA", "OpcaoB"): (0.0, 0.0),
            ("OpcaoB", "OpcaoA"): (0.0, 0.0),
            ("OpcaoB", "OpcaoB"): (coop_val, p2_pref)
        }
        
        pne = [("OpcaoA", "OpcaoA"), ("OpcaoB", "OpcaoB")]
        
        # Mixed strategy Nash Equilibrium calculation:
        # p = prob(OpcaoA) para J2 tal que J1 seja indiferente
        # q = prob(OpcaoA) para J1 tal que J2 seja indiferente
        # J1: p * p1_pref + (1-p)*0 = p*0 + (1-p)*coop_val  => p * p1_pref = (1-p)*coop_val => p = coop_val / (p1_pref + coop_val)
        p = round(coop_val / (p1_pref + coop_val), 4)
        q = round(p2_pref / (p2_pref + coop_val), 4)
        
        return {
            "game": "Battle of the Sexes",
            "parameters": {"p1_pref": p1_pref, "p2_pref": p2_pref, "coop_val": coop_val},
            "payoffs": {str(k): v for k, v in payoffs.items()},
            "nash_equilibria_pure": pne,
            "nash_equilibrium_mixed": {
                "player1_prob_A": q,
                "player2_prob_A": p
            }
        }

    # 3. Caça ao Cervo
    @staticmethod
    def solve_stag_hunt(
        stag_val: float = 5.0, hare_val: float = 3.0, stag_fail: float = 0.0
    ) -> Dict[str, Any]:
        """
        Caça ao Cervo (2x2).
        Caçar Cervo cooperativamente dá (stag_val, stag_val).
        Se um caça lebre e outro cervo, o do lebre ganha hare_val, o do cervo ganha stag_fail.
        Ambos lebre dá (hare_val, hare_val).
        """
        payoffs = {
            ("Cervo", "Cervo"): (stag_val, stag_val),
            ("Cervo", "Lebre"): (stag_fail, hare_val),
            ("Lebre", "Cervo"): (hare_val, stag_fail),
            ("Lebre", "Lebre"): (hare_val, hare_val)
        }
        
        # PNE
        pne = [("Cervo", "Cervo"), ("Lebre", "Lebre")]
        # Cervo-Cervo é payoff-dominant, Lebre-Lebre é risk-dominant
        
        return {
            "game": "Stag Hunt",
            "parameters": {"stag_val": stag_val, "hare_val": hare_val, "stag_fail": stag_fail},
            "payoffs": {str(k): v for k, v in payoffs.items()},
            "nash_equilibria_pure": pne,
            "payoff_dominant": ("Cervo", "Cervo"),
            "risk_dominant": ("Lebre", "Lebre")
        }

    # 4. Jogo do Frango / Gavião-Pombo
    @staticmethod
    def solve_chicken(
        v: float = 4.0, c: float = 6.0
    ) -> Dict[str, Any]:
        """
        Jogo do Frango / Hawk-Dove (2x2).
        V: Valor do recurso, C: Custo de briga/colisão.
        Pombo (C / Cooperar), Gavião (D / Desviar/Atacar).
        """
        payoffs = {
            ("Pombo", "Pombo"): (v / 2.0, v / 2.0),
            ("Pombo", "Gaviao"): (0.0, v),
            ("Gaviao", "Pombo"): (v, 0.0),
            ("Gaviao", "Gaviao"): ((v - c) / 2.0, ((v - c) / 2.0))
        }
        
        # Se C > V (colisão é pior que ficar sem nada)
        pne = [("Pombo", "Gaviao"), ("Gaviao", "Pombo")]
        
        # Misto: p = prob(Gaviao) tal que indiferente
        p = round(v / c, 4) if c > 0 else 1.0
        
        return {
            "game": "Chicken / Hawk-Dove",
            "parameters": {"V": v, "C": c},
            "payoffs": {str(k): v for k, v in payoffs.items()},
            "nash_equilibria_pure": pne,
            "nash_equilibrium_mixed": {
                "player1_prob_Gaviao": p,
                "player2_prob_Gaviao": p
            }
        }

    # 5. Par ou Ímpar
    @staticmethod
    def solve_matching_pennies() -> Dict[str, Any]:
        """Par ou Ímpar (Jogo de soma zero pura, sem PNE)."""
        payoffs = {
            ("Cara", "Cara"): (1.0, -1.0),
            ("Cara", "Coroa"): (-1.0, 1.0),
            ("Coroa", "Cara"): (-1.0, 1.0),
            ("Coroa", "Coroa"): (1.0, -1.0)
        }
        
        return {
            "game": "Matching Pennies",
            "payoffs": {str(k): v for k, v in payoffs.items()},
            "nash_equilibria_pure": [],
            "nash_equilibrium_mixed": {
                "player1_prob_Cara": 0.5,
                "player2_prob_Cara": 0.5
            }
        }

    # 6. Duopólio de Cournot
    @staticmethod
    def solve_cournot(a: float = 10.0, b: float = 1.0, c: float = 2.0) -> Dict[str, Any]:
        """
        Duopólio de Cournot (Competição simultânea de quantidade).
        P = a - b(q1 + q2), Custo = c * q
        """
        if a <= c:
            return {"game": "Cournot Duopoly", "status": "inválido (a <= c)"}
            
        q_star = (a - c) / (3.0 * b)
        price = a - b * (2.0 * q_star)
        profit = (price - c) * q_star
        
        return {
            "game": "Cournot Duopoly",
            "parameters": {"a": a, "b": b, "c": c},
            "equilibrium_quantity_each": round(q_star, 4),
            "market_price": round(price, 4),
            "profit_each": round(profit, 4)
        }

    # 7. Liderança de Stackelberg
    @staticmethod
    def solve_stackelberg(a: float = 10.0, b: float = 1.0, c: float = 2.0) -> Dict[str, Any]:
        """Liderança de Stackelberg (Competição sequencial de quantidade)."""
        if a <= c:
            return {"game": "Stackelberg", "status": "inválido"}
            
        q_leader = (a - c) / (2.0 * b)
        q_follower = (a - c) / (4.0 * b)
        price = a - b * (q_leader + q_follower)
        profit_leader = (price - c) * q_leader
        profit_follower = (price - c) * q_follower
        
        return {
            "game": "Stackelberg Leader-Follower",
            "parameters": {"a": a, "b": b, "c": c},
            "quantity_leader": round(q_leader, 4),
            "quantity_follower": round(q_follower, 4),
            "market_price": round(price, 4),
            "profit_leader": round(profit_leader, 4),
            "profit_follower": round(profit_follower, 4)
        }

    # 8. Jogo da Centopeia
    @staticmethod
    def solve_centipede(rounds: int = 4) -> Dict[str, Any]:
        """Jogo da Centopeia (Jogo sequencial, resolvido por Indução Retroativa)."""
        payoffs = []
        for r in range(rounds):
            if r % 2 == 0:
                # Turno do J1
                payoffs.append({"turn": "Player1", "take": (r + 1, r), "pass": (r, r + 2)})
            else:
                # Turno do J2
                payoffs.append({"turn": "Player2", "take": (r, r + 1), "pass": (r + 2, r)})
                
        # PNE Perfeito em Subjogos (SPNE): Trair na primeira rodada
        spne_action = "Take no turno 1"
        return {
            "game": "Centipede Game",
            "parameters": {"rounds": rounds},
            "payoffs_sequence": payoffs,
            "subgame_perfect_equilibrium": spne_action,
            "cooperative_payoff_last_round": (rounds, rounds + 1) if rounds % 2 == 0 else (rounds + 1, rounds)
        }

    # 9. Jogo do Ultimato
    @staticmethod
    def solve_ultimatum(total_amount: float = 100.0) -> Dict[str, Any]:
        """Jogo do Ultimato (Proposta e Aceitação/Rejeição)."""
        # Raciocínio racional clássico: J1 oferece o mínimo positivo (epsilon), J2 aceita.
        epsilon = 1.0  # Menor fração/unidade inteira
        spne_offer = epsilon
        spne_payoffs = (total_amount - epsilon, epsilon)
        
        return {
            "game": "Ultimatum Game",
            "total_amount": total_amount,
            "spne_proposal_each": {"proposer": total_amount - epsilon, "responder": epsilon},
            "spne_outcome": "Aceito",
            "behavioral_fairness_average_offer": total_amount * 0.4  # Estudos empíricos mostram ~40%
        }

    # 10. Jogo dos Bens Públicos
    @staticmethod
    def solve_public_goods(
        n: int = 4, contribution_limit: float = 10.0, multiplier: float = 2.0
    ) -> Dict[str, Any]:
        """
        Jogo dos Bens Públicos.
        Se multiplier < N, cooperar não é Nash Equilibrium individual (Free riding dominante).
        """
        # Equilíbrio de Nash: Contribuição zero
        nas_contribution = 0.0
        
        # Social optimum: Contribuição máxima
        social_opt_contribution = contribution_limit
        social_opt_payoff = (contribution_limit * n * multiplier) / n
        
        return {
            "game": "Public Goods Game",
            "parameters": {"N": n, "limit": contribution_limit, "multiplier": multiplier},
            "nash_equilibrium_contribution_each": nas_contribution,
            "social_optimum_contribution_each": social_opt_contribution,
            "social_optimum_payoff_each": social_opt_payoff,
            "free_rider_payoff_in_social_optimum": (contribution_limit * (n - 1) * multiplier) / n
        }

    @classmethod
    def solve_game(cls, game_name: str, params: Optional[dict] = None) -> Dict[str, Any]:
        """Resolve qualquer um dos 10 jogos com base no nome."""
        params = params or {}
        g_lower = game_name.lower().replace("_", " ").replace("'", "")
        
        if "prisoner" in g_lower:
            return cls.solve_prisoners_dilemma(
                params.get("R", 3.0), params.get("T", 5.0), params.get("S", 0.0), params.get("P", 1.0)
            )
        elif "battle" in g_lower or "sexes" in g_lower:
            return cls.solve_battle_of_sexes(
                params.get("p1_pref", 3.0), params.get("p2_pref", 3.0), params.get("coop_val", 1.0)
            )
        elif "stag" in g_lower or "cervo" in g_lower:
            return cls.solve_stag_hunt(
                params.get("stag_val", 5.0), params.get("hare_val", 3.0), params.get("stag_fail", 0.0)
            )
        elif "chicken" in g_lower or "frango" in g_lower or "dove" in g_lower:
            return cls.solve_chicken(
                params.get("V", 4.0), params.get("C", 6.0)
            )
        elif "matching" in g_lower or "pennies" in g_lower or "par" in g_lower:
            return cls.solve_matching_pennies()
        elif "cournot" in g_lower:
            return cls.solve_cournot(
                params.get("a", 10.0), params.get("b", 1.0), params.get("c", 2.0)
            )
        elif "stackelberg" in g_lower:
            return cls.solve_stackelberg(
                params.get("a", 10.0), params.get("b", 1.0), params.get("c", 2.0)
            )
        elif "centipede" in g_lower or "centopeia" in g_lower:
            return cls.solve_centipede(params.get("rounds", 4))
        elif "ultimatum" in g_lower or "ultimato" in g_lower:
            return cls.solve_ultimatum(params.get("total_amount", 100.0))
        elif "public" in g_lower or "bens" in g_lower:
            return cls.solve_public_goods(
                params.get("N", 4), params.get("limit", 10.0), params.get("multiplier", 2.0)
            )
        else:
            raise ValueError(f"Jogo desconhecido: {game_name}")


# ═══════════════════════════════════════════════════════════════════════
# ARCHE & RUMI INTEGRATIONS
# ═══════════════════════════════════════════════════════════════════════

def convert_game_to_rlt(game_name: str, params: Optional[dict] = None) -> Dict[str, Any]:
    """Converte a resolução do jogo em um RLTNode (árvore lógica ARCHE RLT)."""
    # Importação dinâmica de RLTNode e PeirceType
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "skills" / "system" / "reasoning-orchestrator"))
    from arche_rlt import RLTNode, PeirceType

    res = GameTheorySolver.solve_game(game_name, params)
    
    # Criar nó raiz
    root = RLTNode(
        inference_type=PeirceType.DEDUCTION_RULE,
        premise=f"Modelagem do jogo '{res['game']}' com parametros {params or 'padrao'}.",
        conclusion=f"Equilibrio de escolha obtido via teoria dos jogos.",
        confidence=1.0,
        metadata={"game_results": res}
    )
    
    # Adicionar nós filhos representando premissas individuais de payoffs e o equilíbrio
    if "nash_equilibria_pure" in res and res["nash_equilibria_pure"]:
        eq_node = RLTNode(
            inference_type=PeirceType.DEDUCTION_CASE,
            premise=f"Os jogadores sao agentes racionais que buscam maximizar seus payoffs individuais.",
            conclusion=f"Equilibrio de Nash Puro (PNE): {res['nash_equilibria_pure']}",
            confidence=0.95
        )
        root.add_child(eq_node)
        
    if "subgame_perfect_equilibrium" in res:
        spne_node = RLTNode(
            inference_type=PeirceType.DEDUCTION_CASE,
            premise=f"Resolucao do jogo sequencial por inducao retroativa (Backwards Induction).",
            conclusion=f"Equilibrio Perfeito em Subjogos (SPNE): {res['subgame_perfect_equilibrium']}",
            confidence=0.98
        )
        root.add_child(spne_node)
        
    return root.to_dict()


def convert_game_to_rumi_hypotheses(game_name: str, params: Optional[dict] = None) -> List[Dict[str, Any]]:
    """Converte dinâmicas de payoffs do jogo em hipóteses causais RUMI."""
    res = GameTheorySolver.solve_game(game_name, params)
    hypotheses = []
    
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from rumi_causal_discovery import CausalHypothesis, HypothesisStatus

    # Hipótese 1: Incentivo individual vs. Cooperação
    h1 = CausalHypothesis(
        cause=f"Payoffs desfavoraveis a cooperacao no jogo {res['game']}",
        effect=f"Comportamento de desertar ou livre-carona (free riding) dos agentes",
        mechanism=f"Minimizacao de prejuizos ou maximizacao de utilidade racional imediata de Nash",
        confidence=0.85,
        status=HypothesisStatus.PROPOSED
    )
    h1.score = 0.85
    h1.evidence.append(f"Retorno do equilibrio: {res.get('nash_equilibria_pure') or res.get('subgame_perfect_equilibrium')}")
    hypotheses.append(h1.to_dict())

    # Hipótese 2: Estratégias mistas (se aplicável)
    if "nash_equilibrium_mixed" in res:
        h2 = CausalHypothesis(
            cause=f"Ausencia de Equilibrio de Nash puro de coordenacao no jogo {res['game']}",
            effect=f"Aleatorizacao de escolha/acoes com frequencia calibrada",
            mechanism=f"Indiferenca de payoffs esperados (Estrategias mistas)",
            confidence=0.90,
            status=HypothesisStatus.PROPOSED
        )
        h2.score = 0.90
        hypotheses.append(h2.to_dict())

    return hypotheses


if __name__ == "__main__":
    # Teste rápido
    sol = GameTheorySolver.solve_game("prisoners_dilemma")
    print(sol)
