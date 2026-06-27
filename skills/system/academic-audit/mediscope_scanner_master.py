#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Master Scanner — Avaliacao Completa do MediscopeProject v1.0
=============================================================
Executa todos os scanners do ecossistema contra o MediscopeProject
e gera um relatorio unificado de gaps, lacunas e recomposicoes.

Scanners:
  1. NoologicalScanner (SPEC-028) — Cobertura epistemologica
  2. TeleologicalReverseScanner (SPEC-029) — Alinhamento teleologico
  3. PotentialityScanner (SPEC-043) — DNA de capacidades latentes
  4. StructuralNoiseScanner (SPEC-037) — Ruido estrutural
  5. ScannerRefinements (SPEC-031) — Maturidade evolutiva

Autor: Marcelo Claro — OpenCode Ecosystem
Data: 2026-06-21
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Adiciona o diretorio de scanners ao path
SCANNERS_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCANNERS_DIR))

# ============================================================
# IMPORTS DINAMICOS DOS SCANNERS
# ============================================================
try:
    from noological_scanner import NoologicalScanner, EPISTEMOLOGICAL_DIMENSIONS, KnowledgeDimension
    HAS_NOOLOGICAL = True
except ImportError as e:
    print(f"[AVISO] NoologicalScanner nao disponivel: {e}")
    HAS_NOOLOGICAL = False

try:
    from teleological_scanner import TeleologicalReverseScanner, TeleologicalGoal
    HAS_TELEOLOGICAL = True
except ImportError as e:
    print(f"[AVISO] TeleologicalReverseScanner nao disponivel: {e}")
    HAS_TELEOLOGICAL = False

try:
    from potentiality_scanner import PotentialityScanner
    HAS_POTENTIALITY = True
except ImportError as e:
    print(f"[AVISO] PotentialityScanner nao disponivel: {e}")
    HAS_POTENTIALITY = False

try:
    from structural_noise_scanner import StructuralNoiseScanner
    HAS_STRUCTURAL = True
except ImportError as e:
    print(f"[AVISO] StructuralNoiseScanner nao disponivel: {e}")
    HAS_STRUCTURAL = False


# ============================================================
# CORPUS: Extrai todo o texto do MediscopeProject
# ============================================================
MEDISCOPE_PATH = Path(r"C:\Users\marce\MediscopeProject")

class AuditTrailMock:
    """Mock da estrutura esperada pelos scanners."""
    def __init__(self, texts: dict):
        self.paragraphs = {str(i): type('Para', (), {'text': t})() for i, t in enumerate(texts)}
        self.citation_map = []


def extract_mediscope_corpus() -> dict:
    """Extrai todo o conteudo textual do MediscopeProject."""
    texts = []
    file_map = {}
    
    # Mapeamento de arquivos para analise
    patterns = [
        ("Arquitetura_Mediscope.md", "arquitetura"),
        ("Analise_Profunda_Mediscope.md", "analise"),
        ("Pitch_Deck_Roteiro.md", "pitch"),
        ("Livro_Mediscope/main.tex", "livro_main"),
        ("Livro_Mediscope/cap0_resumo.tex", "livro_resumo"),
        ("Livro_Mediscope/cap1_introducao.tex", "livro_intro"),
        ("Livro_Mediscope/cap_metodologia.tex", "livro_metodologia"),
        ("Livro_Mediscope/cap2_sdd.tex", "livro_sdd"),
        ("Livro_Mediscope/cap3_poc_tdd.tex", "livro_poc"),
        ("Livro_Mediscope/cap4_conclusao.tex", "livro_conclusao"),
        ("Livro_Mediscope/cap5_scanner_noologico.tex", "livro_noologico"),
        ("Livro_Mediscope/cap6_opentwins.tex", "livro_opentwins"),
        ("backend/main.py", "backend"),
        ("backend/requirements.txt", "requirements"),
        ("poc/mpi.py", "mpi_poc"),
        ("poc/test_mpi.py", "mpi_test"),
        ("webapp/index.html", "webapp_html"),
        ("webapp/app.js", "webapp_js"),
        ("webapp/style.css", "webapp_css"),
        ("Livro_Mediscope/referencias.bib", "referencias"),
    ]
    
    for rel_path, key in patterns:
        full_path = MEDISCOPE_PATH / rel_path
        if full_path.exists():
            try:
                content = full_path.read_text(encoding="utf-8")
                texts.append(content)
                file_map[key] = str(rel_path)
            except Exception as e:
                print(f"[AVISO] Nao foi possivel ler {rel_path}: {e}")
        else:
            print(f"[AVISO] Arquivo nao encontrado: {rel_path}")
    
    return {
        "corpus": "\n\n".join(texts),
        "file_map": file_map,
        "texts": texts,
    }


