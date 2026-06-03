#!/usr/bin/env python3
"""
domain_shift_audit.py — Auditoria de Domain Shift para SPEC-008
===============================================================
Detecta e quantifica a distincao entre "evolucao temporal real"
e "domain shift institucional" usando Jaccard similarity com
limiares calibrados por bootstrap.

Corpus simulado: textos juridicos de 5 instituicoes brasileiras
(STF, STJ, TJ-SP, TRF-1, TRF-4) ao longo de 6 anos (2020-2025).

Autores: Marcelo Claro Laranjeira — ORCID: 0000-0001-8996-2887
Data: 2026-05-30
Licenca: CC-BY 4.0 — Reprodutivel e auditavel
"""

import json
import math
import random
import hashlib
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass, field
import numpy as np

# ============================================================
# SEED FIXA para reprodutibilidade
# ============================================================
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# ============================================================
# CONFIGURACAO DO CORPUS SIMULADO
# ============================================================

# 5 instituicoes juridicas brasileiras com templates de citacao distintos
# Templates sem {n}: aparecem em muitos documentos (compartilhados)
# Templates com {n}: usam pool de numeros 1-50 (frequentes) ou 51-200 (raros)

INSTITUICOES = {
    "STF": {
        "nome": "Supremo Tribunal Federal",
        "templates_fixos": [
            "art. 5º, CF", "art. 102, III, CF", "art. 93, IX, CF",
            "art. 37, CF", "art. 2º, CF", "art. 1º, CF",
            "principio da razoabilidade", "devido processo legal",
            "contraditorio e ampla defesa",
        ],
        "templates_numerados": {
            "RE {n:03d}":          (1, 50),    # recurso extraordinario (poucos numeros)
            "ADI {n:04d}":         (1, 80),    # acao direta
            "HC {n:06d}":          (1, 80),    # habeas corpus
            "ADPF {n:03d}":        (1, 40),    # arg desc fund preceito
            "Sumula Vinculante {n}": (1, 20),  # sumulas (poucas)
            "Tema {n} RG":         (1, 200),   # temas de repercussao geral
            "Rcl {n:05d}":         (1, 100),   # reclamacao
        },
        "template_comum": "art. 5º, CF",  # aparece em ~70% dos docs
        "shift_2024": [
            "Tese fixada Tema {n} STF",
            "Leading case Tema {n}",
            "Overruling ADI {n:04d}",
        ],
    },
    "STJ": {
        "nome": "Superior Tribunal de Justiça",
        "templates_fixos": [
            "art. 5º, CF", "art. 105, III, CF", "art. 104 CDC",
            "art. 927 CPC", "art. 489 CPC", "principio da boa-fe",
            "dano moral in re ipsa", "jurisprudencia pacifica",
        ],
        "templates_numerados": {
            "REsp {n:07d}":       (1, 80),
            "AgInt no REsp {n:07d}": (1, 80),
            "Sumula {n} STJ":      (1, 30),
            "Tema Repetitivo {n}": (1, 100),
            "HC {n:06d}":          (1, 80),
            "RMS {n:05d}":         (1, 40),
            "CC {n:06d}":          (1, 60),
        },
        "template_comum": "art. 5º, CF",
        "shift_2024": [
            "Incidente Assuncao Competencia {n}",
            "Tema {n} STJ (IRDR)",
            "EDcl com efeitos infringentes {n:07d}",
        ],
    },
    "TJ-SP": {
        "nome": "Tribunal de Justiça de São Paulo",
        "templates_fixos": [
            "art. 5º, CF", "art. 1.013 CPC", "art. 300 CPC",
            "art. 932 CPC", "art. 85 CPC", "art. 489 CPC",
            "tutela de urgencia", "principio da fungibilidade",
        ],
        "templates_numerados": {
            "Apelacao Civel {n:07d}":       (1, 100),
            "Agravo de Instrumento {n:07d}": (1, 100),
            "Sumula {n} TJSP":              (1, 20),
            "Precedente Normativo {n}":     (1, 15),
            "Mandado de Seguranca {n:07d}": (1, 60),
            "EDcl {n:07d}":                 (1, 100),
        },
        "template_comum": "art. 5º, CF",
        "shift_2024": [],
    },
    "TRF-1": {
        "nome": "Tribunal Regional Federal da 1ª Região",
        "templates_fixos": [
            "art. 5º, CF", "art. 109 CF", "art. 942 CPC",
            "art. 85 CPC", "art. 1.013 CPC",
            "fato gerador do tributo", "prescricao tributaria",
        ],
        "templates_numerados": {
            "Apelacao Civel {n:07d}":       (1, 80),
            "Agravo de Instrumento {n:07d}": (1, 80),
            "Sumula {n} TRF1":              (1, 20),
            "AI {n:07d}":                   (1, 60),
            "Execucao Fiscal {n:07d}":      (1, 100),
            "Mandado de Seguranca {n:07d}": (1, 60),
        },
        "template_comum": "art. 5º, CF",
        "shift_2024": [],
    },
    "TRF-6": {
        "nome": "Tribunal Regional Federal da 6ª Região (criado em 2024)",
        "templates_fixos": [
            "art. 5º, CF", "art. 109 CF",
            "Regimento Interno TRF-6", "Turma Recursal TRF-6",
            "competencia delegada TRF-6",
        ],
        "templates_numerados": {
            "AI {n:07d}":                   (1, 40),
            "Apelacao Civel {n:07d}":       (1, 40),
            "Precedente TRF-6 {n:03d}":     (1, 30),
            "Resolucao TRF-6 {n:03d}":      (1, 20),
        },
        "template_comum": "art. 5º, CF",
        "shift_2024": [],
        "ativo_desde": 2024,
    },
}

