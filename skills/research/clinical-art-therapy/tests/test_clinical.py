import pytest
import sys
import os
import hashlib
from dataclasses import dataclass, field, asdict
from typing import List, Optional

SKILL_DIR = os.path.join(os.path.dirname(__file__), '..')


@dataclass
class ProtocoloEtico:
    cep: str = ""
    tcle: str = ""
    status: str = "rascunho"

    def validar_tcle(self, texto: str) -> bool:
        return len(texto) >= 100

    def hash_consentimento(self, texto: str) -> str:
        return hashlib.md5(texto.encode()).hexdigest()


@dataclass
class Participante:
    id: str
    idade: int
    tempo_grupo_meses: int
    diagnostico_familiar: str

    def elegivel(self) -> bool:
        return (
            self.idade >= 18
            and self.tempo_grupo_meses >= 3
            and self.diagnostico_familiar in ("TEA", "TDAH", "ALTAS_HABILIDADES")
        )


@dataclass
class PipelineStage:
    nome: str
    concluido: bool = False
    artefatos: List[str] = field(default_factory=list)

    def validar(self) -> bool:
        return len(self.artefatos) > 0


class TestClinicalArtTherapy:

    def test_participante_elegibilidade(self):
        p = Participante("P01", idade=35, tempo_grupo_meses=6,
                         diagnostico_familiar="TEA")
        assert p.elegivel() is True

        p2 = Participante("P02", idade=16, tempo_grupo_meses=6,
                          diagnostico_familiar="TEA")
        assert p2.elegivel() is False

        p3 = Participante("P03", idade=40, tempo_grupo_meses=1,
                          diagnostico_familiar="TDAH")
        assert p3.elegivel() is False

    def test_hash_consentimento_deterministico(self):
        proto = ProtocoloEtico()
        h1 = proto.hash_consentimento("consentimento do participante P01")
        h2 = proto.hash_consentimento("consentimento do participante P01")
        assert h1 == h2
        assert len(h1) == 32

    def test_tcle_tamanho_minimo(self):
        proto = ProtocoloEtico()
        curto = "Eu aceito."
        assert proto.validar_tcle(curto) is False

        longo = (
            "Termo de Consentimento Livre e Esclarecido. "
            + "Prezado(a) participante, voce esta sendo convidado(a) "
            + "a participar de uma pesquisa sobre arteterapia decolonial... "
            + "Esta pesquisa segue a Resolucao CNS 466/2012..."
        )
        assert proto.validar_tcle(longo) is True

    def test_pipeline_stage_validacao(self):
        stage = PipelineStage(
            nome="Estagio 1: Intake e Protocolo Etico",
            artefatos=["TCLE_anonimizado.pdf", "CEP_submissao.pdf"]
        )
        assert stage.validar() is True
        stage_sem = PipelineStage(nome="Estagio 2: Codificacao")
        assert stage_sem.validar() is False

    def test_skill_md_existe(self):
        skill_path = os.path.join(SKILL_DIR, 'SKILL.md')
        assert os.path.exists(skill_path)
        with open(skill_path, encoding="utf-8") as f:
            content = f.read()
        assert "clinical-art-therapy" in content.lower()
        assert "pipeline" in content.lower()
        assert "CEP" in content or "etico" in content.lower()
