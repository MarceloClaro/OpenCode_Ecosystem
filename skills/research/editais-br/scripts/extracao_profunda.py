"""
extracao_profunda.py — Extracao de requisitos de editais em PDF/HTML.

Integra com docling-pdf-extraction do ecossistema para extracao
de layout, tabelas e reading order de editais de fomento.

Uso:
    python extracao_profunda.py edital.pdf
    python extracao_profunda.py https://exemplo.com/edital.pdf
    python extracao_profunda.py --modo itemizado edital.pdf
"""

import json
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


@dataclass
class RequisitoEdital:
    elegibilidade: list[dict] = field(default_factory=list)
    documentacao: list[str] = field(default_factory=list)
    prazos: dict = field(default_factory=dict)
    itens_orcamentarios: list[dict] = field(default_factory=list)
    criterios_selecao: list[dict] = field(default_factory=list)
    contrapartida: Optional[dict] = None
    restricoes: list[str] = field(default_factory=list)
    anexos: list[str] = field(default_factory=list)
    contato: Optional[dict] = None


# Padroes de extracao para editais brasileiros
PADROES_REQUISITOS = {
    "prazo_execucao": r"(?:prazo|periodo|duracao).{0,30}(?:execucao|projeto).{0,20}(\d+)\s*(?:mes|ano|mês|messe)",
    "valor_total": r"(?:valor|montante|investimento).{0,20}(?:total|global).{0,30}R?\$?\s*([\d.]+(?:,\d{2})?)",
    "valor_max_proposta": r"(?:valor|limite|tetro).{0,20}(?:maximo|máximo|por proposta).{0,30}R?\$?\s*([\d.]+(?:,\d{2})?)",
    "contrapartida_minima": r"(?:contrapartida).{0,30}(\d+)%\s*(?:do|da|de)",
    "vagas": r"(\d+)\s*(?:vaga|bolsa|proposta|projetos?)\s*(?:contemplado|selecionado|disponivel)",
    "data_limite": r"(?:data|prazo).{0,20}(?:limite|final|maximo).{0,30}(\d{2}/\d{2}/\d{4})",
}


def extrair_requisitos_texto(texto: str) -> RequisitoEdital:
    """Extrai requisitos de edital a partir de texto limpo."""
    req = RequisitoEdital()
    texto_lower = texto.lower()

    # Prazos
    for nome, pattern in PADROES_REQUISITOS.items():
        match = re.search(pattern, texto_lower)
        if match:
            req.prazos[nome] = match.group(1)

    # Datas limite
    datas = re.findall(r'(\d{2}[/-]\d{2}[/-]\d{4})', texto)
    if datas:
        req.prazos["datas_encontradas"] = datas

    # Elegibilidade - quem pode participar
    categorias_quem_quem = [
        ("pessoa_fisica", r"(?:pessoa fisica|pessoa física|PF|autonomo)"),
        ("pessoa_juridica", r"(?:pessoa juridica|pessoa jurídica|PJ|empresa)"),
        ("mei", r"(?:MEI|microempreendedor)"),
        ("osc", r"(?:OSC|organizacao sociedade civil|ongs?|terceiro setor)"),
        ("ict", r"(?:ICT|instituicao ciencia tecnologia|instituto pesquisa)"),
        ("universidade", r"(?:universidade|instituicao ensino|ies|faculdade)"),
        ("cooperativa", r"(?:cooperativa|associacao)"),
        ("pos_graduacao", r"(?:pos-graduacao|stricto|mestrado|doutorado)"),
    ]
    for categoria, padrao in categorias_quem_quem:
        if re.search(padrao, texto_lower):
            req.elegibilidade.append({"tipo": "proponente", "categoria": categoria})

    # Documentacao exigida
    docs_map = {
        "projeto_basico": r"(?:projeto basico|plano trabalho|proposta tecnica)",
        "cronograma": r"(?:cronograma|plano entregas)",
        "curriculo": r"(?:curriculo|CV|lattes|curriculum)",
        "certidoes": r"(?:certidao|certidão|regularidade fiscal|divida ativa)",
        "contrapartida_doc": r"(?:comprovacao contrapartida|comprovante contrapartida)",
        "declaracoes": r"(?:declaracao|declaração)(?!.{0,20}(?:falso|irregular))",
    }
    for nome, padrao in docs_map.items():
        if re.search(padrao, texto_lower):
            req.documentacao.append(nome)

    # Criterios de selecao
    criterios = re.findall(
        r"(?:criterio|critério|requisito).{0,30}(?:selecao|avaliacao|classificacao).{0,200}?(?:peso|nota|pontuacao).{0,10}?(\d+)",
        texto_lower
    )
    for peso in criterios:
        req.criterios_selecao.append({"criterio": "nao_classificado", "peso": int(peso)})

    # Itens orcamentarios
    valores = re.findall(r'R?\$?\s*([\d.]+,\d{2})', texto)
    for v in valores[:10]:
        req.itens_orcamentarios.append({"valor_encontrado": v})

    # Contrapartida
    cp = re.search(r"contrapartida.{0,50}(\d+)%", texto_lower)
    if cp:
        req.contrapartida = {"percentual": int(cp.group(1)), "tipo": "financeira"}
    else:
        cp_eco = re.search(r"contrapartida.{0,50}(?:economica|tecnica)", texto_lower, re.IGNORECASE)
        if cp_eco:
            req.contrapartida = {"tipo": "economica", "descricao": cp_eco.group(0)}

    # Restricoes
    restricoes_padroes = [
        r"nao.{0,20}(?:poderao|podem).{0,50}participar",
        r"impedimento",
        r"vedado",
        r"exclusao",
        r"inabilita",
    ]
    for p in restricoes_padroes:
        match = re.search(p, texto_lower)
        if match:
            req.restricoes.append(match.group(0))

    return req