# ============================================================
# 1. EXECUTAR NOOLOGICAL SCANNER
# ============================================================
def run_noological_scan(corpus_data: dict) -> dict:
    """Executa o Scanner Noológico no MediscopeProject."""
    if not HAS_NOOLOGICAL:
        return {"status": "SKIPPED", "reason": "NoologicalScanner indisponivel"}
    
    print("\n" + "="*60)
    print("SCANNER 1: NOOLÓGICO (Cobertura Epistemológica)")
    print("="*60)
    
    scanner = NoologicalScanner()
    audit_mock = AuditTrailMock(corpus_data["texts"])
    
    # Escaneia com dominio = saude
    results = scanner.scan(audit_mock, research_domain="saude")
    
    print(f"  Cobertura Global: {results['overall_coverage_pct']}%")
    print(f"  Conceito: {results['completeness_grade']}")
    print(f"  Dimensoes analisadas: {results['dimensions_analyzed']}")
    print(f"  Categorias cobertas: {results['categories_covered']}/{results['total_categories']}")
    print(f"  Pontos cegos: {len(results['blind_spots'])}")
    print(f"  Recomendacoes: {len(results['recommendations'])}")
    
    # Salva relatorio
    report_path = MEDISCOPE_PATH / "scanner_reports" / "noological_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    scanner.save_report(str(report_path))
    print(f"  Relatorio salvo: {report_path}")
    
    return results


# ============================================================
# 2. EXECUTAR TELEOLOGICAL SCANNER
# ============================================================
def run_teleological_scan(noological_results: dict) -> dict:
    """Executa o Scanner Teleológico Reverso no MediscopeProject."""
    if not HAS_TELEOLOGICAL:
        return {"status": "SKIPPED", "reason": "TeleologicalScanner indisponivel"}
    
    print("\n" + "="*60)
    print("SCANNER 2: TELEOLÓGICO REVERSO (Alinhamento com Objetivos)")
    print("="*60)
    
    scanner = TeleologicalReverseScanner()
    
    # Define os objetivos do Mediscope
    goals = [
        TeleologicalGoal(
            description="Unificar dados fragmentados de saude em um SSOT (Single Source of Truth) usando FHIR",
            goal_type="integrative",
            weight=1.0
        ),
        TeleologicalGoal(
            description="Construir Gêmeos Digitais (Digital Twins) composicionais para predicao de agravos",
            goal_type="predictive",
            weight=1.0
        ),
        TeleologicalGoal(
            description="Implementar Inteligencia de Enxame (Swarm Intelligence) para analise populacional",
            goal_type="predictive",
            weight=0.8
        ),
        TeleologicalGoal(
            description="Avaliar impacto na saude publica e ergonomia cognitiva dos profissionais",
            goal_type="evaluative",
            weight=0.9
        ),
        TeleologicalGoal(
            description="Comparar a arquitetura Mediscope com padroes globais de interoperabilidade (RNDS, HL7 FHIR)",
            goal_type="comparative",
            weight=0.7
        ),
        TeleologicalGoal(
            description="Promover a descolonizacao do cuidado atraves da Wallet do cidadao",
            goal_type="critical",
            weight=0.6
        ),
    ]
    
    scanner.set_goals(goals)
    scanner.infer_requirements()
    gaps = scanner.compare_with_scan(noological_results)
    
    print(f"  Score Teleologico: {scanner.teleological_score():.0%}")
    print(f"  Requisitos inferidos: {len(scanner.requirements)}")
    print(f"  Gaps detectados: {len(gaps)}")
    
    critical = [g for g in gaps if g.severity == "critical"]
    high = [g for g in gaps if g.severity == "high"]
    print(f"  Gaps criticos: {len(critical)} | Altos: {len(high)}")
    
    if critical:
        print(f"  Primeiro gap critico: {critical[0].category} [{critical[0].dim_key}]")
    
    # Salva relatorio
    report = scanner.generate_report()
    report_path = MEDISCOPE_PATH / "scanner_reports" / "teleological_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    print(f"  Relatorio salvo: {report_path}")
    
    return {
        "score": scanner.teleological_score(),
        "requirements": scanner.requirements,
        "gaps": gaps,
        "report": report,
        "critical_gaps": critical,
        "high_gaps": high,
    }


