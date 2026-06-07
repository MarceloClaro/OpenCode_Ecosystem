#!/usr/bin/env python3
"""Gerador de pecas juridicas HTML v2.0.

Uso:
    python scripts/gerador_peca_html.py --list
    python scripts/gerador_peca_html.py --tipo pi --output ./peca.html
    python scripts/gerador_peca_html.py --tipo ct --dados '{"autor": "Joao"}' --output ./ct.html
    python scripts/gerador_peca_html.py --tipo ed --placeholder
"""

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path


TIPOS_PECA = {
    "pi": {
        "nome": "Peticao Inicial",
        "secoes": ["enderecamento", "qualificacao", "dos-fatos", "do-direito", "dos-pedidos", "fechamento"],
        "placeholders": [
            "autor", "nacionalidade", "estado_civil", "profissao", "cpf",
            "email", "endereco", "narrativa_fatos", "fundamentacao_juridica",
            "pedido_1", "pedido_2", "valor_causa", "cidade", "data",
            "nome_advogado", "oab"
        ],
        "classes": "peca-pi",
    },
    "ct": {
        "nome": "Contestacao",
        "secoes": ["enderecamento", "preliminares", "merito", "dos-pedidos", "fechamento"],
        "placeholders": [
            "autor", "reu", "processo", "preliminares", "merito",
            "pedido_1", "pedido_2", "cidade", "data",
            "nome_advogado", "oab"
        ],
        "classes": "peca-ct",
    },
    "rp": {
        "nome": "Replica",
        "secoes": ["enderecamento", "preliminares", "merito", "dos-pedidos", "fechamento"],
        "placeholders": [
            "autor", "reu", "processo", "preliminares", "merito",
            "pedido_1", "cidade", "data", "nome_advogado", "oab"
        ],
        "classes": "peca-rp",
    },
    "ai": {
        "nome": "Agravo de Instrumento",
        "secoes": ["enderecamento", "decisao-recorrida", "do-recurso", "dos-pedidos", "fechamento"],
        "placeholders": [
            "agravante", "agravado", "processo", "decisao_recorrida",
            "data_publicacao", "fundamentos_recurso", "pedido_1",
            "cidade", "data", "nome_advogado", "oab"
        ],
        "classes": "peca-ai",
    },
    "ap": {
        "nome": "Apelacao",
        "secoes": ["enderecamento", "razoes", "preliminares", "merito", "dos-pedidos", "fechamento"],
        "placeholders": [
            "apelante", "apelado", "processo", "razoes_recurso",
            "preliminares", "merito", "pedido_1", "cidade", "data",
            "nome_advogado", "oab"
        ],
        "classes": "peca-ap",
    },
    "ed": {
        "nome": "Embargos de Declaracao",
        "secoes": ["enderecamento", "tempestividade", "fundamentos", "dos-pedidos", "fechamento"],
        "placeholders": [
            "embargante", "embargado", "processo", "tempestividade",
            "obscuridade", "contradicao", "omissao", "pedido_1",
            "cidade", "data", "nome_advogado", "oab"
        ],
        "classes": "peca-ed",
    },
    "cr": {
        "nome": "Contrarrazoes",
        "secoes": ["enderecamento", "preliminares", "contra-razoes", "dos-pedidos", "fechamento"],
        "placeholders": [
            "recorrido", "recorrente", "processo", "preliminares",
            "contra_razoes", "pedido_1", "cidade", "data",
            "nome_advogado", "oab"
        ],
        "classes": "peca-cr",
    },
    "pr": {
        "nome": "Parecer",
        "secoes": ["enderecamento", "relatorio", "fundamentacao", "conclusao", "fechamento"],
        "placeholders": [
            "solicitante", "processo", "relatorio", "fundamentacao",
            "conclusao", "cidade", "data", "nome_advogado", "oab"
        ],
        "classes": "peca-pr",
    },
}

CSS_BASE = """@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600&family=DM+Sans:ital,wght@0,400;0,500;1,400&display=swap');
@page { margin: 20mm 20mm 20mm 32mm; size: A4; }
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'DM Sans', sans-serif; font-size: 15px; line-height: 1.65; color: #2D2A24; background: #FEFDFB; }
.doc { border-left: 6px solid #B08A4E; padding: 40px 20px 40px 52px; page-break-inside: avoid; orphans: 3; widows: 3; }
h1, h2, h3, h4 { font-family: 'Space Grotesk', sans-serif; color: #1C1B18; }
h1 { font-size: 18px; margin-bottom: 32px; padding-bottom: 8px; border-bottom: 1px solid #E8E3DC; }
h2 { font-size: 16px; margin-bottom: 16px; page-break-after: avoid; }
p { margin-bottom: 12px; text-align: justify; orphans: 3; widows: 3; }
.citacao { font-style: italic; font-size: 12.5px; margin: 12px 2cm; padding: 12px 16px; border-left: 3px solid #D4C9B8; }
.fonte-julgado { font-style: normal; font-size: 11px; color: #6B5E4E; }
.cabecalho { display: flex; justify-content: space-between; margin-bottom: 30px; }
.fechamento { margin-top: 40px; text-align: center; }
.assinatura { margin-top: 60px; }
.advogado-nome { font-weight: 500; }
.local-data { margin-top: 32px; }
.pedidos-lista { list-style: lower-alpha; margin-left: 2cm; }
.pedidos-lista li { margin-bottom: 8px; }
@media print { .doc { padding: 0; } }
"""