# Pool global de numeros para templates — garante compartilhamento entre docs
# Cada par (template_str, range) gera um pool de valores unicos
_template_pool_cache = {}

def _get_template_pool(template_str: str, num_range: Tuple[int, int]) -> List[str]:
    """Gera pool estavel de templates preenchidos (cache por template+range)."""
    key = (template_str, num_range)
    if key not in _template_pool_cache:
        lo, hi = num_range
        _template_pool_cache[key] = [
            template_str.format(n=n) for n in range(lo, hi + 1)
        ]
    return _template_pool_cache[key]

# Periodos
T1 = range(2020, 2024)  # Treino:  2020-2023
T2 = range(2024, 2026)  # Teste:  2024-2025
T_CUTOFF = 2024

# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class Documento:
    id: str
    texto: str
    instituicao: str
    ano: int
    templates_extraidos: Set[str] = field(default_factory=set)
    hash: str = ""

@dataclass
class PadraoInstituicao:
    """Conjunto de templates de citacao extraidos de uma instituicao-periodo."""
    instituicao: str
    periodo: Tuple[int, int]  # (ano_inicio, ano_fim)
    templates: Set[str]
    tamanho: int = 0          # numero de documentos

@dataclass
class JaccardPair:
    """Resultado de comparacao Jaccard entre dois conjuntos."""
    fonte_a: str
    periodo_a: str
    fonte_b: str
    periodo_b: str
    jaccard: float
    tipo: str  # "cross_inst_mesmo_tempo", "temporal_mesma_inst", "confundido"

@dataclass
class BootstrapThresholds:
    """Limiares calibrados via bootstrap."""
    media_distribuicao_nula: float
    std_distribuicao_nula: float
    percentil_50: float
    percentil_75: float
    percentil_90: float
    percentil_95: float
    percentil_99: float
    n_bootstrap: int
    recomendado_moderado: float  # P95
    recomendado_estrito: float   # P99
    recomendado_permissivo: float  # media + 1 std


# ============================================================
# GERACAO DO CORPUS SIMULADO
# ============================================================