def extrair_de_pdf(caminho_pdf: str) -> Optional[RequisitoEdital]:
    """Extrai requisitos de um PDF via pdfplumber (rapido), com fallback docling OCR.

    Args:
        caminho_pdf: Caminho local ou URL do PDF.

    Returns:
        RequisitoEdital com campos extraidos ou None em erro.
    """
    texto = None

    # Tenta pdfplumber primeiro (rapido, sem OCR)
    try:
        import pdfplumber
        with pdfplumber.open(caminho_pdf) as pdf:
            texto = "\n".join(page.extract_text() or "" for page in pdf.pages)
    except ImportError:
        print("Aviso: pdfplumber nao instalado. pip install pdfplumber")
    except Exception as e:
        print(f"[pdfplumber] erro: {e}")

    # Fallback docling OCR (lento, apenas se pdfplumber nao extraiu texto suficiente)
    if not texto or len(texto.strip()) < 100:
        try:
            from docling.document_converter import DocumentConverter
            converter = DocumentConverter()
            result = converter.convert(caminho_pdf)
            texto = result.document.export_to_markdown()
        except ImportError:
            pass
        except Exception as e:
            print(f"[docling] erro: {e}")

    if not texto:
        return None

    return extrair_requisitos_texto(texto)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Extracao profunda de requisitos de editais")
    parser.add_argument("fonte", help="Caminho do PDF ou URL")
    parser.add_argument("--modo", choices=["rapido", "itemizado"], default="rapido",
                        help="Modo de extracao")
    parser.add_argument("--json", action="store_true", help="Saida em JSON")
    args = parser.parse_args()

    print(f"[extracao] Processando: {args.fonte} (modo: {args.modo})")
    req = extrair_de_pdf(args.fonte)

    if not req:
        print("Erro: nao foi possivel extrair o texto do documento")
        sys.exit(1)

    if args.json:
        print(json.dumps(asdict(req), ensure_ascii=False, indent=2))
    else:
        print(f"\n=== Requisitos Extraidos ===")
        print(f"Elegibilidade: {len(req.elegibilidade)} itens")
        for e in req.elegibilidade:
            print(f"  - {e['categoria']} ({e['tipo']})")
        print(f"Documentacao: {len(req.documentacao)} itens")
        for d in req.documentacao:
            print(f"  - {d}")
        print(f"Prazos: {json.dumps(req.prazos, ensure_ascii=False)}")
        print(f"Contrapartida: {req.contrapartida}")
        print(f"Restricoes: {len(req.restricoes)}")
        print(f"Criterios Selecao: {len(req.criterios_selecao)}")


if __name__ == "__main__":
    main()
