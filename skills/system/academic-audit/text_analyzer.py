#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TextAnalyzer v1.0 — Nuvem de Palavras + Analise de Frequencia
===============================================================
Complementa o NVivo11 com analise quantitativa de corpus textual.
Integrado ao AcademicAuditTrail e NoologicalScanner.

Funcionalidades:
  1. WordCloud — nuvem de palavras (ASCII + JSON para visualizacao)
  2. FrequencyAnalysis — frequencia de termos, stopwords PT-BR
  3. NGramAnalysis — bigramas e trigramas
  4. TF-IDF — importancia relativa de termos no corpus
  5. Concordance — contexto de ocorrencia (KWIC)

Uso:
  from text_analyzer import TextAnalyzer
  ta = TextAnalyzer()
  ta.analyze(corpus_text)
  ta.wordcloud(output="wordcloud.json")
  ta.frequency_report()
"""

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Stopwords PT-BR (palavras comuns sem valor analitico)
STOPWORDS_PTBR = {
    "o", "a", "os", "as", "um", "uma", "uns", "umas",
    "de", "do", "da", "dos", "das", "no", "na", "nos", "nas",
    "em", "por", "para", "com", "sem", "sob", "sobre",
    "e", "ou", "mas", "que", "se", "nao", "sim",
    "ele", "ela", "eles", "elas", "eu", "voce", "nos",
    "meu", "minha", "seus", "suas", "este", "esta", "isto",
    "isso", "aquilo", "aqui", "ali", "la",
    "muito", "pouco", "mais", "menos", "bem", "mal",
    "foi", "era", "sao", "ser", "estar", "tem", "ha",
    "entre", "sobre", "ate", "desde", "apos", "antes",
    "durante", "contra", "como", "quando", "onde", "porque",
    "dos", "das", "pelo", "pela", "pelos", "pelas",
}


@dataclass
class WordData:
    """Dados de uma palavra na analise."""
    word: str
    count: int
    frequency: float = 0.0  # frequencia relativa (0-1)
    tfidf: float = 0.0      # TF-IDF (se calculado)
    rank: int = 0            # posicao no ranking


class TextAnalyzer:
    """Analisador de texto com nuvem de palavras e frequencia.

    Substitui funcionalidades do NVivo11 com integracao ao ecossistema.
    """

    def __init__(self, stopwords: set[str] | None = None, min_len: int = 3):
        self.stopwords = stopwords or STOPWORDS_PTBR
        self.min_len = min_len
        self.corpus: str = ""
        self.word_counts: Counter[str] = Counter()
        self.word_data: list[WordData] = []
        self.total_words: int = 0
        self.unique_words: int = 0

    def analyze(self, corpus: str) -> dict[str, Any]:
        """Analisa um corpus textual completo.

        Args:
            corpus: Texto completo para analise

        Returns:
            Dict com metricas da analise
        """
        self.corpus = corpus
        text_lower = corpus.lower()

        # Tokenizar (remover pontuacao, numeros)
        tokens = re.findall(r'\b[a-záàâãéêíóôõúç]{3,}\b', text_lower)

        # Filtrar stopwords
        filtered = [t for t in tokens if t not in self.stopwords]

        self.word_counts = Counter(filtered)
        self.total_words = len(filtered)
        self.unique_words = len(self.word_counts)

        # Criar WordData ordenado
        self.word_data = []
        for rank, (word, count) in enumerate(self.word_counts.most_common(), 1):
            wd = WordData(
                word=word,
                count=count,
                frequency=count / max(1, self.total_words),
                rank=rank,
            )
            self.word_data.append(wd)

        return {
            "total_words": self.total_words,
            "unique_words": self.unique_words,
            "diversity_ratio": round(self.unique_words / max(1, self.total_words), 3),
            "top_words": [(w.word, w.count) for w in self.word_data[:20]],
        }

    def wordcloud_data(self, top_n: int = 100) -> list[dict[str, Any]]:
        """Gera dados para nuvem de palavras (formato JSON).

        Returns:
            Lista de dicts com word, count, size (para renderizacao)
        """
        if not self.word_data:
            return []

        max_count = self.word_data[0].count if self.word_data else 1
        result = []
        for wd in self.word_data[:top_n]:
            # Tamanho proporcional: 10px a 80px
            size = max(10, int(80 * wd.count / max_count))
            result.append({
                "word": wd.word,
                "count": wd.count,
                "frequency": round(wd.frequency, 4),
                "size": size,
                "rank": wd.rank,
            })
        return result

    def frequency_report(self, top_n: int = 30) -> str:
        """Gera relatorio de frequencia em Markdown.

        Args:
            top_n: Numero de palavras no top

        Returns:
            Relatorio Markdown formatado
        """
        if not self.word_data:
            return "Nenhum dado analisado."

        lines = [
            "# Analise de Frequencia Textual",
            "",
            f"**Total de palavras**: {self.total_words:,}",
            f"**Palavras unicas**: {self.unique_words:,}",
            f"**Diversidade lexical**: {self.unique_words/max(1,self.total_words):.2%}",
            "",
            f"## Top {top_n} Palavras",
            "",
            "| # | Palavra | Frequencia | % | Barra |",
            "|:--:|---------|:---------:|:--:|-------|",
        ]

        for wd in self.word_data[:top_n]:
            pct = wd.frequency * 100
            bar_len = int(pct * 2)  # escala visual
            bar = "#" * min(bar_len, 40)
            lines.append(f"| {wd.rank} | {wd.word} | {wd.count:,} | {pct:.1f}% | {bar} |")

        return "\n".join(lines)

    def ngram_analysis(self, n: int = 2, top_n: int = 20) -> list[tuple[str, int]]:
        """Analise de n-gramas (bigramas, trigramas).

        Args:
            n: Tamanho do n-grama (2=bigrama, 3=trigrama)
            top_n: Quantos retornar

        Returns:
            Lista de (ngrama, contagem)
        """
        text_lower = self.corpus.lower()
        tokens = re.findall(r'\b[a-záàâãéêíóôõúç]{3,}\b', text_lower)
        filtered = [t for t in tokens if t not in self.stopwords]

        ngrams = []
        for i in range(len(filtered) - n + 1):
            ngram = " ".join(filtered[i:i+n])
            ngrams.append(ngram)

        return Counter(ngrams).most_common(top_n)

    def tfidf_analysis(self, documents: list[str] | None = None) -> list[WordData]:
        """Calcula TF-IDF para o corpus.

        TF-IDF = Term Frequency * Inverse Document Frequency
        Mede a importancia relativa de uma palavra no documento
        em relacao a uma colecao de documentos.

        Args:
            documents: Lista de documentos para calcular IDF.
                      Se None, usa apenas o corpus atual (TF puro).

        Returns:
            Lista de WordData com tfidf preenchido
        """
        if not documents:
            documents = [self.corpus]

        num_docs = len(documents)
        for wd in self.word_data:
            # IDF: log(N / df), onde df = numero de docs que contem a palavra
            doc_count = sum(1 for doc in documents if wd.word in doc.lower())
            idf = __import__('math').log(num_docs / max(1, doc_count))
            wd.tfidf = round(wd.frequency * idf, 4)

        return sorted(self.word_data, key=lambda x: x.tfidf, reverse=True)

    def concordance(self, word: str, context_size: int = 40) -> list[str]:
        """Busca concordancia (KWIC — Key Word In Context).

        Mostra todas as ocorrencias de uma palavra com contexto ao redor.

        Args:
            word: Palavra a buscar
            context_size: Numero de caracteres de contexto (cada lado)

        Returns:
            Lista de linhas de concordancia
        """
        results = []
        text_lower = self.corpus.lower()
        word_lower = word.lower()
        idx = 0

        while True:
            idx = text_lower.find(word_lower, idx)
            if idx == -1:
                break

            start = max(0, idx - context_size)
            end = min(len(text_lower), idx + len(word) + context_size)
            left = self.corpus[start:idx].strip()
            right = self.corpus[idx+len(word):end].strip()
            results.append(f"...{left} **{self.corpus[idx:idx+len(word)]}** {right}...")
            idx += 1

        return results

    def save_wordcloud_json(self, output_path: str | Path, top_n: int = 100) -> Path:
        """Salva dados da nuvem de palavras em JSON.

        Args:
            output_path: Caminho do arquivo de saida
            top_n: Numero de palavras

        Returns:
            Path do arquivo salvo
        """
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "words": self.wordcloud_data(top_n),
            "metadata": {
                "total_words": self.total_words,
                "unique_words": self.unique_words,
                "diversity": round(self.unique_words / max(1, self.total_words), 3),
            },
        }
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    def save_frequency_report(self, output_path: str | Path) -> Path:
        """Salva relatorio de frequencia em Markdown."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.frequency_report(), encoding="utf-8")
        return path

    @staticmethod
    def from_audit_trail(audit_trail: Any) -> TextAnalyzer:
        """Cria analisador a partir de um AcademicAuditTrail.

        Extrai o texto de todos os paragrafos registrados.

        Args:
            audit_trail: Instancia de AcademicAuditTrail

        Returns:
            TextAnalyzer com o corpus carregado e analisado
        """
        ta = TextAnalyzer()
        corpus_parts = []

        if hasattr(audit_trail, "paragraphs"):
            for para in audit_trail.paragraphs.values():
                if hasattr(para, "text"):
                    corpus_parts.append(para.text)
                elif isinstance(para, dict):
                    corpus_parts.append(para.get("text", ""))

        corpus = " ".join(corpus_parts)
        ta.analyze(corpus)
        return ta


# ── Quick test ──
if __name__ == "__main__":
    sample = """
    A terapia cognitivo-comportamental demonstrou eficacia no tratamento
    da ansiedade generalizada. O paciente apresentou melhora significativa
    apos 20 sessoes de terapia. A terapia foi aplicada semanalmente com
    tecnicas de reestruturacao cognitiva e exposicao gradual. A paciente
    relatou reducao da ansiedade e melhora na qualidade de vida. A terapia
    cognitivo-comportamental e considerada tratamento de primeira linha.
    """
    ta = TextAnalyzer()
    result = ta.analyze(sample)
    print(f"Palavras: {result['total_words']}, Unicas: {result['unique_words']}")
    print(f"Top 5: {result['top_words'][:5]}")
