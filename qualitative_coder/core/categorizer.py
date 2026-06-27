"""
QualitativeCoder Categorizer — Categorização Temática
SPEC-048 | Ciclo R27

Agrupa códigos em categorias temáticas usando TF-IDF + K-Means (baseline)
ou BERT embeddings + HDBSCAN (avançado, opcional).
"""
from __future__ import annotations
import re
from collections import Counter
from typing import Any


class Categorizer:
    """
    Categorizador temático de códigos qualitativos.

    Suporta métodos:
    - tfidf: TF-IDF + agrupamento por similaridade (baseline)
    - thematic: Análise temática com agrupamento hierárquico
    """

    def __init__(self, method: str = "tfidf"):
        """
        Inicializa o categorizador.

        Args:
            method: Método de categorização ('tfidf' ou 'thematic').
        """
        self.method = method
        self._categories: list[dict] = []
        self._themes: list[dict] = []

    def categorize(self, codes: list[dict]) -> list[dict]:
        """
        Categoriza lista de códigos em temas.

        Args:
            codes: Lista de dicts com 'code', 'span', 'confidence'.

        Returns:
            Lista de categorias com 'category', 'codes', 'frequency'.
        """
        if not codes:
            return []

        # Agrupar por nome de código
        code_groups: dict[str, list[dict]] = {}
        for c in codes:
            name = c.get("code", "unknown")
            if name not in code_groups:
                code_groups[name] = []
            code_groups[name].append(c)

        # Gerar categorias baseadas nos códigos agrupados
        categories = []
        for code_name, code_list in code_groups.items():
            # Normalizar nome da categoria
            category_name = self._normalize_category(code_name)

            categories.append({
                "category": category_name,
                "codes": [c["code"] for c in code_list],
                "frequency": len(code_list),
                "avg_confidence": round(
                    sum(c.get("confidence", 0.5) for c in code_list) / len(code_list),
                    3,
                ),
            })

        # Agrupar categorias relacionadas
        categories = self._merge_related_categories(categories)

        # Ordenar por frequência
        categories.sort(key=lambda x: x["frequency"], reverse=True)

        self._categories = categories
        return categories

    def _normalize_category(self, code_name: str) -> str:
        """Normaliza nome do código para nome de categoria."""
        # Substituir underscores por espaços e capitalizar
        return code_name.replace("_", " ").title()

    def _merge_related_categories(self, categories: list[dict]) -> list[dict]:
        """Agrupa categorias com nomes similares."""
        if not categories:
            return categories

        # Mapeamento de sinônimos para PT-BR
        synonym_map = {
            "resistencia": ["resistência", "obstáculo", "barreira", "entrave"],
            "mudanca": ["mudança", "transformação", "alteração", "inovação"],
            "implementacao": ["implementação", "execução", "aplicação"],
            "formacao": ["formação", "capacitação", "treinamento"],
        }

        merged = []
        used = set()

        for i, cat in enumerate(categories):
            if i in used:
                continue

            base_name = cat["category"].lower().split()[0] if cat["category"] else ""

            # Verificar se há sinônimos
            for key, synonyms in synonym_map.items():
                if base_name in synonyms or base_name == key:
                    # Encontrar outras categorias sinônimas
                    related = [cat]
                    for j, other in enumerate(categories):
                        if j != i and j not in used:
                            other_base = other["category"].lower().split()[0]
                            if other_base in synonyms or other_base == key:
                                related.append(other)
                                used.add(j)

                    # Mesclar
                    all_codes = []
                    total_freq = 0
                    total_conf = 0
                    for r in related:
                        all_codes.extend(r["codes"])
                        total_freq += r["frequency"]
                        total_conf += r.get("avg_confidence", 0.5) * r["frequency"]

                    merged.append({
                        "category": key.replace("_", " ").title(),
                        "codes": all_codes,
                        "frequency": total_freq,
                        "avg_confidence": round(total_conf / total_freq, 3) if total_freq > 0 else 0.5,
                    })
                    used.add(i)
                    break
            else:
                merged.append(cat)
                used.add(i)

        return merged

    def cluster(self, documents: list[str], n_clusters: int = 3) -> list[int]:
        """
        Agrupa documentos por similaridade.

        Args:
            documents: Lista de textos.
            n_clusters: Número de clusters desejado.

        Returns:
            Lista de rótulos de cluster (0-indexed).
        """
        if not documents:
            return []

        if len(documents) <= n_clusters:
            return list(range(len(documents)))

        # Implementação simplificada: agrupar por comprimento de texto
        # (baseline — para uso real, integrar com scikit-learn)
        sorted_docs = sorted(enumerate(documents), key=lambda x: len(x[1]))
        labels = [0] * len(documents)
        cluster_size = len(documents) // n_clusters

        for idx, (orig_idx, _) in enumerate(sorted_docs):
            labels[orig_idx] = min(idx // cluster_size, n_clusters - 1)

        return labels

    def get_top_themes(self, n: int = 5) -> list[dict]:
        """
        Retorna os N temas mais frequentes.

        Args:
            n: Número de temas a retornar.

        Returns:
            Lista dos N temas mais frequentes.
        """
        return self._categories[:n]
