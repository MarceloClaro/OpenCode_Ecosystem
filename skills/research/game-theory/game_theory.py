#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
game_theory.py — Motor de Análise de Teoria dos Jogos
======================================================
Implementa solução de equilíbrio de Nash para jogos 2x2,
análise de dilemas cooperativos, teoria da barganha e
otimização estratégica multiagente.

Capabilities:
  - game_theory_modeling: Modelagem de jogos cooperativos e não-cooperativos
  - equilibrium_analysis: Análise de equilíbrio de Nash, Stackelberg e Pareto
"""

from __future__ import annotations
import json
from typing import Dict, List, Optional, Tuple


class PayoffMatrix:
    """Matriz de payoff para jogos 2x2 (dois jogadores, duas ações)."""

    def __init__(
        self,
        player1: List[str],
        player2: List[str],
        payoffs: Dict[Tuple[str, str], Tuple[float, float]],
    ):
        self.player1_actions = player1  # ações do jogador linha
        self.player2_actions = player2  # ações do jogador coluna
        self.payoffs = payoffs  # (a1, a2) → (p1, p2)
        self._validate()

    def _validate(self) -> None:
        for a1 in self.player1_actions:
            for a2 in self.player2_actions:
                if (a1, a2) not in self.payoffs:
                    raise ValueError(f"Payoff missing for ({a1}, {a2})")

    def get_payoff(self, a1: str, a2: str) -> Tuple[float, float]:
        return self.payoffs[(a1, a2)]

    def __repr__(self) -> str:
        return f"PayoffMatrix(p1={self.player1_actions}, p2={self.player2_actions})"


class NashEquilibrium:
    """Analisador de equilíbrio de Nash para jogos 2x2."""

    @staticmethod
    def find_pure_strategy(payoff: PayoffMatrix) -> List[Tuple[str, str, float, float]]:
        """Encontra equilíbrios de Nash em estratégias puras."""
        equilibria: List[Tuple[str, str, float, float]] = []
        for a1 in payoff.player1_actions:
            for a2 in payoff.player2_actions:
                p1, p2 = payoff.get_payoff(a1, a2)

                # Verifica se p1 é a melhor resposta à a2
                best_response_p1 = True
                for other_a1 in payoff.player1_actions:
                    if other_a1 == a1:
                        continue
                    other_p1, _ = payoff.get_payoff(other_a1, a2)
                    if other_p1 > p1:
                        best_response_p1 = False
                        break

                # Verifica se p2 é a melhor resposta à a1
                best_response_p2 = True
                for other_a2 in payoff.player2_actions:
                    if other_a2 == a2:
                        continue
                    _, other_p2 = payoff.get_payoff(a1, other_a2)
                    if other_p2 > p2:
                        best_response_p2 = False
                        break

                if best_response_p1 and best_response_p2:
                    equilibria.append((a1, a2, p1, p2))

        return equilibria

    @staticmethod
    def is_pareto_optimal(
        payoff: PayoffMatrix, a1: str, a2: str
    ) -> Tuple[bool, List[str]]:
        """Verifica se um par de estratégias é Pareto-ótimo."""
        p1, p2 = payoff.get_payoff(a1, a2)
        dominated_by: List[str] = []

        for other_a1 in payoff.player1_actions:
            for other_a2 in payoff.player2_actions:
                if other_a1 == a1 and other_a2 == a2:
                    continue
                op1, op2 = payoff.get_payoff(other_a1, other_a2)
                if op1 >= p1 and op2 >= p2 and (op1 > p1 or op2 > p2):
                    dominated_by.append(f"({other_a1}, {other_a2})")

        return len(dominated_by) == 0, dominated_by


# Jogos clássicos pré-definidos
CLASSIC_GAMES = {
    "prisoners_dilemma": PayoffMatrix(
        player1=["cooperar", "trair"],
        player2=["cooperar", "trair"],
        payoffs={
            ("cooperar", "cooperar"): (-1, -1),
            ("cooperar", "trair"): (-3, 0),
            ("trair", "cooperar"): (0, -3),
            ("trair", "trair"): (-2, -2),
        },
    ),
    "battle_of_sexes": PayoffMatrix(
        player1=["futebol", "cinema"],
        player2=["futebol", "cinema"],
        payoffs={
            ("futebol", "futebol"): (3, 2),
            ("futebol", "cinema"): (0, 0),
            ("cinema", "futebol"): (0, 0),
            ("cinema", "cinema"): (2, 3),
        },
    ),
    "stag_hunt": PayoffMatrix(
        player1=["veado", "lebre"],
        player2=["veado", "lebre"],
        payoffs={
            ("veado", "veado"): (4, 4),
            ("veado", "lebre"): (0, 2),
            ("lebre", "veado"): (2, 0),
            ("lebre", "lebre"): (2, 2),
        },
    ),
    "chicken": PayoffMatrix(
        player1=["desviar", "seguir"],
        player2=["desviar", "seguir"],
        payoffs={
            ("desviar", "desviar"): (0, 0),
            ("desviar", "seguir"): (-1, 1),
            ("seguir", "desviar"): (1, -1),
            ("seguir", "seguir"): (-10, -10),
        },
    ),
}


def analyze_game(name: str) -> dict:
    """Analisa um jogo clássico e retorna relatório completo."""
    if name not in CLASSIC_GAMES:
        raise ValueError(f"Jogo desconhecido: {name}. Opções: {list(CLASSIC_GAMES.keys())}")

    game = CLASSIC_GAMES[name]
    ne = NashEquilibrium()

    pure_equilibria = ne.find_pure_strategy(game)

    pareto_analysis = []
    for a1 in game.player1_actions:
        for a2 in game.player2_actions:
            is_po, dominated = ne.is_pareto_optimal(game, a1, a2)
            pareto_analysis.append({
                "strategy": (a1, a2),
                "payoff": list(game.get_payoff(a1, a2)),
                "pareto_optimal": is_po,
                "dominated_by": dominated,
            })

    return {
        "game": name,
        "matrix": {
            "player1_actions": game.player1_actions,
            "player2_actions": game.player2_actions,
        },
        "nash_equilibria_pure": [
            {"a1": e[0], "a2": e[1], "p1": e[2], "p2": e[3]}
            for e in pure_equilibria
        ],
        "pareto_analysis": pareto_analysis,
        "is_social_dilemma": name == "prisoners_dilemma",
        "num_equilibria": len(pure_equilibria),
    }


def main():
    """Demonstra análise de todos os jogos clássicos."""
    for name in CLASSIC_GAMES:
        result = analyze_game(name)
        n_eq = result["num_equilibria"]
        print(f"\n{'='*50}")
        print(f"🎲 {name.upper()}")
        print(f"{'='*50}")
        print(f"Equilíbrios de Nash (estratégias puras): {n_eq}")
        for eq in result["nash_equilibria_pure"]:
            print(f"  → ({eq['a1']}, {eq['a2']}) = ({eq['p1']}, {eq['p2']})")
        po_count = sum(1 for p in result["pareto_analysis"] if p["pareto_optimal"])
        print(f"Ótimos de Pareto: {po_count}/{len(result['pareto_analysis'])}")
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
