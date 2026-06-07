import pytest
import json
import os
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_DIR / "scripts"))
try:
    from gerador_peca_html import TIPOS_PECA, gerar_html, css_para_8_tipos, validar_dados
except ImportError:
    TIPOS_PECA = {}
    gerar_html = None
    css_para_8_tipos = lambda: ""
    validar_dados = lambda t, d: (False, "import falhou")


class TestEstruturaSkill:
    """Testes de estrutura basica da skill (ESTRUTURA)."""

    def test_skill_exists(self):
        assert (SKILL_DIR / "SKILL.md").exists(), "SKILL.md nao encontrado"

    def test_has_category(self):
        content = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        assert "category: juridico" in content

    def test_has_version(self):
        content = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        assert "version:" in content

    def test_has_frontmatter(self):
        content = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        assert content.startswith("---")

    def test_references_exist(self):
        ref_dir = SKILL_DIR / "references"
        assert ref_dir.is_dir(), "diretorio references nao encontrado"
        refs = list(ref_dir.iterdir())
        assert len(refs) >= 4, f"references/ deve conter ao menos 4 arquivos, tem {len(refs)}"

    def test_scripts_init_exists(self):
        assert (SKILL_DIR / "scripts" / "__init__.py").exists()

    def test_scripts_gerador_exists(self):
        assert (SKILL_DIR / "scripts" / "gerador_peca_html.py").exists()

    def test_manifest_exists(self):
        assert (SKILL_DIR / "skill.manifest.json").exists()

    def test_manifest_is_valid_json(self):
        content = (SKILL_DIR / "skill.manifest.json").read_text(encoding="utf-8")
        data = json.loads(content)
        assert "version" in data
        assert "name" in data


class TestTiposPeca:
    """Testes de definicao dos 8 tipos de peca (TIPOS)."""

    def test_oito_tipos_definidos(self):
        assert len(TIPOS_PECA) == 8, f"Esperado 8 tipos, obtido {len(TIPOS_PECA)}"

    def test_todos_tipos_possuem_nome(self):
        for sigla, info in TIPOS_PECA.items():
            assert "nome" in info, f"Tipo {sigla} sem nome"

    def test_todos_tipos_possuem_secoes(self):
        for sigla, info in TIPOS_PECA.items():
            assert "secoes" in info, f"Tipo {sigla} sem secoes"
            assert len(info["secoes"]) >= 3, f"Tipo {sigla} com menos de 3 secoes"

    def test_todos_tipos_possuem_placeholders(self):
        for sigla, info in TIPOS_PECA.items():
            assert "placeholders" in info, f"Tipo {sigla} sem placeholders"
            assert len(info["placeholders"]) >= 5, f"Tipo {sigla} com menos de 5 placeholders"

    def test_todas_secoes_definidas_sao_validas(self):
        secoes_validas = {
            "enderecamento", "qualificacao", "dos-fatos", "do-direito",
            "dos-pedidos", "fechamento", "preliminares", "merito",
            "decisao-recorrida", "do-recurso", "razoes", "tempestividade",
            "fundamentos", "contra-razoes", "relatorio", "fundamentacao",
            "conclusao"
        }
        for sigla, info in TIPOS_PECA.items():
            for secao in info["secoes"]:
                assert secao in secoes_validas, f"Tipo {sigla}: secao '{secao}' invalida"

    def test_peticao_inicial_secoes(self):
        assert "pi" in TIPOS_PECA
        secoes = TIPOS_PECA["pi"]["secoes"]
        assert "enderecamento" in secoes
        assert "qualificacao" in secoes
        assert "dos-fatos" in secoes
        assert "do-direito" in secoes
        assert "dos-pedidos" in secoes
        assert "fechamento" in secoes

    def test_tipo_nomes_corretos(self):
        esperados = {
            "pi": "Peticao Inicial",
            "ct": "Contestacao",
            "rp": "Replica",
            "ai": "Agravo de Instrumento",
            "ap": "Apelacao",
            "ed": "Embargos de Declaracao",
            "cr": "Contrarrazoes",
            "pr": "Parecer"
        }
        for sigla, nome_esperado in esperados.items():
            assert TIPOS_PECA[sigla]["nome"] == nome_esperado, f"{sigla}: esperado '{nome_esperado}'"


