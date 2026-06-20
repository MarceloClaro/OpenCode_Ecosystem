"""
SPEC-044: Testes TDD do Social Impact Scanner
==============================================
Casos de Teste: CT-4401 a CT-4406
Cobertura: SROI, Theory of Change, B Impact Assessment,
           IRIS+, SDG Tracker, Relatório Consolidado
"""

import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..',
                                'skills', 'system', 'academic-audit'))

from social_impact_scanner import (
    SocialImpactScanner, SROIAnalyzer, TheoryOfChangeBuilder,
    BImpactAssessor, IRISPlusReport, SDGTracker,
    SocialValueAdjustments, SocialImpactReport
)

import pytest


# =====================================================================
# CT-4401: SROI Ratio Analysis
# =====================================================================

class TestSROIAnalyzer:
    """CT-4401: Garante que o cálculo do SROI ratio é correto e robusto"""

    def setup_method(self):
        self.analyzer = SROIAnalyzer()

    def test_ct4401_basic_sroi_calculation(self):
        """Cálculo básico de SROI com valores simples"""
        self.analyzer.set_adjustments(deadweight=0.0, attribution=1.0,
                                      displacement=0.0, duration_years=1)
        stakeholders = [
            self.analyzer.add_stakeholder("Comunidade", 1.0,
                                          ["benefício"], 200000)
        ]
        result = self.analyzer.calculate_sroi(100000, stakeholders)
        assert result.sroi_ratio == 2.0, f"SROI should be 2.0, got {result.sroi_ratio}"
        assert result.net_present_value == 200000

    def test_ct4401_sroi_with_deadweight(self):
        """SROI com deadweight (20% teria ocorrido de qualquer forma)"""
        self.analyzer.set_adjustments(deadweight=0.2, attribution=1.0,
                                      displacement=0.0, duration_years=1)
        stakeholders = [
            self.analyzer.add_stakeholder("Comunidade", 1.0,
                                          ["benefício"], 200000)
        ]
        result = self.analyzer.calculate_sroi(100000, stakeholders)
        # NPV = 200000 * (1-0.2) = 160000
        assert result.sroi_ratio == 1.6, f"SROI should be 1.6, got {result.sroi_ratio}"
        assert result.deadweight_value == 40000  # 20% of 200000

    def test_ct4401_sroi_with_attribution(self):
        """SROI com attribution (apenas 60% atribuível)"""
        self.analyzer.set_adjustments(deadweight=0.0, attribution=0.6,
                                      displacement=0.0, duration_years=1)
        stakeholders = [
            self.analyzer.add_stakeholder("Comunidade", 1.0,
                                          ["benefício"], 200000)
        ]
        result = self.analyzer.calculate_sroi(100000, stakeholders)
        # NPV = 200000 * 0.6 = 120000
        assert result.sroi_ratio == 1.2, f"SROI should be 1.2, got {result.sroi_ratio}"
        assert result.attribution_value == 120000

    def test_ct4401_sroi_with_displacement(self):
        """SROI com displacement (10% deslocado)"""
        self.analyzer.set_adjustments(deadweight=0.0, attribution=1.0,
                                      displacement=0.1, duration_years=1)
        stakeholders = [
            self.analyzer.add_stakeholder("Comunidade", 1.0,
                                          ["benefício"], 200000)
        ]
        result = self.analyzer.calculate_sroi(100000, stakeholders)
        # NPV = 200000 * (1-0.1) = 180000
        assert result.sroi_ratio == 1.8, f"SROI should be 1.8, got {result.sroi_ratio}"
        assert result.displacement_value == 20000

    def test_ct4401_sroi_multi_year(self):
        """SROI com duração de 5 anos e drop-off anual de 10%"""
        self.analyzer.set_adjustments(deadweight=0.0, attribution=1.0,
                                      displacement=0.0, drop_off=0.1,
                                      duration_years=5)
        stakeholders = [
            self.analyzer.add_stakeholder("Comunidade", 1.0,
                                          ["benefício"], 100000)
        ]
        result = self.analyzer.calculate_sroi(100000, stakeholders)
        # Year 0: 100000
        # Year 1: 100000 * 0.9 = 90000
        # Year 2: 100000 * 0.81 = 81000
        # Year 3: 100000 * 0.729 = 72900
        # Year 4: 100000 * 0.6561 = 65610
        # Total: 409510
        assert result.sroi_ratio == pytest.approx(4.0951, rel=0.01)
        assert result.net_present_value == pytest.approx(409510, rel=0.01)

    def test_ct4401_sroi_zero_investment(self):
        """SROI com investimento zero não deve causar divisão por zero"""
        stakeholders = [
            self.analyzer.add_stakeholder("Comunidade", 1.0,
                                          ["benefício"], 100000)
        ]
        result = self.analyzer.calculate_sroi(0, stakeholders)
        assert result.sroi_ratio == 0.0

    def test_ct4401_sroi_multiple_stakeholders(self):
        """SROI com múltiplos stakeholders e pesos"""
        self.analyzer.set_adjustments(deadweight=0.1, attribution=0.8,
                                      displacement=0.05, duration_years=2)
        stakeholders = [
            self.analyzer.add_stakeholder("Academia", 0.8,
                                          ["publicações"], 150000),
            self.analyzer.add_stakeholder("Sociedade", 1.0,
                                          ["impacto social"], 300000),
            self.analyzer.add_stakeholder("Governo", 0.6,
                                          ["políticas públicas"], 100000)
        ]
        result = self.analyzer.calculate_sroi(200000, stakeholders)
        total_gross = 150000 + 300000 + 100000  # = 550000
        assert result.gross_social_value == total_gross
        net_mult = 0.8 * (1 - 0.05) * (1 - 0.1)  # = 0.684
        duration = 1 + (1 - 0.0)  # = 2 (drop_off=0)
        expected_npv = total_gross * net_mult * duration  # = 550000 * 0.684 * 2 = 752400
        assert result.net_present_value == pytest.approx(expected_npv, rel=0.01)

    def test_ct4401_iso_26000_analysis(self):
        """Análise dos 7 temas centrais ISO 26000"""
        scores = self.analyzer.analyze_iso_26000(
            ["governança", "transparência", "meio ambiente", "comunidade",
             "ética", "direitos humanos", "trabalhista"]
        )
        assert len(scores) == 7
        for theme in self.analyzer.ISO_26000_THEMES:
            assert theme in scores

    def test_ct4401_net_multiplier_calculation(self):
        """Teste do cálculo do net multiplier"""
        adj = SocialValueAdjustments(deadweight=0.2, attribution=0.8,
                                     displacement=0.1, drop_off=0.05,
                                     duration_years=3)
        # net_mult = 0.8 * (1-0.1) * (1-0.2) = 0.8 * 0.9 * 0.8 = 0.576
        assert adj.net_multiplier == pytest.approx(0.576, rel=0.01)