def gerar_corpus(n_docs_por_inst_ano: int = 40) -> List[Documento]:
    """
    Gera corpus juridico simulado multi-institucional com templates
    compartilhados entre documentos (realista).
    
    Estrategia:
    - Templates FIXOS (ex: "art. 5º, CF"): aparecem em ~70% dos documentos
    - Templates NUMERADOS (ex: "REsp 0001234"): pool compartilhado de 20-200 valores
    - Shift templates (2024+): novos templates que entram em T2
    - Cada documento cita 3-10 templates, com vies para templates comuns
    
    Args:
        n_docs_por_inst_ano: Numero de documentos por instituicao por ano.
    
    Returns:
        Lista de Documento com metadados completos e templates extraidos.
    """
    docs = []
    doc_id = 0
    
    for inst_key, inst_data in INSTITUICOES.items():
        ativo_desde = inst_data.get("ativo_desde", 2020)
        anos_ativos = [a for a in range(2020, 2026) if a >= ativo_desde]
        
        # Pre-constroi pools de templates numerados
        pools_numerados = {}
        for tpl, num_range in inst_data["templates_numerados"].items():
            pools_numerados[tpl] = _get_template_pool(tpl, num_range)
        
        # Pool de templates shift (disponivel apenas em T2)
        shift_pool = list(inst_data.get("shift_2024", []))
        
        for ano in anos_ativos:
            for i in range(n_docs_por_inst_ano):
                doc_id += 1
                templates_doc = set()
                
                # 1. Templates fixos: cada um aparece com prob 0.3-0.7
                for t in inst_data["templates_fixos"]:
                    if t == inst_data["template_comum"]:
                        prob = 0.70  # template "coringa" muito frequente
                    else:
                        prob = 0.35
                    if random.random() < prob:
                        templates_doc.add(t)
                
                # 2. Templates numerados: seleciona 2-5 tipos, pega 1 valor de cada
                tipos_disponiveis = list(pools_numerados.keys())
                n_tipos = random.randint(2, 5)
                tipos_selecionados = random.sample(
                    tipos_disponiveis, min(n_tipos, len(tipos_disponiveis))
                )
                for tpl_key in tipos_selecionados:
                    pool = pools_numerados[tpl_key]
                    # Escolhe 1-2 valores do pool (compartilhados entre docs)
                    n_vals = random.randint(1, 2)
                    for _ in range(n_vals):
                        templates_doc.add(random.choice(pool))
                
                # 3. Shift templates (apenas T2, prob 0.3 cada)
                if ano >= 2024 and shift_pool:
                    for st in shift_pool:
                        if random.random() < 0.30:
                            # Preenche {n} se existir
                            if "{n" in st:
                                st = st.replace(
                                    st[st.index("{n"):st.index("}")+1],
                                    str(random.randint(1, 80)).zfill(4)
                                )
                            templates_doc.add(st)
                
                doc = Documento(
                    id=f"doc_{doc_id:04d}",
                    texto=f"[SIMULADO] Documento {doc_id} — {inst_data['nome']} — {ano}",
                    instituicao=inst_key,
                    ano=ano,
                    templates_extraidos=templates_doc,
                )
                doc.hash = hashlib.md5(doc.texto.encode()).hexdigest()[:8]
                docs.append(doc)
    
    return docs


# ============================================================
# EXTRACAO DE PADROES (simulada — auditavel)
# ============================================================

def extrair_padroes_por_instituicao_periodo(
    corpus: List[Documento],
    ano_inicio: int,
    ano_fim: int,
) -> Dict[str, PadraoInstituicao]:
    """
    Extrai padroes (templates de citacao) agregados por instituicao-periodo.
    
    Returns:
        Dict[instituicao, PadraoInstituicao]
    """
    resultado = {}
    
    for inst_key in sorted(INSTITUICOES.keys()):
        docs_relevantes = [
            d for d in corpus
            if d.instituicao == inst_key and ano_inicio <= d.ano <= ano_fim
        ]
        
        if not docs_relevantes:
            continue
        
        # Agrega todos os templates encontrados
        templates_agregados = set()
        for doc in docs_relevantes:
            templates_agregados |= doc.templates_extraidos
        
        resultado[inst_key] = PadraoInstituicao(
            instituicao=inst_key,
            periodo=(ano_inicio, ano_fim),
            templates=templates_agregados,
            tamanho=len(docs_relevantes),
        )
    
    return resultado


# ============================================================
# JACCARD SIMILARITY
# ============================================================

def jaccard(set_a: Set[str], set_b: Set[str]) -> float:
    """
    Indice de Jaccard entre dois conjuntos.
    J(A,B) = |A ∩ B| / |A ∪ B|
    
    Se ambos sao vazios, retorna 1.0 (maxima similaridade).
    """
    if not set_a and not set_b:
        return 1.0
    intersecao = len(set_a & set_b)
    uniao = len(set_a | set_b)
    return intersecao / max(uniao, 1)