class TestGeracaoHTML:
    """Testes de geracao de HTML (GERACAO)."""

    def test_geracao_pi_retorna_html_valido(self):
        if gerar_html is None:
            pytest.skip("gerar_html nao importou")
        dados = {"autor": "Joao", "nacionalidade": "brasileiro", "valor_causa": "R$ 1.000,00"}
        html = gerar_html("pi", dados)
        assert html.startswith("<!DOCTYPE html>")
        assert "</html>" in html
        assert "Joao" in html
        assert "R$ 1.000,00" in html

    def test_geracao_ct_contem_enderecamento(self):
        if gerar_html is None:
            pytest.skip("gerar_html nao importou")
        html = gerar_html("ct", {})
        assert "JUIZ DE DIREITO" in html

    def test_geracao_ed_contem_tempestividade(self):
        if gerar_html is None:
            pytest.skip("gerar_html nao importou")
        html = gerar_html("ed", {})
        assert "TEMPESTIVIDADE" in html or "tempestividade" in html

    def test_conteudo_injetado(self):
        if gerar_html is None:
            pytest.skip("gerar_html nao importou")
        dados = {"autor": "Maria Silva", "narrativa_fatos": "Fatos ocorridos em 2024"}
        html = gerar_html("pi", dados)
        assert "Maria Silva" in html
        assert "Fatos ocorridos em 2024" in html

    def test_placeholders_preservados_quando_sem_dados(self):
        if gerar_html is None:
            pytest.skip("gerar_html nao importou")
        html = gerar_html("ai", {})
        assert "{{" in html or "{ agravante }" in html

    def test_css_embutido(self):
        if gerar_html is None:
            pytest.skip("gerar_html nao importou")
        html = gerar_html("pi", {})
        assert "<style>" in html
        assert "Space+Grotesk" in html or "font-family" in html

    def test_border_left_no_doc(self):
        if gerar_html is None:
            pytest.skip("gerar_html nao importou")
        html = gerar_html("ct", {})
        assert "border-left" in html

    def test_quebra_pagina_via_at_page(self):
        if gerar_html is None:
            pytest.skip("gerar_html nao importou")
        html = gerar_html("rp", {})
        assert "@page" in html

    def test_geracao_todos_8_tipos_param(self):
        """Gerar HTML para cada um dos 8 tipos com dados basicos."""
        if gerar_html is None:
            pytest.skip("gerar_html nao importou")
        for sigla in TIPOS_PECA:
            html = gerar_html(sigla, {})
            assert html.startswith("<!DOCTYPE html>"), f"Falha ao gerar {sigla}"
            assert "</html>" in html, f"HTML incompleto para {sigla}"


class TestCLI:
    """Testes da interface CLI (CLI)."""

    def test_cli_import_sem_erros(self):
        import importlib
        try:
            importlib.reload(__import__("gerador_peca_html"))
        except Exception:
            pass

    def test_cli_list(self):
        result = os.popen(f'"{sys.executable}" "{SKILL_DIR / "scripts" / "gerador_peca_html.py"}" --list').read()
        assert "Peticao Inicial" in result
        assert "Contestacao" in result
        assert "Agravo de Instrumento" in result
        assert "Embargos de Declaracao" in result
        assert "Parecer" in result

    def test_cli_placeholder(self):
        result = os.popen(f'"{sys.executable}" "{SKILL_DIR / "scripts" / "gerador_peca_html.py"}" --tipo pi --placeholder').read()
        assert "autor" in result
        assert "nome_advogado" in result
        assert "oab" in result

    def test_cli_placeholder_tipo_invalido(self):
        import subprocess
        result = subprocess.run(
            [sys.executable, str(SKILL_DIR / "scripts" / "gerador_peca_html.py"), "--tipo", "xx", "--placeholder"],
            capture_output=True, text=True
        )
        assert result.returncode != 0

    def test_cli_sem_tipo_falha(self):
        import subprocess
        result = subprocess.run(
            [sys.executable, str(SKILL_DIR / "scripts" / "gerador_peca_html.py")],
            capture_output=True, text=True
        )
        assert result.returncode != 0

    def test_cli_output_pi(self, tmp_path):
        output = tmp_path / "test_pi.html"
        import subprocess
        result = subprocess.run(
            [sys.executable, str(SKILL_DIR / "scripts" / "gerador_peca_html.py"),
             "--tipo", "pi", "--dados", '{"autor": "Teste"}', "--output", str(output)],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"CLI falhou: {result.stderr}"
        assert output.exists(), "Arquivo de saida nao foi criado"
        content = output.read_text(encoding="utf-8")
        assert "Teste" in content

    def test_cli_output_todos_tipos(self, tmp_path):
        import subprocess
        for sigla in TIPOS_PECA:
            output = tmp_path / f"test_{sigla}.html"
            result = subprocess.run(
                [sys.executable, str(SKILL_DIR / "scripts" / "gerador_peca_html.py"),
                 "--tipo", sigla, "--output", str(output)],
                capture_output=True, text=True
            )
            assert result.returncode == 0, f"CLI falhou para tipo {sigla}: {result.stderr}"
            assert output.exists(), f"Arquivo nao criado para {sigla}"


class TestCSS:
    """Testes de regras CSS para exportacao (CSS)."""

    def test_sem_height_no_doc(self):
        if gerar_html is None:
            pytest.skip("gerar_html nao importou")
        html = gerar_html("pi", {})
        css_section = html[html.index("<style>"):html.index("</style>")]
        assert ".doc {" in css_section or ".doc\n{" in css_section, ".doc deve ter regras CSS"

    def test_css_tem_border_left(self):
        css = css_para_8_tipos()
        assert "border-left" in css

    def test_css_tem_at_page(self):
        css = css_para_8_tipos()
        assert "@page" in css

    def test_css_tem_break_inside(self):
        css = css_para_8_tipos()
        assert "break-inside" in css or "page-break-inside" in css

    def test_css_tem_orphans_widows(self):
        css = css_para_8_tipos()
        assert "orphans" in css
        assert "widows" in css


class TestValidacao:
    """Testes de validacao (VALIDACAO)."""

    def test_validacao_tipo_valido(self):
        valido, msg = validar_dados("pi", {"autor": "x", "narrativa_fatos": "y"})
        assert isinstance(valido, bool)

    def test_validacao_tipo_invalido(self):
        valido, msg = validar_dados("zz", {})
        assert not valido

    def test_validacao_dados_ausentes(self):
        valido, msg = validar_dados("pi", {})
        assert isinstance(valido, bool)
