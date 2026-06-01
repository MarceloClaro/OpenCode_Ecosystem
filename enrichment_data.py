#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dados de enriquecimento para fichamentos da monografia.
Contem referencias bibliograficas completas + excertos originais,
traducoes e paginas para cada passagem citada.

Estrutura:
  REFERENCES[cite_key] = {
      "author": str,
      "title": str,
      "year": str,
      "publisher": str,
      "type": "magisterio"|"livro"|"artigo"|"legislacao",
      "url": str (opcional),
  }

  PASSAGES[cite_key] = [
      {
          "ref": str (paragrafo/secao/artigo),
          "orig": str (excerto original, vazio se nao localizado),
          "traducao": str (traducao PT-BR, vazio se ja em PT),
          "paginas": str (paginas especificas, vazio se nao aplicavel),
      }
  ]
"""

# ============================================================
# REFERENCIAS BIBLIOGRAFICAS COMPLETAS
# ============================================================
# Dados extraidos de refs.bib para todas as chaves citadas
# nos fichamentos de anexo-fichamentos.tex

REFERENCES = {
    # --- MAGISTERIO PONTIFICIO ---
    "LeaoXIV2026MH": {
        "author": "Leão XIV",
        "title": "Carta Encíclica *Magnifica Humanitas*: sobre a dignidade e a vocação da pessoa humana na era da inteligência artificial",
        "year": "2026",
        "publisher": "Libreria Editrice Vaticana",
        "type": "magisterio",
        "url": "https://www.vatican.va/content/leone-xiv/pt/encyclicals.index.html",
    },
    "Francisco2015LS": {
        "author": "Francisco",
        "title": "Carta Encíclica *Laudato Si'*: sobre o cuidado da casa comum",
        "year": "2015",
        "publisher": "Libreria Editrice Vaticana",
        "type": "magisterio",
        "url": "https://www.vatican.va/content/francesco/pt/encyclicals.index.html",
    },
    "JoaoPauloII1991CA": {
        "author": "João Paulo II",
        "title": "Carta Encíclica *Centesimus Annus*",
        "year": "1991",
        "publisher": "Libreria Editrice Vaticana",
        "type": "magisterio",
        "url": "https://www.vatican.va/content/john-paul-ii/pt/encyclicals.index.html",
    },
    "JoaoXXIII1963PT": {
        "author": "João XXIII",
        "title": "Carta Encíclica *Pacem in Terris*: sobre a paz de todos os povos na base da verdade, justiça, caridade e liberdade",
        "year": "1963",
        "publisher": "Libreria Editrice Vaticana",
        "type": "magisterio",
        "url": "https://www.vatican.va/content/john-xxiii/pt/encyclicals.index.html",
    },
    # --- LIVROS ---
    "Bioni2021PPD": {
        "author": "Bioni, Bruno Ricardo",
        "title": "Proteção de Dados Pessoais: A Função e os Limites do Consentimento",
        "year": "2021",
        "publisher": "Forense",
        "type": "livro",
        "url": "",
    },
    "Doneda2006PDD": {
        "author": "Doneda, Danilo",
        "title": "Da privacidade à proteção dos dados pessoais",
        "year": "2006",
        "publisher": "Renovar",
        "type": "livro",
        "url": "",
    },
    "Rodota2008PDA": {
        "author": "Rodotà, Stefano",
        "title": "A Privacidade entre a Proteção de Dados e a Dignidade da Pessoa",
        "year": "2008",
        "publisher": "Instituto Piaget",
        "type": "livro",
        "url": "",
    },
    "Castells2010EI": {
        "author": "Castells, Manuel",
        "title": "A Era da Informação: Economia, Sociedade e Cultura",
        "year": "2010",
        "publisher": "Paz e Terra",
        "type": "livro",
        "url": "",
    },
    "Zuboff2019SC": {
        "author": "Zuboff, Shoshana",
        "title": "A Era do Capitalismo de Vigilância: a luta por um futuro humano na nova fronteira do poder",
        "year": "2019",
        "publisher": "Intrínseca",
        "type": "livro",
        "url": "",
    },
    # --- ARTIGOS ---
    "Floridi2018AIP": {
        "author": "Floridi, Luciano; Cowls, Josh",
        "title": "A Unified Framework of Five Principles for AI in Society",
        "year": "2018",
        "publisher": "Harvard Data Science Review, v. 1, n. 1",
        "type": "artigo",
        "url": "",
    },
    "Calo2017AIL": {
        "author": "Calo, Ryan",
        "title": "Artificial Intelligence Policy: A Primer and Roadmap",
        "year": "2017",
        "publisher": "UC Davis Law Review, v. 51, pp. 399-435",
        "type": "artigo",
        "url": "",
    },
    # --- LEGISLACAO ---
    "Brasil1988CF": {
        "author": "Brasil",
        "title": "Constituição da República Federativa do Brasil de 1988",
        "year": "1988",
        "publisher": "Senado Federal",
        "type": "legislacao",
        "url": "https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm",
    },
    "Brasil2018LGPD": {
        "author": "Brasil",
        "title": "Lei nº 13.709, de 14 de agosto de 2018. Lei Geral de Proteção de Dados Pessoais (LGPD)",
        "year": "2018",
        "publisher": "Diário Oficial da União",
        "type": "legislacao",
        "url": "https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm",
    },
    "Brasil2023PL2338": {
        "author": "Brasil",
        "title": "Projeto de Lei nº 2.338, de 2023. Dispõe sobre o uso da Inteligência Artificial",
        "year": "2023",
        "publisher": "Câmara dos Deputados",
        "type": "legislacao",
        "url": "https://www.camara.leg.br/proposicoesWeb/fichadetramitacao?idProposicao=2370492",
    },
}

# ============================================================
# PASSAGENS (EXCERTOS ORIGINAIS, TRADUCOES, PAGINAS)
# ============================================================
# Para cada cite_key, lista de passagens citadas nos fichamentos.
# Campos:
#   ref:      paragrafo/secao/artigo citado (ex.: "§ 5", "Art. 1º")
#   orig:     excerto no idioma original (vazio se ainda nao localizado)
#   traducao: traducao PT-BR (vazio se o original ja esta em PT)
#   paginas:  paginas especificas na edicao de referencia
#
# IMPORTANTE: Campos vazios indicam que o dado precisa ser
# preenchido manualmente apos consulta ao texto-fonte.
# Para enciclicas, a referencia canonica e o paragrafo (§),
# nao o numero de pagina.

PASSAGES = {
    "LeaoXIV2026MH": [
        {
            "ref": "§ 5",
            "orig": "",
            "traducao": "",
            "paginas": "",
        },
        {
            "ref": "§ 7",
            "orig": "",
            "traducao": "",
            "paginas": "",
        },
        {
            "ref": "§ 10",
            "orig": "",
            "traducao": "",
            "paginas": "",
        },
    ],
    "Francisco2015LS": [
        {
            "ref": "§ 102-114",
            "orig": "",
            "traducao": "",
            "paginas": "",
        },
    ],
    "JoaoPauloII1991CA": [
        {
            "ref": "§ 33-42",
            "orig": "",
            "traducao": "",
            "paginas": "",
        },
    ],
    "JoaoXXIII1963PT": [
        {
            "ref": "§ 9-27",
            "orig": "",
            "traducao": "",
            "paginas": "",
        },
    ],
    "Bioni2021PPD": [
        {
            "ref": "Cap. 2",
            "orig": "",
            "traducao": "",
            "paginas": "",
        },
    ],
    "Doneda2006PDD": [
        {
            "ref": "Cap. 3",
            "orig": "",
            "traducao": "",
            "paginas": "",
        },
    ],
    "Rodota2008PDA": [
        {
            "ref": "Cap. 1",
            "orig": "",
            "traducao": "",
            "paginas": "",
        },
    ],
    "Castells2010EI": [
        {
            "ref": "Vol. 1, Cap. 1",
            "orig": "",
            "traducao": "",
            "paginas": "",
        },
    ],
    "Zuboff2019SC": [
        {
            "ref": "Parte I",
            "orig": "",
            "traducao": "",
            "paginas": "",
        },
    ],
    "Floridi2018AIP": [
        {
            "ref": "Seção 2",
            "orig": "",
            "traducao": "",
            "paginas": "pp. 5-12",
        },
    ],
    "Calo2017AIL": [
        {
            "ref": "Seção III",
            "orig": "",
            "traducao": "",
            "paginas": "pp. 420-428",
        },
    ],
    "Brasil1988CF": [
        {
            "ref": "Art. 1º, III",
            "orig": "",
            "traducao": "",
            "paginas": "",
        },
        {
            "ref": "Art. 5º",
            "orig": "",
            "traducao": "",
            "paginas": "",
        },
    ],
    "Brasil2018LGPD": [
        {
            "ref": "Arts. 1º-6º",
            "orig": "",
            "traducao": "",
            "paginas": "",
        },
        {
            "ref": "Arts. 7º-11",
            "orig": "",
            "traducao": "",
            "paginas": "",
        },
    ],
    "Brasil2023PL2338": [
        {
            "ref": "Arts. 1º-5º",
            "orig": "",
            "traducao": "",
            "paginas": "",
        },
    ],
}


# ============================================================
# FUNCOES AUXILIARES
# ============================================================

def get_reference(cite_key):
    """Retorna dados completos da referencia ou None se nao encontrar."""
    return REFERENCES.get(cite_key)


def format_citation(cite_key):
    """
    Retorna citacao formatada para um dado cite_key.
    Exemplo: "LEÃO XIV. Magnifica Humanitas... Libreria Editrice Vaticana, 2026."
    """
    ref = REFERENCES.get(cite_key)
    if not ref:
        return f"[{cite_key}]"

    author = ref["author"]
    title = ref["title"]
    year = ref["year"]
    publisher = ref["publisher"]

    # Formatar por tipo
    t = ref.get("type", "")
    if t == "magisterio":
        return f"{author.upper()}. {title}. {publisher}, {year}."
    elif t == "legislacao":
        return f"{author.upper()}. {title}. {publisher}, {year}."
    elif t == "artigo":
        return f"{author}. \\\"{title}\\\". {publisher}, {year}."
    else:  # livro
        return f"{author}. {title}. {publisher}, {year}."


def get_passages(cite_key):
    """Retorna lista de passagens enriquecidas para um cite_key."""
    return PASSAGES.get(cite_key, [])