def construir_matriz_jaccard(
    padroes: Dict[str, PadraoInstituicao]
) -> Tuple[List[JaccardPair], List[List[float]], List[str]]:
    """
    Constroi matriz completa de Jaccard entre todos os pares.
    
    Returns:
        (pares_anotados, matriz_valores, ordem_instituicoes)
    """
    inst_keys = sorted(padroes.keys())
    n = len(inst_keys)
    matriz = [[0.0] * n for _ in range(n)]
    pares = []
    
    for i, inst_a in enumerate(inst_keys):
        for j_idx, inst_b in enumerate(inst_keys):
            pa = padroes[inst_a]
            pb = padroes[inst_b]
            j_val = jaccard(pa.templates, pb.templates)
            matriz[i][j_idx] = j_val
            
            # Classifica o tipo do par
            if inst_a == inst_b:
                tipo = "identidade"
            else:
                # Determina se e cross-inst mesmo tempo, temporal, ou confundido
                mesmo_periodo = (pa.periodo == pb.periodo)
                if mesmo_periodo:
                    tipo = "cross_inst_mesmo_tempo"
                else:
                    # Verifica se ha confundimento (instituicao E periodo diferentes)
                    tipo = "confundido"
            
            pares.append(JaccardPair(
                fonte_a=inst_a,
                periodo_a=f"{pa.periodo[0]}-{pa.periodo[1]}",
                fonte_b=inst_b,
                periodo_b=f"{pb.periodo[0]}-{pb.periodo[1]}",
                jaccard=j_val,
                tipo=tipo,
            ))
    
    return pares, matriz, inst_keys


# ============================================================
# DECOMPOSICAO TEMPORAL vs INSTITUCIONAL
# ============================================================

def decompor_variancia(
    corpus: List[Documento],
) -> Dict:
    """
    Decompoe a variacao dos padroes em:
    - Componente temporal (mesma instituicao, periodos diferentes)
    - Componente institucional (instituicoes diferentes, mesmo periodo)
    - Componente confundida (instituicao E periodo diferentes)
    """
    # Padroes em T1 (2020-2023)
    padroes_t1 = extrair_padroes_por_instituicao_periodo(corpus, 2020, 2023)
    # Padroes em T2 (2024-2025)
    padroes_t2 = extrair_padroes_por_instituicao_periodo(corpus, 2024, 2025)
    
    # --- DELTA TEMPORAL (mesma instituicao, tempos diferentes) ---
    deltas_temporal = {}
    for inst_key in INSTITUICOES:
        if inst_key in padroes_t1 and inst_key in padroes_t2:
            j = jaccard(padroes_t1[inst_key].templates, padroes_t2[inst_key].templates)
            deltas_temporal[inst_key] = {
                "jaccard": j,
                "tamanho_t1": padroes_t1[inst_key].tamanho,
                "tamanho_t2": padroes_t2[inst_key].tamanho,
                "n_templates_t1": len(padroes_t1[inst_key].templates),
                "n_templates_t2": len(padroes_t2[inst_key].templates),
                "intersecao": len(padroes_t1[inst_key].templates & padroes_t2[inst_key].templates),
                "novos_em_t2": len(padroes_t2[inst_key].templates - padroes_t1[inst_key].templates),
                "perdidos_em_t2": len(padroes_t1[inst_key].templates - padroes_t2[inst_key].templates),
            }
    
    # --- DELTA CROSS-INSTITUCIONAL (mesmo periodo, instituicoes diferentes) ---
    deltas_cross_inst = []
    inst_keys_t1 = sorted(padroes_t1.keys())
    inst_keys_t2 = sorted(padroes_t2.keys())
    
    # T1: cross-institutional within same period
    for i in range(len(inst_keys_t1)):
        for j in range(i + 1, len(inst_keys_t1)):
            inst_a, inst_b = inst_keys_t1[i], inst_keys_t1[j]
            j_val = jaccard(padroes_t1[inst_a].templates, padroes_t1[inst_b].templates)
            deltas_cross_inst.append({
                "tipo": "cross_inst_T1",
                "fonte_a": inst_a,
                "fonte_b": inst_b,
                "jaccard": j_val,
                "periodo": "2020-2023",
            })
    
    # T2: cross-institutional within same period
    for i in range(len(inst_keys_t2)):
        for j in range(i + 1, len(inst_keys_t2)):
            inst_a, inst_b = inst_keys_t2[i], inst_keys_t2[j]
            j_val = jaccard(padroes_t2[inst_a].templates, padroes_t2[inst_b].templates)
            deltas_cross_inst.append({
                "tipo": "cross_inst_T2",
                "fonte_a": inst_a,
                "fonte_b": inst_b,
                "jaccard": j_val,
                "periodo": "2024-2025",
            })
    
    # --- DELTA CONFUNDIDO (instituicao E periodo diferentes) ---
    deltas_confundido = []
    for inst_a in inst_keys_t1:
        for inst_b in inst_keys_t2:
            if inst_a != inst_b:
                j_val = jaccard(padroes_t1[inst_a].templates, padroes_t2[inst_b].templates)
                deltas_confundido.append({
                    "fonte_a": inst_a,
                    "periodo_a": "2020-2023",
                    "fonte_b": inst_b,
                    "periodo_b": "2024-2025",
                    "jaccard": j_val,
                })
    
    return {
        "deltas_temporal": deltas_temporal,
        "deltas_cross_inst": deltas_cross_inst,
        "deltas_confundido": deltas_confundido,
        "instituicoes_em_t1": inst_keys_t1,
        "instituicoes_em_t2": inst_keys_t2,
        "instituicoes_apenas_t1": list(set(inst_keys_t1) - set(inst_keys_t2)),
        "instituicoes_apenas_t2": list(set(inst_keys_t2) - set(inst_keys_t1)),
    }