def css_para_8_tipos():
    return CSS_BASE


def html_para_secao(tag, classe, conteudo):
    if tag == "section":
        return f'  <section class="secao {classe}">\n{conteudo}\n  </section>'
    return ""


def gerar_secao_enderecamento(tipo, dados):
    if tipo in ("pi", "ct", "rp", "cr"):
        return """    <p>EXCELENTISSIMO SENHOR DOUTOR JUIZ DE DIREITO DA ___ VARA ___ DA COMARCA DE ___</p>"""
    elif tipo in ("ai", "ap", "ed"):
        return """    <p>EXCELENTISSIMO SENHOR DOUTOR DESEMBARGADOR PRESIDENTE DO TRIBUNAL ___</p>"""
    return """    <p>EXCELENTISSIMO SENHOR DOUTOR(A) ___(CARGO)___</p>"""


def gerar_secao(tipo_secao, tipo_peca, dados):
    if tipo_secao == "enderecamento":
        return gerar_secao_enderecamento(tipo_peca, dados)
    elif tipo_secao == "qualificacao":
        return f"""    <p>{dados.get('autor', '{{ autor }}')}, {dados.get('nacionalidade', '{{ nacionalidade }}')}, {dados.get('estado_civil', '{{ estado_civil }}')}, {dados.get('profissao', '{{ profissao }}')}, portador do CPF sob n. {dados.get('cpf', '{{ cpf }}')},</p>
    <p>endereco eletronico {dados.get('email', '{{ email }}')}, residente e domiciliado {dados.get('endereco', '{{ endereco }}')},</p>
    <p>por seu advogado que esta subscreve, vem, respeitosamente, a presenca de Vossa Excelencia, propor</p>"""
    elif tipo_secao == "dos-fatos":
        return f"""    <h2>I — DOS FATOS</h2>
    <p>{dados.get('narrativa_fatos', '{{ narrativa_fatos }}')}</p>"""
    elif tipo_secao == "do-direito":
        return f"""    <h2>II — DO DIREITO</h2>
    <p>{dados.get('fundamentacao_juridica', '{{ fundamentacao_juridica }}')}</p>"""
    elif tipo_secao == "dos-pedidos":
            p1 = dados.get('pedido_1', '{{ pedido_1 }}')
            p2 = dados.get('pedido_2')
            return f"""    <h2>III — DOS PEDIDOS</h2>
    <p>Ante o exposto, requer:</p>
    <ol class="pedidos-lista">
      <li>{p1}</li>
      {f'<li>{p2}</li>' if p2 else ''}
    </ol>
    <p>Da-se a causa o valor de {dados.get('valor_causa', '{{ valor_causa }}')}.</p>"""
    elif tipo_secao == "fechamento":
        return f"""    <p>Nestes termos, pede deferimento.</p>
    <p class="local-data">{dados.get('cidade', '{{ cidade }}')}, {dados.get('data', '{{ data }}')}.</p>
    <div class="assinatura">
      <p class="advogado-nome">{dados.get('nome_advogado', '{{ nome_advogado }}')}</p>
      <p class="advogado-oab">{dados.get('oab', '{{ oab }}')}</p>
    </div>"""
    elif tipo_secao == "preliminares":
        return f"""    <h2>I — DAS PRELIMINARES</h2>
    <p>{dados.get('preliminares', '{{ preliminares }}')}</p>"""
    elif tipo_secao == "merito":
        return f"""    <h2>II — DO MERITO</h2>
    <p>{dados.get('merito', '{{ merito }}')}</p>"""
    elif tipo_secao == "decisao-recorrida":
        return f"""    <h2>I — DA DECISAO RECORRIDA</h2>
    <p>{dados.get('decisao_recorrida', '{{ decisao_recorrida }}')}</p>"""
    elif tipo_secao == "do-recurso":
        return f"""    <h2>II — DO RECURSO</h2>
    <p>{dados.get('fundamentos_recurso', '{{ fundamentos_recurso }}')}</p>"""
    elif tipo_secao == "razoes":
        return f"""    <h2>I — DAS RAZOES RECURSAIS</h2>
    <p>{dados.get('razoes_recurso', '{{ razoes_recurso }}')}</p>"""
    elif tipo_secao == "tempestividade":
        return f"""    <h2>I — DA TEMPESTIVIDADE</h2>
    <p>{dados.get('tempestividade', '{{ tempestividade }}')}</p>"""
    elif tipo_secao == "fundamentos":
        return f"""    <h2>II — DOS FUNDAMENTOS</h2>
    <p>O presente embargo visa aclarar {dados.get('obscuridade', '{{ obscuridade }}')}, {dados.get('contradicao', '{{ contradicao }}')}, {dados.get('omissao', '{{ omissao }}')}.</p>"""
    elif tipo_secao == "contra-razoes":
        return f"""    <h2>II — DAS CONTRA-RAZOES</h2>
    <p>{dados.get('contra_razoes', '{{ contra_razoes }}')}</p>"""
    elif tipo_secao == "relatorio":
        return f"""    <h2>I — RELATORIO</h2>
    <p>{dados.get('relatorio', '{{ relatorio }}')}</p>"""
    elif tipo_secao == "fundamentacao":
        return f"""    <h2>II — DA FUNDAMENTACAO</h2>
    <p>{dados.get('fundamentacao', '{{ fundamentacao }}')}</p>"""
    elif tipo_secao == "conclusao":
        return f"""    <h2>III — CONCLUSAO</h2>
    <p>{dados.get('conclusao', '{{ conclusao }}')}</p>"""
    return f"""    <p>{{ {tipo_secao} }}</p>"""