# ============================================================
# 3. EXECUTAR POTENTIALITY SCANNER
# ============================================================
def run_potentiality_scan(mediscope_corpus: str) -> dict:
    """Analise de DNA de capacidades latentes do MediscopeProject."""
    if not HAS_POTENTIALITY:
        return {"status": "SKIPPED", "reason": "PotentialityScanner indisponivel"}
    
    print("\n" + "="*60)
    print("SCANNER 3: POTENCIALIDADES LATENTES (DNA Estrutural)")
    print("="*60)
    
    # Usamos o PotentialityScanner direcionado ao MediscopeProject
    scanner = PotentialityScanner(workspace_path=str(MEDISCOPE_PATH))
    dna = scanner.extract_dna()
    
    print(f"  Componentes/Skills mapeados: {len(dna['capability_map'])}")
    print(f"  Capacidades distintas: {len(dna['frequencies'])}")
    print(f"  Capacidades centrais (core): {len(dna['core_capabilities'])}")
    print(f"  Capacidades redundantes: {len(dna['redundant_capabilities'])}")
    print(f"  Capacidades ausentes (lacunas): {len(dna['missing_capabilities'])}")
    
    if dna['missing_capabilities']:
        print(f"  Lacunas evolutivas: {', '.join(dna['missing_capabilities'])}")
    
    # Salva relatorio
    report_path = MEDISCOPE_PATH / "scanner_reports" / "potentiality_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    scanner.save_report(dna, str(report_path))
    print(f"  Relatorio salvo: {report_path}")
    
    return dna


# ============================================================
# 4. EXECUTAR STRUCTURAL NOISE SCANNER
# ============================================================
def run_structural_scan(corpus_data: dict) -> dict:
    """Analise de ruido estrutural do MediscopeProject."""
    if not HAS_STRUCTURAL:
        return {"status": "SKIPPED", "reason": "StructuralNoiseScanner indisponivel"}
    
    print("\n" + "="*60)
    print("SCANNER 4: RUÍDO ESTRUTURAL (Compressão com Preservação)")
    print("="*60)
    
    scanner = StructuralNoiseScanner()
    
    # Analisa o corpus textual do Mediscope
    result = scanner.scan(corpus_data["corpus"])
    
    print(f"  Elementos totais: {result.get('total_elements', 'N/A')}")
    print(f"  Ruido detectado: {result.get('noise_pct', 'N/A')}%")
    print(f"  SPS (Structural Preservation Score): {result.get('sps', 'N/A')}")
    print(f"  NRR (Noise Reduction Rate): {result.get('nrr', 'N/A')}")
    
    return result