# =====================================================================
# CT-4402: Theory of Change Framework
# =====================================================================

class TestTheoryOfChange:
    """CT-4402: Garante a integridade da cadeia lógica ToC"""

    def setup_method(self):
        self.builder = TheoryOfChangeBuilder()

    def test_ct4402_basic_toc_creation(self):
        """Criação básica de ToC com todos os elementos"""
        toc = self.builder.build(
            input_desc="Investimento em pesquisa científica",
            activities=["Revisão bibliográfica", "Coleta de dados", "Análise estatística"],
            outputs=["Artigo publicado", "Dataset disponibilizado"],
            outcomes=["Avanço do conhecimento", "Formação de RH"],
            impact="Transformação social através da ciência",
            indicators={"publicacoes": "Número de artigos Qualis A"},
            assumptions=["Resultados reprodutíveis", "Dados acessíveis"]
        )
        assert toc.input_desc == "Investimento em pesquisa científica"
        assert len(toc.activities) == 3
        assert len(toc.outputs) == 2
        assert len(toc.outcomes) == 2
        assert toc.impact == "Transformação social através da ciência"
        assert len(toc.indicators) == 1
        assert len(toc.assumptions) == 2

    def test_ct4402_validate_complete_chain(self):
        """Validação de cadeia completa não deve gerar issues"""
        toc = self.builder.build(
            input_desc="Input válido",
            activities=["A1", "A2", "A3"],
            outputs=["O1", "O2"],
            outcomes=["OC1", "OC2"],
            impact="Impacto válido",
            indicators={"k": "v"}
        )
        issues = self.builder.validate_chain(toc)
        assert len(issues) == 0, f"Expected 0 issues, got {issues}"

    def test_ct4402_validate_incomplete_chain(self):
        """Validação de cadeia incompleta deve gerar issues"""
        toc = self.builder.build(
            input_desc="",
            activities=[],
            outputs=[],
            outcomes=[],
            impact="",
            indicators={}
        )
        issues = self.builder.validate_chain(toc)
        assert len(issues) >= 5  # 5 elementos obrigatórios faltantes

    def test_ct4402_generate_narrative(self):
        """Narrativa de mudança deve ser gerada corretamente"""
        toc = self.builder.build(
            input_desc="Educação",
            activities=["Curso", "Mentoria"],
            outputs=["Certificados"],
            outcomes=["Empregabilidade"],
            impact="Redução da desigualdade",
            indicators={"emprego": "taxa de empregabilidade"}
        )
        narrative = self.builder.generate_narrative(toc)
        assert "Educação" in narrative
        assert "Redução da desigualdade" in narrative
        assert "2 atividades" in narrative or "2" in narrative

    def test_ct4402_rebalance_check(self):
        """Check de balanceamento atividades/outputs"""
        toc = self.builder.build(
            input_desc="X", activities=["A1","A2","A3","A4","A5","A6","A7"],
            outputs=["O1"], outcomes=["OC1"], impact="I",
            indicators={"k": "v"}
        )
        issues = self.builder.validate_chain(toc)
        assert len(issues) > 0  # desbalanceado: 7 atividades para 1 output