def gerar_html(tipo, dados):
    info = TIPOS_PECA.get(tipo)
    if not info:
        raise ValueError(f"Tipo desconhecido: {tipo}")

    secoes_html = ""
    for secao in info["secoes"]:
        conteudo = gerar_secao(secao, tipo, dados)
        secoes_html += f"""  <section class="secao {secao}">\n{conteudo}\n  </section>\n"""

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{info['nome']}</title>
<style>
{css_para_8_tipos()}
</style>
</head>
<body>
<div class="doc {info['classes']}">
{secoes_html}
</div>
</body>
</html>"""
    return html


def listar_tipos():
    print("Tipos de peca disponiveis:")
    print(f"{'Sigla':<6} {'Nome':<25} {'Secoes':<50} {'Placeholders':<10}")
    print("-" * 91)
    for sigla, info in TIPOS_PECA.items():
        secs = ", ".join(info["secoes"])
        phs = str(len(info["placeholders"]))
        print(f"{sigla:<6} {info['nome']:<25} {secs:<50} {phs:<10}")


def listar_placeholders(tipo):
    info = TIPOS_PECA.get(tipo)
    if not info:
        print(f"Erro: tipo '{tipo}' nao encontrado. Use --list para ver os tipos disponiveis.", file=sys.stderr)
        sys.exit(1)
    print(f"Placeholders para {info['nome']} ({tipo}):")
    for ph in info["placeholders"]:
        print(f"  {ph}")


def validar_dados(tipo, dados):
    info = TIPOS_PECA.get(tipo)
    if not info:
        return False, "Tipo desconhecido"
    ausentes = [ph for ph in info["placeholders"] if ph not in dados]
    if ausentes:
        return False, f"Placeholders ausentes: {', '.join(ausentes)}"
    return True, "OK"


def main():
    parser = argparse.ArgumentParser(description="Gerador de pecas juridicas HTML v2.0")
    parser.add_argument("--tipo", choices=list(TIPOS_PECA.keys()), help="Tipo de peca")
    parser.add_argument("--dados", type=str, default="{}", help="JSON com dados para placeholders")
    parser.add_argument("--arquivo-dados", type=str, help="Arquivo JSON com dados")
    parser.add_argument("--output", type=str, default="./output.html", help="Caminho do arquivo de saida")
    parser.add_argument("--placeholder", action="store_true", help="Listar placeholders do tipo e sair")
    parser.add_argument("--list", action="store_true", help="Listar tipos disponiveis e sair")
    parser.add_argument("--abrir", action="store_true", help="Abrir navegador apos geracao")

    args = parser.parse_args()

    if args.list:
        listar_tipos()
        return

    if not args.tipo:
        parser.error("--tipo e obrigatorio (use --list para ver tipos)")

    if args.placeholder:
        listar_placeholders(args.tipo)
        return

    if args.arquivo_dados:
        try:
            with open(args.arquivo_dados, encoding="utf-8") as f:
                dados = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Erro ao ler arquivo de dados: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        try:
            dados = json.loads(args.dados)
        except json.JSONDecodeError as e:
            print(f"Erro ao parsear JSON: {e}", file=sys.stderr)
            sys.exit(1)

    if "data" not in dados:
        dados["data"] = date.today().strftime("%d de %B de %Y").lower()
    if "cidade" not in dados:
        dados["cidade"] = "[cidade]"

    try:
        html = gerar_html(args.tipo, dados)
    except ValueError as e:
        print(f"Erro: {e}", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    print(f"Peca gerada: {output_path.resolve()}")

    if args.abrir:
        import subprocess
        subprocess.Popen(["start", str(output_path.resolve())], shell=True)


if __name__ == "__main__":
    main()
