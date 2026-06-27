"""
QualitativeCoder Core — Engine de Codificação Qualitativa
SPEC-048 | Ciclo R27

Engine principal que orquestra codificação, categorização, triangulação e relatórios.
Substitui NVivo 12 e MAXQDA com código aberto, validável e reproduzível.
"""
import re
import json
from typing import Any
from qualitative_coder.core.categorizer import Categorizer
from qualitative_coder.core.triangulator import Triangulator
from qualitative_coder.core.reporter import Reporter


class QualitativeCoder:
    """
    Engine principal de análise qualitativa.

    Fornece codificação automática e semi-automática de dados qualitativos,
    categorização temática, triangulação de métodos e geração de relatórios.

    Exemplo:
        >>> coder = QualitativeCoder(language="pt-br")
        >>> codes = coder.code("A resistência dos docentes é um problema.")
        >>> categories = coder.categorize(codes)
        >>> report = coder.report({"categories": categories}, format="latex")
    """

    # Padrões léxicos para detecção de códigos (PT-BR)
    LEXICAL_PATTERNS = {
        "resistencia": [
            r"resist[eê]ncia", r"resist[eê]nte", r"resistir",
            r"obst[aá]culo", r"barreira", r"entrave",
        ],
        "mudanca": [
            r"mudan[cç]a", r"transforma[cç][aã]o", r"altera[cç][aã]o",
            r"inova[cç][aã]o", r"renova[cç][aã]o",
        ],
        "implementacao": [
            r"implementa[cç][aã]o", r"execu[cç][aã]o", r"aplica[cç][aã]o",
            r"execu[cç]ar", r"implementar", r"aplicar",
        ],
        "formacao": [
            r"forma[cç][aã]o", r"capacita[cç][aã]o", r"treinamento",
            r"educa[cç][aã]o", r"aprendizagem",
        ],
        "gestao": [
            r"gest[aã]o", r"administra[cç][aã]o", r"gerenciamento",
            r"lideran[cç]a", r"dire[cç][aã]o",
        ],
        "avaliacao": [
            r"avalia[cç][aã]o", r"avaliar", r"avaliar",
            r"mensura[cç][aã]o", r"medi[cç][aã]o",
        ],
        "resistencia_mudanca": [
            r"resist[eê]ncia.*mudan[cç]a",
            r"resist[eê]ncia.*transforma[cç][aã]o",
        ],
        "barreiras_implementacao": [
            r"barreira.*implementa[cç][aã]o",
            r"obst[aá]culo.*implementa[cç][aã]o",
        ],
        "necessidade_formacao": [
            r"necessidade.*forma[cç][aã]o",
            r"necessidade.*capacita[cç][aã]o",
        ],
    }

    # Mapeamento de relações causais (para codificação axial)
    CAUSAL_MARKERS = [
        r"causou", r"causa", r"porque", r"devido", r"em fun[cç][aã]o",
        r"consequência", r"resultado", r"levou", r"gerou", r"provocou",
    ]

    def __init__(self, language: str = "pt-br"):
        """
        Inicializa o QualitativeCoder.

        Args:
            language: Código ISO do idioma (padrão: 'pt-br').
        """
        self.language = language
        self.codebook: dict[str, dict] = {}
        self.categories: list[dict] = []
        self._categorizer = Categorizer()
        self._triangulator = Triangulator()
        self._reporter = Reporter()

    def code(self, text: str, method: str = "open") -> list[dict[str, Any]]:
        """
        Codifica texto qualitativo em unidades de sentido.

        Args:
            text: Texto a ser codificado.
            method: Método de codificação ('open' ou 'axial').

        Returns:
            Lista de dicts com code, span, confidence.
        """
        if not text or not text.strip():
            return []

        results = []
        text_lower = text.lower()

        for code_name, patterns in self.LEXICAL_PATTERNS.items():
            # Pular códigos compostos no método open
            if method == "open" and "_" in code_name:
                continue

            for pattern in patterns:
                for match in re.finditer(pattern, text_lower):
                    start, end = match.start(), match.end()
                    # Calcular confiança baseada na qualidade da match
                    confidence = self._compute_confidence(match, text_lower)
                    results.append({
                        "code": code_name,
                        "span": (start, end),
                        "confidence": round(confidence, 3),
                    })

        # Para método axial, adicionar relações causais detectadas
        if method == "axial":
            results.extend(self._detect_causal_relations(text_lower, text))

        # Deduplicar por span sobreposto
        results = self._deduplicate_spans(results)

        return results

    def _compute_confidence(self, match: re.Match, text: str) -> float:
        """Calcula score de confiança baseado no contexto."""
        base = 0.7

        # Match exato (não parcial)
        if match.group() == re.sub(r'[.*+?^${}()|[\]\\]', '', match.group()):
            base += 0.1

        # Contexto rico (frase longa ao redor)
        start = max(0, match.start() - 50)
        end = min(len(text), match.end() + 50)
        context = text[start:end]
        word_count = len(context.split())
        if word_count > 8:
            base += 0.1

        # Presença de marcadores acadêmicos
        academic_markers = ["segundo", "conforme", "de acordo", "estudo", "pesquisa"]
        if any(m in context for m in academic_markers):
            base += 0.1

        return min(base, 1.0)

    def _detect_causal_relations(self, text_lower: str, original: str) -> list[dict]:
        """Detecta relações causais para codificação axial."""
        results = []
        for marker in self.CAUSAL_MARKERS:
            for match in re.finditer(marker, text_lower):
                # Encontrar códigos nas proximidades
                start = max(0, match.start() - 80)
                end = min(len(text_lower), match.end() + 80)
                context = text_lower[start:end]

                for code_name, patterns in self.LEXICAL_PATTERNS.items():
                    if "_" in code_name:  # Pular compostos
                        continue
                    for pat in patterns:
                        if re.search(pat, context):
                            results.append({
                                "code": f"relacao_causal_{code_name}",
                                "span": (start, end),
                                "confidence": 0.65,
                            })
                            break
        return results

    def _deduplicate_spans(self, results: list[dict]) -> list[dict]:
        """Remove códigos com spans sobrepostos (mantém maior confiança)."""
        if not results:
            return results

        sorted_results = sorted(results, key=lambda x: x["span"][0])
        deduplicated = [sorted_results[0]]

        for item in sorted_results[1:]:
            last = deduplicated[-1]
            if item["span"][0] >= last["span"][1]:
                deduplicated.append(item)
            elif item["confidence"] > last["confidence"]:
                deduplicated[-1] = item

        return deduplicated

    def categorize(self, codes: list[dict], method: str = "thematic") -> list[dict]:
        """
        Categoriza códigos em temas.

        Args:
            codes: Lista de códigos (output de code()).
            method: Método de categorização.

        Returns:
            Lista de categorias com codes e frequency.
        """
        return self._categorizer.categorize(codes)

    def triangulate(
        self,
        data_quant: dict,
        data_qual: list[dict],
        method: str = "convergence",
    ) -> dict:
        """
        Triangula dados quantitativos e qualitativos.

        Args:
            data_quant: Dados quantitativos (dict de métricas).
            data_qual: Dados qualitativos (lista de códigos).
            method: Método de triangulação.

        Returns:
            Dict com convergence, divergence, gaps.
        """
        return self._triangulator.triangulate(data_quant, data_qual, method)

    def report(self, data: dict, format: str = "latex") -> Any:
        """
        Gera relatório da análise.

        Args:
            data: Dict com categories e triangulation.
            format: Formato de saída ('latex', 'markdown', 'json').

        Returns:
            Relatório no formato especificado.
        """
        return self._reporter.report(data, format)

    def add_code(self, name: str, description: str = "", parent: str = None) -> None:
        """
        Adiciona código ao codebook.

        Args:
            name: Nome do código.
            description: Descrição do código.
            parent: Código pai (para hierarquia).
        """
        self.codebook[name] = {
            "description": description,
            "parent": parent,
        }

    def export_codebook(self) -> dict:
        """
        Exporta codebook como dict serializável.

        Returns:
            Dict com todos os códigos registrados.
        """
        return dict(self.codebook)