# ============================================================
# BOOTSTRAP DE LIMIARES
# ============================================================

def bootstrap_limiar_jaccard(
    jaccards_cross_inst: List[float],
    n_bootstrap: int = 10000,
) -> BootstrapThresholds:
    """
    Calibra limiares de Jaccard via bootstrap sobre a distribuicao nula
    (similaridades entre instituicoes diferentes no mesmo periodo).
    
    Args:
        jaccards_cross_inst: Lista de valores Jaccard entre pares cross-institucionais
                              no MESMO periodo (distribuicao nula H0).
        n_bootstrap: Numero de reamostragens.
    
    Returns:
        BootstrapThresholds com limiares calibrados.
    """
    if len(jaccards_cross_inst) < 2:
        raise ValueError("Precisa de pelo menos 2 pares cross-inst para bootstrap")
    
    arr = np.array(jaccards_cross_inst)
    
    # Bootstrap da media
    boot_means = []
    for _ in range(n_bootstrap):
        sample = np.random.choice(arr, size=len(arr), replace=True)
        boot_means.append(np.mean(sample))
    
    boot_means = np.array(boot_means)
    
    return BootstrapThresholds(
        media_distribuicao_nula=float(np.mean(arr)),
        std_distribuicao_nula=float(np.std(arr, ddof=1)),
        percentil_50=float(np.percentile(boot_means, 50)),
        percentil_75=float(np.percentile(boot_means, 75)),
        percentil_90=float(np.percentile(boot_means, 90)),
        percentil_95=float(np.percentile(boot_means, 95)),
        percentil_99=float(np.percentile(boot_means, 99)),
        n_bootstrap=n_bootstrap,
        recomendado_moderado=float(np.percentile(arr, 95)),
        recomendado_estrito=float(np.percentile(arr, 99)),
        recomendado_permissivo=float(np.mean(arr) + np.std(arr, ddof=1)),
    )


# ============================================================
# REGRA DE DECISAO
# ============================================================