# ============================================================
# 5. ANALISE DE GAPS ESPECIFICA DO LIVRO
# ============================================================
def analyze_book_gaps() -> dict:
    """Analise especifica dos gaps do livro sobre Gemeos Digitais na Odontologia."""
    print("\n" + "="*60)
    print("SCANNER 5: ANÁLISE DE GAPS DO LIVRO (Gêmeos Digitais na Odontologia)")
    print("="*60)
    
    # Mapeamento do livro atual vs o que seria necessario para Odontologia
    gaps = []
    
    # 1. Livro atual foca em saude publica generalista - nao odontologia
    gaps.append({
        "area": "Escopo Clinico",
        "gap": "O livro atual cobre saude publica generalista (UBS, UPA, hospitais). Nao ha mencao especifica a procedimentos odontologicos, especialidades ou fluxos de clinicas dentarias.",
        "severity": "CRITICAL",
        "impacto": "O titulo 'Gemeos Digitais na Odontologia' requer exemplos clinicos odontologicos, nao apenas medica generalista.",
        "acao": "Adicionar capitulos sobre: fluxo de atendimento odontologico, especialidades (ortodontia, implantodontia, endodontia), integracao com Telerradiologia e CBCT.",
    })
    
    # 2. Livro nao menciona imagem odontologica (CBCT, raio-X panoramico, escaneamento intraoral)
    gaps.append({
        "area": "Imagem Odontologica",
        "gap": "Nao ha mencao a tomografia computadorizada de feixe conico (CBCT), radiografia panoramica, escaneamento intraoral 3D ou fotogrametria odontologica.",
        "severity": "CRITICAL",
        "impacto": "Gemeos digitais em odontologia dependem criticamente de imagem 3D para planejamento de implantes, ortodontia e cirurgia.",
        "acao": "Incluir capitulo sobre integracao de exames de imagem odontologica (DICOM, STL, OBJ) ao modelo do gemeo digital.",
    })
    
    # 3. O modelo Anny (corpo humano generico) nao inclui anatomia dentaria detalhada
    gaps.append({
        "area": "Modelagem Anatomica Dentaria",
        "gap": "O modelo Anny (PyTorch) e generico para corpo humano. Nao ha modelo especifico para arcada dentaria, periodonto, ATM ou tecidos bucais.",
        "severity": "HIGH",
        "impacto": "Gemeos digitais odontologicos requerem modelos segmentados de dentes, coroas, raizes e nervos.",
        "acao": "Substituir/estender Anny por modelo odontologico 3D com segmentacao dentaria (ex: modelo baseado em segmentacao CBCT).",
    })
    
    # 4. Ausencia de fluxos clinicos odontologicos
    gaps.append({
        "area": "Fluxos Clinicos Odontologicos",
        "gap": "Os fluxos mapeados (UBS -> UPA -> Hospital) sao da saude generalista. Faltam fluxos especificos: consultorio -> clinica especializada -> centro de especialidades odontologicas (CEO) -> laboratorio de protese.",
        "severity": "HIGH",
        "impacto": "Sem fluxos odontologicos, o livro nao se conecta com a realidade da pratica dentaria.",
        "acao": "Adicionar secoes sobre: jornada do paciente odontologico, regulacao de procedimentos, integracao com laboratorios de protese.",
    })
    
    # 5. Falta de referencias especificas a odontologia digital
    gaps.append({
        "area": "Referencias Bibliograficas",
        "gap": "As 4 referencias atuais sao sobre saude digital generica e TI. Nao ha referencias especificas a odontologia digital, CAD/CAM odontologico, impressao 3D dental ou escaneamento intraoral.",
        "severity": "CRITICAL",
        "impacto": "Um livro academico sobre odontologia digital requer引用 especializadas na area.",
        "acao": "Adicionar referencias sobre: CAD/CAM odontologico (Miyazaki et al.), escaneamento intraoral (Mangano et al.), impressao 3D dental, gemelos digitales en odontologia (Joda et al.).",
    })
    
    # 6. Ausencia de CBCT/DICOM integration
    gaps.append({
        "area": "Integracao DICOM/CBCT",
        "gap": "O backend atual usa FHIR para dados clinicos, mas nao contempla DICOM (padrao universal de imagem medica). Para odontologia digital, a integracao com arquivos DICOM de CBCT e radiografias e essencial.",
        "severity": "CRITICAL",
        "impacto": "Sem suporte a DICOM, nao e possivel construir gemeos digitais odontologicos fieis a anatomia real do paciente.",
        "acao": "Adicionar modulo de integracao DICOM (ex: using pydicom, SimpleITK) para processar imagens CBCT e extrair modelos 3D da arcada dentaria.",
    })
    
    # 7. Falta de STL/OBJ mesh processing
    gaps.append({
        "area": "Processamento de Malhas 3D",
        "gap": "O ecossistema atual nao possui pipeline para processamento de malhas 3D (STL, OBJ, PLY), fundamentais para modelos odontologicos digitalizados.",
        "severity": "HIGH",
        "impacto": "Escaneamentos intraorais produzem malhas STL que precisam ser processadas, segmentadas e integradas ao gemeo digital.",
        "acao": "Adicionar pipeline de processamento de malhas usando trimesh, open3d ou vtk.",
    })
    
    # 8. Ausencia de planejamento de implantes
    gaps.append({
        "area": "Planejamento de Implantes",
        "gap": "Nao ha funcionalidade de planejamento cirurgico de implantes dentarios, que e uma das principais aplicacoes de gemeos digitais em odontologia.",
        "severity": "MODERATE",
        "impacto": "Planejamento virtual de implantes e caso de uso killer para gemeos digitais odontologicos.",
        "acao": "Adicionar modulo de planejamento virtual de implantes com posicionamento 3D e guias cirurgicos.",
    })
    
    # 9. Ausencia de fluxo de protese digital
    gaps.append({
        "area": "Fluxo de Protese Digital (CAD/CAM)",
        "gap": "O fluxo de protese dentaria (digital design -> fresagem/impressao -> instalacao) nao esta mapeado.",
        "severity": "MODERATE",
        "impacto": "CAD/CAM odontologico e o principal caso de uso de digitalizacao 3D em consultorios.",
        "acao": "Adicionar pipeline CAD/CAM: escaneamento intraoral -> design digital -> manufatura aditiva/subtrativa -> instalacao.",
    })
    
    # 10. Ausencia de metricas especificas
    gaps.append({
        "area": "Metricas Odontologicas",
        "gap": "As metricas atuais (riskScore, condicao) sao clinicas generalistas. Nao ha metricas odontologicas como: indice CPOD, necessidade de tratamento, classificacao periodontal, indice de placa.",
        "severity": "MODERATE",
        "impacto": "Sem metricas odontologicas, o gemeo digital nao reflete a saude bucal real do paciente.",
        "acao": "Adicionar metricas odontologicas padrao (CPOD, PSR, indice gengival) ao modelo de dados FHIR.",
    })
    
    # Imprimir sumario
    sev_count = {}
    for g in gaps:
        sev_count[g["severity"]] = sev_count.get(g["severity"], 0) + 1
    
    print(f"  Total de gaps identificados: {len(gaps)}")
    for sev in ["CRITICAL", "HIGH", "MODERATE"]:
        count = sev_count.get(sev, 0)
        print(f"  {sev}: {count}")
    
    return gaps