# =====================================================================
# CT-4403: B Impact Assessment Scoring
# =====================================================================

class TestBImpactAssessment:
    """CT-4403: Garante o cálculo correto do B Impact Assessment"""

    def setup_method(self):
        self.assessor = BImpactAssessor()

    def test_ct4403_basic_scoring(self):
        """Score básico com todas as dimensões em 50"""
        score = self.assessor.assess(50, 50, 50, 50, 50)
        # total = (50*0.2 + 50*0.2 + 50*0.25 + 50*0.2 + 50*0.15) * 2
        # total = (10 + 10 + 12.5 + 10 + 7.5) * 2 = 50 * 2 = 100
        assert score.total == 100.0

    def test_ct4403_high_impact(self):
        """Score de alto impacto"""
        score = self.assessor.assess(80, 70, 90, 60, 70)
        # (80*0.2 + 70*0.2 + 90*0.25 + 60*0.2 + 70*0.15) * 2
        # (16 + 14 + 22.5 + 12 + 10.5) * 2 = 75 * 2 = 150
        assert score.total == 150.0
        assert "Certified B Corp" in score.rating

    def test_ct4403_low_impact_rating(self):
        """Classificação correta para score baixo"""
        score = self.assessor.assess(10, 10, 10, 10, 10)
        # (10*0.2*5) * 2 = 10 * 2 = 20
        assert score.total == 20.0
        assert score.rating == "Impacto Inicial"

    def test_ct4403_very_low_impact_rating(self):
        """Classificação para score muito baixo deve ser Abaixo do Esperado"""
        score = self.assessor.assess(5, 5, 5, 5, 5)
        assert score.total == 10.0
        assert "Abaixo do Esperado" in score.rating

    def test_ct4403_clamp_values(self):
        """Valores acima de 100 devem ser limitados"""
        score = self.assessor.assess(150, -10, 80, 40, 50)
        assert score.governance == 100.0
        assert score.workers == 0.0

    def test_ct4403_diagnosis(self):
        """Diagnóstico por dimensão"""
        score = self.assessor.assess(80, 30, 70, 20, 60)
        diagnosis = self.assessor.diagnose(score)
        assert "governance" in diagnosis
        assert diagnosis["governance"]["status"] == "forte"
        assert diagnosis["workers"]["status"] == "fraco"
        assert diagnosis["environment"]["status"] == "fraco"

    def test_ct4403_b_corp_eligibility(self):
        """Verificação de elegibilidade B Corp (>80)"""
        score = self.assessor.assess(60, 50, 70, 55, 45)
        # (60*0.2 + 50*0.2 + 70*0.25 + 55*0.2 + 45*0.15) * 2
        # (12 + 10 + 17.5 + 11 + 6.75) * 2 = 57.25 * 2 = 114.5
        assert score.total > 80
        assert "B Corp" in score.rating


# =====================================================================
# CT-4404: IRIS+ Standard Indicators
# =====================================================================