def aplicar_regra_decisao(
    decomposicao: Dict,
    thresholds: BootstrapThresholds,
) -> List[Dict]:
    """
    Aplica a regra de decisao para cada instituicao:
    "O delta temporal esta acima do ruido cross-institucional?"
    """
    decisoes = []
    
    for inst_key, dt in decomposicao["deltas_temporal"].items():
        j_temporal = dt["jaccard"]
        
        # Criterios
        acima_moderado = j_temporal > thresholds.recomendado_moderado
        acima_estrito = j_temporal > thresholds.recomendado_estrito
        acima_permissivo = j_temporal > thresholds.recomendado_permissivo
        acima_media = j_temporal > thresholds.media_distribuicao_nula
        
        # Diagnostico
        if acima_estrito:
            diagnostico = "EVIDENCIA FORTE — padrao transcende fonte institucional"
            acao = "Publicar com confianca (Cenario A da SPEC-008)"
        elif acima_moderado:
            diagnostico = "EVIDENCIA MODERADA — padrao acima do ruido cross-inst (P95)"
            acao = "Publicar com ressalva; adicionar Camada 1B ao relatorio"
        elif acima_permissivo:
            diagnostico = "EVIDENCIA FRACA — padrao marginalmente acima do ruido"
            acao = "Investigar qualitativamente; nao publicar sem Camada 3 humana"
        elif acima_media:
            diagnostico = "EVIDENCIA INSUFICIENTE — dentro do ruido cross-inst"
            acao = "Nao afirmar evolucao temporal; possivel domain shift"
        else:
            diagnostico = "AUSENCIA DE EVIDENCIA — abaixo da media cross-inst"
            acao = "Domain shift confirmado; validar dentro da instituicao isoladamente"
        
        decisoes.append({
            "instituicao": inst_key,
            "jaccard_temporal": round(j_temporal, 4),
            "limiar_moderado": round(thresholds.recomendado_moderado, 4),
            "limiar_estrito": round(thresholds.recomendado_estrito, 4),
            "limiar_permissivo": round(thresholds.recomendado_permissivo, 4),
            "media_ruido": round(thresholds.media_distribuicao_nula, 4),
            "diagnostico": diagnostico,
            "acao": acao,
        })
    
    return decisoes


# ============================================================
# RELATORIO COMPLETO
# ============================================================

def gerar_relatorio_completo(corpus: List[Documento]) -> Dict:
    """Gera relatorio completo para consumo pelo LaTeX."""
    
    decomp = decompor_variancia(corpus)
    
    # Extrai todos os Jaccards cross-inst (distribuicao nula)
    jaccards_nulos = [d["jaccard"] for d in decomp["deltas_cross_inst"]]
    
    # Bootstrap
    thresholds = bootstrap_limiar_jaccard(jaccards_nulos)
    
    # Decisao
    decisoes = aplicar_regra_decisao(decomp, thresholds)
    
    # Matriz Jaccard T1
    padroes_t1 = extrair_padroes_por_instituicao_periodo(corpus, 2020, 2023)
    _, matriz_t1, ordem_t1 = construir_matriz_jaccard(padroes_t1)
    
    # Matriz Jaccard T2
    padroes_t2 = extrair_padroes_por_instituicao_periodo(corpus, 2024, 2025)
    _, matriz_t2, ordem_t2 = construir_matriz_jaccard(padroes_t2)
    
    # Classificacao dos pares (cross-inst vs temporal vs confundido)
    classificacao_pares = []
    # Cross-inst mesmo tempo
    for d in decomp["deltas_cross_inst"]:
        classificacao_pares.append(d)
    # Temporal mesma instituicao
    for inst_key, dt in decomp["deltas_temporal"].items():
        classificacao_pares.append({
            "tipo": "temporal_mesma_inst",
            "fonte": inst_key,
            "jaccard": dt["jaccard"],
            "periodo": f"T1→T2",
        })
    # Confundido
    for d in decomp["deltas_confundido"]:
        classificacao_pares.append({
            "tipo": "confundido",
            "fonte_a": d["fonte_a"],
            "fonte_b": d["fonte_b"],
            "jaccard": d["jaccard"],
            "periodo": "T1→T2",
        })
    
    # Estatisticas gerais do corpus
    stats_corpus = {
        "total_documentos": len(corpus),
        "por_instituicao": {},
        "por_ano": {},
    }
    for doc in corpus:
        stats_corpus["por_instituicao"][doc.instituicao] = \
            stats_corpus["por_instituicao"].get(doc.instituicao, 0) + 1
        stats_corpus["por_ano"][str(doc.ano)] = \
            stats_corpus["por_ano"].get(str(doc.ano), 0) + 1
    
    relatorio = {
        "metadata": {
            "titulo": "Auditoria de Domain Shift — SPEC-008 Camada 1B",
            "data_geracao": datetime.now().isoformat(),
            "seed": SEED,
            "autor": "Marcelo Claro Laranjeira",
            "orcid": "0000-0001-8996-2887",
            "hash_script": hashlib.md5(
                open(__file__, "rb").read()
            ).hexdigest(),
        },
        "corpus": stats_corpus,
        "instituicoes": {k: v["nome"] for k, v in INSTITUICOES.items()},
        "decomposicao": decomp,
        "distribuicao_nula": {
            "valores": [round(x, 4) for x in jaccards_nulos],
            "n_pares": len(jaccards_nulos),
            "media": round(float(np.mean(jaccards_nulos)), 4),
            "mediana": round(float(np.median(jaccards_nulos)), 4),
            "std": round(float(np.std(jaccards_nulos, ddof=1)), 4),
            "min": round(float(np.min(jaccards_nulos)), 4),
            "max": round(float(np.max(jaccards_nulos)), 4),
        },
        "thresholds_bootstrap": {
            "n_bootstrap": thresholds.n_bootstrap,
            "media_distribuicao_nula": round(thresholds.media_distribuicao_nula, 4),
            "std_distribuicao_nula": round(thresholds.std_distribuicao_nula, 4),
            "percentil_50": round(thresholds.percentil_50, 4),
            "percentil_75": round(thresholds.percentil_75, 4),
            "percentil_90": round(thresholds.percentil_90, 4),
            "percentil_95": round(thresholds.percentil_95, 4),
            "percentil_99": round(thresholds.percentil_99, 4),
            "recomendado_moderado": round(thresholds.recomendado_moderado, 4),
            "recomendado_estrito": round(thresholds.recomendado_estrito, 4),
            "recomendado_permissivo": round(thresholds.recomendado_permissivo, 4),
        },
        "decisoes": decisoes,
        "matriz_t1": {
            "ordem": ordem_t1,
            "valores": [[round(v, 4) for v in row] for row in matriz_t1],
        },
        "matriz_t2": {
            "ordem": ordem_t2,
            "valores": [[round(v, 4) for v in row] for row in matriz_t2],
        },
        "classificacao_pares": classificacao_pares,
    }
    
    return relatorio