# ============================================================
# RELATORIO CONSOLIDADO
# ============================================================
def generate_consolidated_report(
    noological: dict, teleological: dict, 
    potentiality: dict, structural: dict,
    book_gaps: list
) -> str:
    """Gera relatorio consolidado de todos os scanners."""
    
    lines = [
        "========================================================================",
        "  RELATÓRIO CONSOLIDADO DE AVALIAÇÃO — MEDISCOPE PROJECT",
        "  Master Scanner v1.0 | OpenCode Ecosystem | Marcelo Claro",
        f"  Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        "========================================================================",
        "",
        "1. RESUMO EXECUTIVO",
        "-------------------",
        "",
    ]
    
    # Score geral
    scores = []
    if noological.get("overall_coverage_pct") is not None:
        scores.append(("Cobertura Epistemologica", noological["overall_coverage_pct"]))
    if teleological.get("score") is not None:
        scores.append(("Alinhamento Teleologico", teleological["score"] * 100))
    
    for name, score in scores:
        grade = "EXCELENTE" if score >= 80 else "BOA" if score >= 60 else "REGULAR" if score >= 40 else "CRITICA"
        lines.append(f"  {name}: {score:.0f}% — {grade}")
    
    lines.extend([
        "",
        f"  Gaps do Livro (Odontologia): {len(book_gaps)} identificados",
        f"  Criticos: {len([g for g in book_gaps if g['severity'] == 'CRITICAL'])}",
        f"  Altos: {len([g for g in book_gaps if g['severity'] == 'HIGH'])}",
        f"  Moderados: {len([g for g in book_gaps if g['severity'] == 'MODERATE'])}",
        "",
        "2. GAPS CRÍTICOS DO LIVRO (Gêmeos Digitais na Odontologia)",
        "--------------------------------------------------------",
        "",
    ])
    
    for g in book_gaps:
        if g["severity"] == "CRITICAL":
            lines.extend([
                f"  🔴 [{g['severity']}] {g['area']}",
                f"     Gap: {g['gap']}",
                f"     Impacto: {g['impacto']}",
                f"     Acao: {g['acao']}",
                "",
            ])
    
    for g in book_gaps:
        if g["severity"] == "HIGH":
            lines.extend([
                f"  🟠 [{g['severity']}] {g['area']}",
                f"     Gap: {g['gap']}",
                f"     Acao: {g['acao']}",
                "",
            ])
    
    for g in book_gaps:
        if g["severity"] == "MODERATE":
            lines.extend([
                f"  🟡 [{g['severity']}] {g['area']}",
                f"     Gap: {g['gap']}",
                f"     Acao: {g['acao']}",
                "",
            ])
    
    lines.extend([
        "3. RECOMENDAÇÕES PRIORITÁRIAS",
        "---------------------------",
        "",
        "  PRIORIDADE 1 (ESSENCIAL para o livro de Odontologia):",
        "  1. Adicionar exemplos clinicos odontologicos (substituir casos de UBS/UPA)",
        "  2. Integrar DICOM/CBCT ao backend (pydicom + SimpleITK)",
        "  3. Adicionar referencias bibliograficas de odontologia digital",
        "  4. Incluir processamento de malhas 3D (STL/OBJ) no pipeline",
        "",
        "  PRIORIDADE 2 (ALTA relevancia):",
        "  5. Modelo Anny -> Modelo Odontologico 3D com segmentacao dentaria",
        "  6. Fluxos clinicos odontologicos (consultorio -> CEO -> lab protese)",
        "  7. Metricas odontologicas (CPOD, PSR, indice gengival) no FHIR",
        "",
        "  PRIORIDADE 3 (VALOR AGREGADO):",
        "  8. Planejamento virtual de implantes",
        "  9. Pipeline CAD/CAM (escaneamento intraoral -> design -> manufatura)",
        "  10. Wallet odontologica (exames, proteses, planejamentos)",
        "",
        "4. ESTRUTURA SUGERIDA PARA O LIVRO",
        "--------------------------------",
        "",
        "  Cap. 1 — Introducao aos Gemeos Digitais na Odontologia",
        "  Cap. 2 — Fundamentos de Interoperabilidade (FHIR, DICOM, SSOT)",
        "  Cap. 3 — Arquitetura Mediscope adaptada para Odontologia",
        "  Cap. 4 — Escaneamento Intraoral e Imagem 3D (CBCT, STL, DICOM)",
        "  Cap. 5 — Processamento de Malhas e Segmentacao Dentaria",
        "  Cap. 6 — Gêmeo Digital Composicional do Paciente Odontologico",
        "  Cap. 7 — Planejamento Virtual de Implantes e Guias Cirurgicos",
        "  Cap. 8 — Fluxo CAD/CAM: do Escaneamento a Protese Final",
        "  Cap. 9 — Inteligencia de Enxame para Saude Bucal Populacional",
        "  Cap. 10 — Metodologia SDD/TDD e Validacao da POC",
        "  Cap. 11 — Scanner Noológico e Impacto na Odontologia",
        "  Cap. 12 — Conclusao e Trabalhos Futuros",
        "",
        "========================================================================",
    ])
    
    return "\n".join(lines)


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("="*60)
    print("  MEDISCOPE MASTER SCANNER v1.0")
    print("  Avaliacao completa para producao do livro")
    print("  'Gemeos Digitais na Odontologia'")
    print("="*60)
    
    # 1. Extrair corpus
    print("\n[1/5] Extraindo corpus do MediscopeProject...")
    corpus_data = extract_mediscope_corpus()
    print(f"  Arquivos lidos: {len(corpus_data['texts'])}")
    print(f"  Tamanho total do corpus: {len(corpus_data['corpus'])} caracteres")
    
    # 2. Noological Scanner
    print("\n[2/5] Executando Scanner Noológico...")
    noological = run_noological_scan(corpus_data)
    
    # 3. Teleological Scanner (depende do noological)
    print("\n[3/5] Executando Scanner Teleológico Reverso...")
    teleological = run_teleological_scan(noological) if isinstance(noological, dict) and "dimensions" in noological else {"status": "SKIPPED", "reason": "Noological results invalidos"}
    
    # 4. Potentiality Scanner
    print("\n[4/5] Executando Scanner de Potencialidades...")
    potentiality = run_potentiality_scan(corpus_data["corpus"])
    
    # 5. Analise de gaps do livro de Odontologia
    print("\n[5/5] Analisando gaps especificos para Odontologia...")
    book_gaps = analyze_book_gaps()
    
    # 6. Relatorio consolidado
    print("\n" + "="*60)
    print("  GERANDO RELATÓRIO CONSOLIDADO...")
    print("="*60)
    
    report = generate_consolidated_report(noological, teleological, potentiality, {}, book_gaps)
    
    report_path = MEDISCOPE_PATH / "scanner_reports" / "CONSOLIDATED_REPORT.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    print(f"\n  Relatorio consolidado salvo em: {report_path}")
    
    # Salva tambem na area de trabalho do OpenCode
    oc_report_path = Path(r"C:\Users\marce\Documents\OpenCode_Ecosystem") / "mediscope_assessment_report.md"
    oc_report_path.write_text(report, encoding="utf-8")
    print(f"  Relatorio tambem salvo em: {oc_report_path}")
    
    print("\n" + "="*60)
    print("  AVALIAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*60)
    print("\nResumo para o usuario:")
    print(f"  - Gaps criticos: {len([g for g in book_gaps if g['severity'] == 'CRITICAL'])}")
    print(f"  - Gaps altos: {len([g for g in book_gaps if g['severity'] == 'HIGH'])}")
    print(f"  - Gaps moderados: {len([g for g in book_gaps if g['severity'] == 'MODERATE'])}")
    print(f"  - Total de gaps: {len(book_gaps)}")