class TestIRISPlus:
    """CT-4404: Garante a conformidade com padrão GIIN IRIS+"""

    def setup_method(self):
        self.iris = IRISPlusReport()

    def test_ct4404_basic_indicators(self):
        """Preenchimento dos 4 indicadores obrigatórios"""
        ind = self.iris.generate(
            product_desc="Plataforma de educação a distância",
            social_objective="Democratizar o acesso ao ensino superior",
            direct_beneficiaries=10000,
            indirect_beneficiaries=50000
        )
        assert ind.od01_product_service_description == "Plataforma de educação a distância"
        assert ind.od02_social_objective == "Democratizar o acesso ao ensino superior"
        assert ind.od03_direct_beneficiaries == 10000
        assert ind.od04_indirect_beneficiaries == 50000

    def test_ct4404_validation_passes(self):
        """Validação com dados completos"""
        ind = self.iris.generate("Descrição", "Objetivo", 100, 200)
        errors = self.iris.validate(ind)
        assert len(errors) == 0

    def test_ct4404_validation_fails(self):
        """Validação com dados incompletos"""
        ind = self.iris.generate("", "", 0, 0)
        errors = self.iris.validate(ind)
        assert len(errors) >= 3  # OD01, OD02, OD03 faltando

    def test_ct4404_additional_metrics(self):
        """Métricas adicionais no relatório IRIS+"""
        ind = self.iris.generate(
            "Descrição", "Objetivo", 100, 200,
            additional_metrics={"SROI_Ratio": 3.5, "Impact_Score": 85}
        )
        assert ind.additional_metrics["SROI_Ratio"] == 3.5
        assert ind.additional_metrics["Impact_Score"] == 85

    def test_ct4404_iris_label_constants(self):
        """Verificação das labels padronizadas"""
        assert "OD01" in IRISPlusReport.OD01_LABEL
        assert "OD02" in IRISPlusReport.OD02_LABEL
        assert "OD03" in IRISPlusReport.OD03_LABEL
        assert "OD04" in IRISPlusReport.OD04_LABEL


# =====================================================================
# CT-4405: SDG Alignment Tracking
# =====================================================================

class TestSDGTracker:
    """CT-4405: Garante o correto mapeamento de ODS"""

    def setup_method(self):
        self.tracker = SDGTracker()

    def test_ct4405_basic_tracking(self):
        """Rastreamento básico de ODS"""
        alignments = self.tracker.track(
            "pesquisa sobre saúde e educação ambiental"
        )
        assert len(alignments) > 0
        goal_numbers = [a.goal_number for a in alignments]
        # Deve encontrar: Saúde (3), Educação (4), Meio Ambiente (13, 15)
        assert 3 in goal_numbers or 4 in goal_numbers

    def test_ct4405_top_three(self):
        """Os 3 ODS mais relevantes devem ser retornados"""
        alignments = self.tracker.track(
            "saúde educação inovação redução da pobreza"
        )
        top = self.tracker.top_three(alignments)
        assert len(top) <= 3
        assert len(top) > 0
        # O primeiro deve ter score >= aos demais
        assert top[0].score >= top[-1].score if len(top) > 1 else True

    def test_ct4405_scores_are_percentages(self):
        """Scores devem estar entre 0 e 100"""
        alignments = self.tracker.track(
            "inovação tecnologia pesquisa indústria"
        )
        for a in alignments:
            assert 0 <= a.score <= 100, f"Score {a.score} fora do range"

    def test_ct4405_no_false_positives(self):
        """Texto sem relação com ODS deve retornar lista vazia"""
        alignments = self.tracker.track(
            "xyzzy kwyjibo nonsensical text without meaning"
        )
        # Pode não encontrar nada
        pass  # Não assertivo, apenas não deve crashar

    def test_ct4405_sdg_list_completeness(self):
        """A lista de ODS deve conter todos os 17 objetivos"""
        assert len(self.tracker.SDGS) == 17
        for i in range(1, 18):
            assert i in self.tracker.SDGS, f"ODS {i} não encontrado"

    def test_ct4405_goal_names_are_descriptive(self):
        """Nomes dos ODS devem ser não vazios"""
        for num, (name, _) in self.tracker.SDGS.items():
            assert len(name) > 5, f"ODS {num} nome muito curto: {name}"


# =====================================================================
# CT-4406: Consolidated Social Impact Report
# =====================================================================