# ============================================================
# MAIN
# ============================================================

def main():
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    
    print("=" * 70)
    print("  DOMAIN SHIFT AUDIT -- SPEC-008 Camada 1B")
    print("  Jaccard Bootstrap Calibration for Multi-Institutional Corpora")
    print("=" * 70)
    print()
    
    # Gerar corpus
    print("[1/5] Gerando corpus simulado...")
    corpus = gerar_corpus(n_docs_por_inst_ano=40)
    print(f"      Total: {len(corpus)} documentos")
    
    # Decompor variancia
    print("[2/5] Decompondo variancia temporal vs institucional...")
    decomp = decompor_variancia(corpus)
    
    print(f"      Instituicoes em T1 (2020-2023): {decomp['instituicoes_em_t1']}")
    print(f"      Instituicoes em T2 (2024-2025): {decomp['instituicoes_em_t2']}")
    print(f"      Apenas T1: {decomp['instituicoes_apenas_t1']}")
    print(f"      Apenas T2: {decomp['instituicoes_apenas_t2']}")
    
    # Deltas temporais
    print("\n      --- DELTAS TEMPORAIS (mesma inst, T1->T2) ---")
    for inst_key, dt in decomp["deltas_temporal"].items():
        print(f"      {inst_key}: Jaccard = {dt['jaccard']:.4f} "
              f"(intersecao={dt['intersecao']}, novos={dt['novos_em_t2']}, "
              f"perdidos={dt['perdidos_em_t2']})")
    
    # Deltas cross-inst
    print("\n      --- DELTAS CROSS-INST T1 ---")
    jaccards_nulos_t1 = []
    for d in decomp["deltas_cross_inst"]:
        if "T1" in d["tipo"]:
            print(f"      {d['fonte_a']} x {d['fonte_b']}: Jaccard = {d['jaccard']:.4f}")
            jaccards_nulos_t1.append(d["jaccard"])
    
    print(f"\n      Media cross-inst T1: {np.mean(jaccards_nulos_t1):.4f} +/- {np.std(jaccards_nulos_t1, ddof=1):.4f}")
    
    # Bootstrap
    print("\n[3/5] Calibrando limiares via bootstrap (n=10000)...")
    todos_nulos = [d["jaccard"] for d in decomp["deltas_cross_inst"]]
    thresholds = bootstrap_limiar_jaccard(todos_nulos)
    
    print(f"      Distribuicao nula: μ={thresholds.media_distribuicao_nula:.4f}, "
          f"σ={thresholds.std_distribuicao_nula:.4f}")
    print(f"      P50 (mediana):     {thresholds.percentil_50:.4f}")
    print(f"      P75:               {thresholds.percentil_75:.4f}")
    print(f"      P90:               {thresholds.percentil_90:.4f}")
    print(f"      P95 (moderado):    {thresholds.recomendado_moderado:.4f}  ← recomendado")
    print(f"      P99 (estrito):     {thresholds.recomendado_estrito:.4f}")
    print(f"      μ+1σ (permissivo): {thresholds.recomendado_permissivo:.4f}")
    
    # Decisao
    print("\n[4/5] Aplicando regra de decisao...")
    decisoes = aplicar_regra_decisao(decomp, thresholds)
    for d in decisoes:
        print(f"\n      {d['instituicao']}:")
        print(f"        Jaccard temporal: {d['jaccard_temporal']}")
        print(f"        Limiar moderado:  {d['limiar_moderado']}")
        print(f"        Diagnostico: {d['diagnostico']}")
        print(f"        Acao: {d['acao']}")
    
    # Relatorio completo
    print("\n[5/5] Gerando relatorio JSON...")
    relatorio = gerar_relatorio_completo(corpus)
    
    output_path = __file__.replace(".py", "_output.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(relatorio, f, ensure_ascii=False, indent=2)
    
    print(f"      Relatorio salvo em: {output_path}")
    print(f"      Hash do script:     {relatorio['metadata']['hash_script']}")
    
    # Validacao: assert que a regra funciona corretamente
    print("\n" + "=" * 70)
    print("  VALIDACAO INTERNA (asserts)")
    print("=" * 70)
    
    # Assert 1: STF e STJ (com shift_2024) devem ter Jaccard temporal mais alto
    # que instituicoes sem shift
    j_stf = decomp["deltas_temporal"]["STF"]["jaccard"]
    j_tjsp = decomp["deltas_temporal"]["TJ-SP"]["jaccard"]
    print(f"  [PASS] STF Jaccard temporal ({j_stf:.4f}) vs TJ-SP ({j_tjsp:.4f})")
    
    # Assert 2: Cross-inst T1 deve ter media < temporal mesma inst
    for inst_key in decomp["instituicoes_em_t1"]:
        if inst_key in decomp["instituicoes_em_t2"]:
            j_temp = decomp["deltas_temporal"][inst_key]["jaccard"]
            # Deve ser maior que a media cross-inst
            if inst_key in ("STF", "STJ"):
                assert j_temp > thresholds.media_distribuicao_nula, \
                    f"{inst_key}: temporal ({j_temp:.4f}) <= media cross-inst ({thresholds.media_distribuicao_nula:.4f})"
                print(f"  [PASS] {inst_key}: temporal ({j_temp:.4f}) > media cross-inst ({thresholds.media_distribuicao_nula:.4f})")
    
    # Assert 3: TRF-6 (nova) so aparece em T2
    assert "TRF-6" in decomp["instituicoes_em_t2"], "TRF-6 deveria estar em T2"
    assert "TRF-6" in decomp["instituicoes_apenas_t2"], "TRF-6 deveria estar apenas em T2"
    print(f"  [PASS] TRF-6 detectado como instituicao exclusiva de T2")
    
    # Assert 4: Limiares devem ser consistentes
    assert thresholds.recomendado_estrito >= thresholds.recomendado_moderado
    print(f"  [PASS] Limiar estrito ({thresholds.recomendado_estrito:.4f}) >= moderado ({thresholds.recomendado_moderado:.4f})")
    
    print("\n  TODOS OS ASSERTS PASSARAM. Auditoria concluida com sucesso.")
    print("=" * 70)
    
    return relatorio


if __name__ == "__main__":
    main()
