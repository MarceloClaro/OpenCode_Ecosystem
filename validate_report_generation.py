#!/usr/bin/env python3
"""
Validação Autônoma de Geração de Relatório de Evento Injetado
Garante o funcionamento do fluxo completo:
Injeção -> Detecção de Tópico -> Download de Dataset -> Busca Acadêmica (Artigo Base) -> Corretor CJK -> Geração de Relatório ABNT Qualis A1.
"""

import os
import sys
import json
import sqlite3

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "skills", "data-collector", "scripts"))
sys.path.insert(0, os.path.join(BASE, "skills", "simulation-runner", "scripts"))
sys.path.insert(0, os.path.join(BASE, "skills", "agent-forum", "scripts"))
sys.path.insert(0, os.path.join(BASE, "criador-artigo", "banca"))

from report_generator import ResearchReport

def run_validation():
    print("=" * 70)
    print("📡 VALIDANDO INJEÇÃO DE EVENTO E GERAÇÃO DE RELATÓRIO DINÂMICO")
    print("=" * 70)

    # 1. Simular Evento Injetado
    event = {
        "title": "Aprovação do Marco Regulatório de Inteligência Artificial",
        "description": "Nova legislação de IA aprovada no Congresso afeta custos de conformidade e adoção tecnológica pelas empresas.",
        "impact": 0.85,
        "duration": 5,
        "round": 1
    }
    print(f"\n1. Simulando Injeção de Evento: '{event['title']}'")
    
    # 2. Instanciar o Relatório
    fake_summary = {
        "total_agents": 200,
        "total_rounds": 30,
        "total_actions": 450,
        "avg_sentiment": -0.15,
        "topic_analysis": {
            "ia_impacto": {"mean": 0.45, "std": 0.12},
            "economia": {"mean": -0.25, "std": 0.35},
            "inovacao": {"mean": 0.65, "std": 0.08}
        }
    }
    report = ResearchReport(fake_summary)
    report.last_injected_event = event

    # 3. Validar detecção de tópico
    detected_topic = report._detect_event_topic()
    print(f"2. Tópico detectado: '{detected_topic}' (Esperado: 'ia_impacto')")
    assert detected_topic == "ia_impacto", f"Erro na detecção do tópico: {detected_topic}"
    print("   ✅ Tópico detectado corretamente!")

    # 4. Validar Download do Dataset (DataCollector)
    print("\n3. Executando DataCollector...")
    data_summary = report.collect_data()
    print(f"   ✅ Dataset carregado com sucesso! {len(data_summary.get('summary', {}).get('indicators', {}))} indicadores.")
    
    # 5. Validar Busca de Artigo Base e Citações (CitationFinder)
    print("\n4. Executando Busca Acadêmica de Artigo Base no Semantic Scholar...")
    citations = report.collect_citations()
    base_art = getattr(report, "base_article", None)
    
    if base_art:
        print(f"   ✅ Artigo Base Encontrado:")
        print(f"      Título:  {base_art.get('title')}")
        print(f"      Autores: {base_art.get('authors')}")
        print(f"      Ano:     {base_art.get('year')}")
        print(f"      DOI:     {base_art.get('doi')}")
    else:
        print("   ❌ Artigo Base não foi inicializado.")
        sys.exit(1)

    # 6. Salvar e Executar Corretor CJK
    print("\n5. Salvando Relatório Qualis A1 e aplicando ptbr_corrector...")
    output_path = report.save()
    print(f"   ✅ Relatório salvo e corrigido em: {output_path}")

    # 7. Validar Conteúdo do Relatório
    with open(output_path, "r", encoding="utf-8") as f:
        report_content = f.read()

    print("\n6. Validando conformidade Qualis A1...")
    # Verificar se o artigo base está citado
    base_author = base_art.get("authors", "").split(",")[0].strip()
    cite_string = f"({base_author},"
    assert cite_string in report_content or base_art.get("title")[:20] in report_content, "Erro: Artigo base não citado no texto!"
    print(f"   ✅ Artigo base citado corretamente no texto.")

    # Verificar CJK
    from ptbr_corrector import PTBRCorrector
    corrector = PTBRCorrector()
    issues = corrector.scan_text(report_content)
    assert len(issues) == 0, f"Erro: Caracteres CJK detectados no relatório! {issues}"
    print("   ✅ Zero caracteres CJK vazados na saída.")

    print("\n" + "=" * 70)
    print("🏆 PARABÉNS! Todo o fluxo integrado foi validado com 100% de sucesso!")
    print("=" * 70)

if __name__ == "__main__":
    run_validation()