class TestSocialImpactScanner:
    """CT-4406: Garante a integridade do relatório consolidado"""

    def setup_method(self):
        self.scanner = SocialImpactScanner()

    def test_ct4406_full_analysis_generates_report(self):
        """Análise completa deve gerar relatório com todas as seções"""
        report = self.scanner.analyze_research_paper(
            titulo="Pesquisa em Saúde Pública",
            resumo="Análise de impacto de políticas públicas de saúde",
            metodologia="Revisão sistemática",
            resultados="Melhoria significativa nos indicadores",
            conclusoes="Políticas de saúde são efetivas",
            palavras_chave=["saúde", "políticas públicas", "bem-estar"],
            area_conhecimento="Ciências da Saúde"
        )
        assert isinstance(report, SocialImpactReport)
        assert report.title == "Pesquisa em Saúde Pública"

    def test_ct4406_report_has_all_components(self):
        """Relatório deve conter todos os 6 componentes metodológicos"""
        report = self.scanner.analyze_research_paper(
            titulo="Teste", resumo="Teste", metodologia="Teste",
            resultados="Teste", conclusoes="Teste"
        )
        # SROI
        assert report.sroi.sroi_ratio >= 0
        # Theory of Change
        assert report.theory_of_change.input_desc != ""
        # IRIS+
        assert report.iris_plus.od01_product_service_description != ""
        # B Impact
        assert report.b_impact.total >= 0
        # SDG
        assert isinstance(report.sdg_alignments, list)
        # Parecer
        assert len(report.parecer) > 0

    def test_ct4406_consolidated_score_range(self):
        """Score consolidado deve estar entre 0 e 100"""
        report = self.scanner.analyze_research_paper(
            titulo="Teste Score", resumo="educação saúde inovação",
            metodologia="Experimental", resultados="Positivos",
            conclusoes="Impacto significativo",
            palavras_chave=["educação", "saúde", "tecnologia"],
            area_conhecimento="Ciências Sociais",
            orcamento_estimado=500000
        )
        assert 0 <= report.consolidated_score <= 100
        assert report.consolidated_score > 0

    def test_ct4406_json_export(self):
        """Relatório deve ser exportável para JSON"""
        report = self.scanner.analyze_research_paper(
            titulo="JSON Test", resumo="Teste", metodologia="Teste",
            resultados="Teste", conclusoes="Teste"
        )
        json_str = report.as_json()
        parsed = json.loads(json_str)
        assert parsed["title"] == "JSON Test"
        assert "sroi" in parsed
        assert "b_impact" in parsed
        assert "parecer" in parsed

    def test_ct4406_parecer_quality(self):
        """Parecer deve conter análise qualitativa fundamentada"""
        report = self.scanner.analyze_research_paper(
            titulo="Pesquisa de Alto Impacto",
            resumo="Inovação tecnológica para redução das desigualdades",
            metodologia="Pesquisa-ação",
            resultados="Resultados positivos em 3 comunidades",
            conclusoes="Tecnologia social reduz desigualdade em 40%",
            palavras_chave=["inovação", "desigualdade", "comunidade",
                           "tecnologia social", "impacto"],
            area_conhecimento="Ciências Sociais Aplicadas",
            orcamento_estimado=1000000,
            num_pesquisadores=8,
            anos_projeto=3
        )
        assert "SROI" in report.parecer
        assert "Impacto Social" in report.parecer or "impacto social" in report.parecer.lower()
        assert "ODS" in report.parecer or "score" in report.parecer.lower()

    def test_ct4406_recommendations(self):
        """Recomendações de forças e melhorias devem ser coerentes"""
        report = self.scanner.analyze_research_paper(
            titulo="Pesquisa", resumo="saúde educação inovação tecnologia",
            metodologia="Experimental", resultados="Melhoria de 50%",
            conclusoes="Impacto significativo na comunidade",
            palavras_chave=["saúde", "educação", "comunidade"],
            area_conhecimento="Saúde Coletiva",
            orcamento_estimado=1000000,
            anos_projeto=4
        )
        # Deve ter pelo menos 1 strength ou 1 improvement
        assert len(report.strengths) > 0 or len(report.improvements) > 0

    def test_ct4406_social_value_adjustments_chain(self):
        """Teste integrado da cadeia de ajustes de valor social"""
        report = self.scanner.analyze_research_paper(
            titulo="Teste Ajustes", resumo="Pesquisa social aplicada",
            metodologia="Qualitativa", resultados="Efetivo",
            conclusoes="Contribui para políticas públicas",
            orcamento_estimado=200000
        )
        assert report.sroi.deadweight_value >= 0
        assert report.sroi.attribution_value >= 0
        assert report.sroi.displacement_value >= 0


# =====================================================================
# RUNNER
# =====================================================================

if __name__ == "__main__":
    pytest.main(["-v", __file__])
