#!/usr/bin/env python3
"""Seed script: popula o banco com dados de editais a partir de fixtures HTML.

Simula o pipeline completo: crawl → dedup → extract → analyze.
Útil para desenvolvimento e demonstração sem depender de sites externos.
"""

import sys
from pathlib import Path

# Adiciona o diretório do projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

from api.database import SessionLocal, engine, Base
from api.models.portal import Portal
from api.models.edital import Edital
from worker.connectors.prosas import ProsasConnector
from pipeline.deduplicator import deduplicate

# Garante tabelas
Base.metadata.create_all(bind=engine)


def seed_portais():
    """Cadastra os portais no banco."""
    db = SessionLocal()
    portais_data = [
        ("prosas", "https://prosas.com.br/editais", "http"),
        ("finep", "https://www.finep.gov.br/chamadas-publicas", "http"),
        ("fapeg", "https://fapeg.go.gov.br/editais", "http"),
        ("sebrae", "https://www.sebrae.com.br/editais", "http"),
        ("cnpq", "https://www.gov.br/cnpq", "http"),
    ]
    for nome, url, mode in portais_data:
        exists = db.query(Portal).filter(Portal.nome == nome).first()
        if not exists:
            db.add(Portal(nome=nome, base_url=url, mode=mode))
    db.commit()
    print(f"✅ Portais cadastrados")


def seed_editais_from_fixture():
    """Extrai editais do HTML fixture e salva no banco."""
    db = SessionLocal()
    portal = db.query(Portal).filter(Portal.nome == "prosas").first()
    if not portal:
        print("❌ Portal 'prosas' não encontrado")
        return

    fixture_path = Path(__file__).parent.parent / "tests" / "fixtures" / "prosas_editais.html"
    if not fixture_path.exists():
        print(f"❌ Fixture não encontrado: {fixture_path}")
        return

    html = fixture_path.read_text()
    connector = ProsasConnector()
    raw_editais = connector.parse(html)
    print(f"📄 {len(raw_editais)} editais extraídos do HTML")

    # Converte e deduplica
    raw_dicts = [
        {
            "titulo": e.titulo,
            "url_original": e.url,
            "pdf_url": e.pdf_url,
            "data_publicacao": e.data_publicacao,
            "portal_id": str(portal.id),
        }
        for e in raw_editais
    ]
    unique = deduplicate(raw_dicts)
    print(f"🔄 Após deduplicação: {len(unique)} únicos (removidos {len(raw_dicts) - len(unique)})")

    novos = 0
    for data in unique:
        exists = db.query(Edital).filter(Edital.url_original == data["url_original"]).first()
        if not exists:
            edital = Edital(
                portal_id=portal.id,
                titulo=data["titulo"],
                url_original=data["url_original"],
                pdf_url=data.get("pdf_url"),
                status="extraido",
                raw_text=f"Conteúdo simulado do edital: {data['titulo']}.\n\n"
                         f"Este é um texto de exemplo representando o conteúdo extraído "
                         f"de um edital real do portal Prosas.",
                financiador="Prosas/Fundo Social",
                valor_min=50000.0,
                valor_max=200000.0,
                moeda="BRL",
                eixos_tematicos=["tecnologia", "inovacao"],
                perfil_elegivel=["startup_early_stage", "ict"],
                mecanismo_financiamento="subvencao_economica",
                status_inscricao="inscricoes_abertas",
                nivel_trl_min=3,
                nivel_trl_max=7,
                score_complexidade=3,
                resumo=f"Edital de fomento: {data['titulo']}",
            )
            db.add(edital)
            novos += 1

    db.commit()
    print(f"✅ {novos} novos editais salvos no banco")
    db.close()


if __name__ == "__main__":
    seed_portais()
    seed_editais_from_fixture()
    print("\n🚀 Seed concluído! Acesse http://localhost para ver os dados.")
