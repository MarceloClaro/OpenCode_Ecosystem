"""
SPEC-014 — Pipeline de Conformidade LGPD para Ecossistema OpenCode

Camadas (L0-L5):
  L0: agent-forum (multiagente + mascaramento)         [3 CTs]
  L1: lgpd-crypto (pseudonimizacao, AES, k-anonymity)  [3 CTs]
  L2: lgpd-dpo (consentimento, auditoria)               [3 CTs]
  L3: lgpd-integration (bridge unificada)               [3 CTs]
  L4: lgpd-pipeline (pipeline completo)                [3 CTs]
  Total: 15 CTs

Uso:
  python SPEC-014_lgpd_pipeline.py          # Executa pipeline completo
  python SPEC-014_lgpd_pipeline.py --score  # Executa e exibe score
"""

import sys, os, json, time
from datetime import datetime

BASE = r'C:\Users\marce\OneDrive\Documentos\Antiprojeto UFC\fase2_implementacao'

for d in ['lgpd-crypto', 'lgpd-dpo', 'lgpd-integration']:
    sys.path.insert(0, os.path.join(BASE, d))

# ─── Imports ──────────────────────────────────────────────────────────
from lgpd_crypto import (
    pseudonymize, encrypt_aes256gcm, decrypt_aes256gcm,
    mask_data, classify_sensitivity,
    anonymize_k_anonymity, anonymize_l_diversity, verify_anonymization,
    encrypt_file, decrypt_file,
)
from consent_manager import ConsentManager
from audit_logger import AuditLogger
from dpo_agent import DPOAgent, DataProcessingActivity
from lgpd_bridge import LGPDPipeline, ProcessingRequest

# ─── Executor de CTs ──────────────────────────────────────────────────
results: list[dict] = []

def ct(id: str, label: str, camada: str, fn) -> dict:
    """Executa um caso de teste e registra resultado."""
    t0 = time.time()
    try:
        fn()
        status = "PASS"
    except AssertionError as e:
        status = "FAIL"
    except Exception as e:
        status = f"ERROR: {e}"
    dt = round((time.time() - t0) * 1000, 1)
    r = {"id": id, "label": label, "camada": camada, "status": status, "ms": dt}
    results.append(r)
    print(f"  [{status}] {id} ({dt}ms) — {label}")
    return r

# ─── L0: agent-forum ──────────────────────────────────────────────────
def run_l0():
    print("\n=== L0: agent-forum (Multiagente + Mascaramento) ===")

    def ct001():
        # Dado sensivel mascarado por padrao
        masked = mask_data("joao.silva@email.com")
        assert "***@" in masked or "***" in masked

    def ct002():
        # CPF classificado como CRITICO
        cls = classify_sensitivity("cpf", "12345678901")
        assert cls["sensitivity_level"] == 5
        assert cls["label"] == "CRITICO (art. 5\u00ba LGPD - dado sensivel)"

    def ct003():
        # Consentimento multiagente: registrar e verificar
        cm = ConsentManager()
        cm.grant("agente-001", "debate", ["texto"])
        assert cm.check("agente-001", "debate") == True
        assert cm.check("agente-001", "outro") == False

    ct("CT001", "Mascaramento de dado sensivel", "L0", ct001)
    ct("CT002", "Classificacao de sensibilidade", "L0", ct002)
    ct("CT003", "Consentimento multiagente", "L0", ct003)

# ─── L1: lgpd-crypto ──────────────────────────────────────────────────
def run_l1():
    print("\n=== L1: lgpd-crypto (Criptografia e Anonimizacao) ===")

    def ct004():
        pid = pseudonymize("Maria Souza", salt="spec014")
        assert pid.startswith("P-")

    def ct005():
        bundle = encrypt_aes256gcm("dado sensivel")
        plain = decrypt_aes256gcm(bundle)
        assert plain == "dado sensivel"

    def ct006():
        records = [
            {'idade': 30, 'cep': '60000', 'diagnostico': 'A'},
            {'idade': 30, 'cep': '60000', 'diagnostico': 'B'},
            {'idade': 31, 'cep': '60001', 'diagnostico': 'A'},
            {'idade': 31, 'cep': '60001', 'diagnostico': 'B'},
        ]
        anon, _ = anonymize_k_anonymity(records, ['idade', 'cep'], k=2)
        v = verify_anonymization(anon, ['idade', 'cep'], k=2)
        assert v['pass']

    ct("CT004", "Pseudonimizacao SHA-256 + salt", "L1", ct004)
    ct("CT005", "Criptografia AES-256-GCM", "L1", ct005)
    ct("CT006", "k-anonymity (k=2) + verificacao", "L1", ct006)

# ─── L2: lgpd-dpo ─────────────────────────────────────────────────────
def run_l2():
    print("\n=== L2: lgpd-dpo (Consentimento e Auditoria) ===")

    def ct007():
        cm = ConsentManager()
        cm.grant("titular-001", "pesquisa", ["nome", "email"])
        assert cm.check("titular-001", "pesquisa") == True
        cm.revoke("titular-001", "pesquisa")
        assert cm.check("titular-001", "pesquisa") == False

    def ct008():
        al = AuditLogger()
        al.log("process", "titular-001", "sensitive", "pesquisa", "agente-x")
        al.log("delete", "titular-001", "personal", "pesquisa", "agente-x")
        assert al.report()["total_operations"] == 2

    def ct009():
        dpo = DPOAgent()
        dpo.consent.grant("titular-002", "pesquisa", ["*"])
        result = dpo.process_personal_data("titular-002", "sensitive", "pesquisa", "cora")
        assert result == True
        result2 = dpo.process_personal_data("titular-003", "sensitive", "pesquisa", "cora")
        assert result2 == False

    ct("CT007", "Ciclo de consentimento (grant/check/revoke)", "L2", ct007)
    ct("CT008", "Registro de auditoria", "L2", ct008)
    ct("CT009", "Pipeline DPO com e sem consentimento", "L2", ct009)

# ─── L3: lgpd-integration ─────────────────────────────────────────────
def run_l3():
    print("\n=== L3: lgpd-integration (Bridge Unificada) ===")

    def ct010():
        pipe = LGPDPipeline(salt="spec014")
        pipe.dpo.consent.grant("sujeito-010", "pesquisa", ["*"])
        req = ProcessingRequest(
            subject_id="sujeito-010", purpose="pesquisa",
            data="dado sensivel", data_type="sensitive",
            agent="test", target_level="pseudonymized",
        )
        res = pipe.process(req)
        assert res.status == "granted"

    def ct011():
        pipe = LGPDPipeline(salt="spec014")
        pipe.dpo.consent.grant("sujeito-011", "pesquisa", ["*"])
        records = [
            {'nome': 'A', 'idade': 30, 'cep': '60', 'diagnostico': 'X'},
            {'nome': 'B', 'idade': 30, 'cep': '60', 'diagnostico': 'Y'},
            {'nome': 'C', 'idade': 31, 'cep': '61', 'diagnostico': 'X'},
        ]
        result = pipe.anonymize_dataset(records, ['idade', 'cep'], 'diagnostico')
        assert result['verified']['pass'] == True

    def ct012():
        pipe = LGPDPipeline()
        report = pipe.compliance_report()
        assert "total_consents" in report
        assert "total_audit_entries" in report
        assert "total_activities" in report

    ct("CT010", "Pipeline bridge com consentimento", "L3", ct010)
    ct("CT011", "Anonimizacao integrada de dataset", "L3", ct011)
    ct("CT012", "Relatorio de compliance consolidado", "L3", ct012)

# ─── L4: lgpd-pipeline (Pipeline End-to-End) ──────────────────────────
def run_l4():
    print("\n=== L4: lgpd-pipeline (Cenario Real Unificado) ===")

    def ct013():
        """Cenario completo: coleta com consentimento → pseudo → auditoria."""
        pipe = LGPDPipeline(salt="spec014-e2e")

        pipe.register_skill_activity(
            skill_name="cora-debate",
            purpose="Debate multiagente com dados pessoais",
            data_categories=["nome", "email", "texto"],
            legal_basis="consentimento explicito (Art. 7\u00ba, I)",
        )

        pipe.dpo.consent.grant(
            "pesquisador-01", "debate-academico",
            ["nome", "email", "texto"],
            evidence="termo_v1.pdf"
        )

        req = ProcessingRequest(
            subject_id="pesquisador-01",
            purpose="debate-academico",
            data="O pensamento computacional de Joao Silva",
            data_type="personal",
            agent="cora-debate",
            target_level="pseudonymized",
        )
        res = pipe.process(req)
        assert res.status == "granted"
        assert res.consent_valid == True

    def ct014():
        """Cenario sem consentimento: fluxo negado com auditoria."""
        pipe = LGPDPipeline(salt="spec014-e2e")
        req = ProcessingRequest(
            subject_id="pesquisador-02",
            purpose="analise-comportamental",
            data="historico de navegacao",
            data_type="sensitive",
            agent="agent-forum",
            target_level="encrypted",
        )
        res = pipe.process(req)
        assert res.status == "denied"

        entries = pipe.dpo.audit.query(subject_id="pesquisador-02")
        assert any("denied" in e.operation or e.operation == "denied" for e in entries)

    def ct015():
        """Cenario de anonimizacao: k=3, l=2, verificado."""
        pipe = LGPDPipeline(salt="spec014-e2e")
        pipe.dpo.consent.grant("anon-01", "publicacao", ["*"])
        records = [
            {'nome': 'A', 'idade': 30, 'cep': '60000', 'diagnostico': 'D1'},
            {'nome': 'B', 'idade': 30, 'cep': '60000', 'diagnostico': 'D2'},
            {'nome': 'C', 'idade': 30, 'cep': '60000', 'diagnostico': 'D3'},
            {'nome': 'D', 'idade': 31, 'cep': '60001', 'diagnostico': 'D1'},
            {'nome': 'E', 'idade': 31, 'cep': '60001', 'diagnostico': 'D2'},
            {'nome': 'F', 'idade': 31, 'cep': '60001', 'diagnostico': 'D3'},
        ]
        result = pipe.anonymize_dataset(records, ['idade', 'cep'], 'diagnostico', k=3)
        assert result['verified']['pass'] == True
        assert result['k_anonymity']['records_before'] == 6

    ct("CT013", "Cenario real: coleta → consentimento → pseudo → auditoria", "L4", ct013)
    ct("CT014", "Cenario real: negacao sem consentimento + auditoria", "L4", ct014)
    ct("CT015", "Cenario real: anonimizacao k=3 + l-diversity", "L4", ct015)

# ─── AUTO SCORE ────────────────────────────────────────────────────────
def auto_score() -> dict:
    """Calcula score baseado nos resultados dos CTs."""
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] != "PASS")
    rate = round(passed / total * 100, 1) if total > 0 else 0.0

    # Pontuacao Qualis: cada camada vale ate 20 pontos
    layers = {"L0": 0, "L1": 0, "L2": 0, "L3": 0, "L4": 0}
    layer_cts = {k: 0 for k in layers}
    layer_pass = {k: 0 for k in layers}
    for r in results:
        layer_cts[r["camada"]] = layer_cts.get(r["camada"], 0) + 1
        if r["status"] == "PASS":
            layer_pass[r["camada"]] = layer_pass.get(r["camada"], 0) + 1

    for layer in layers:
        total_cts = layer_cts[layer]
        passed_cts = layer_pass[layer]
        if total_cts > 0:
            layers[layer] = round(passed_cts / total_cts * 20, 1)

    total_score = round(sum(layers.values()), 1)

    return {
        "total_cts": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": rate,
        "layers": layers,
        "total_score": total_score,
        "max_score": 100,
        "qualis_equivalent": "A1" if total_score >= 90 else "A2" if total_score >= 80 else "B1" if total_score >= 70 else "B2",
    }

# ─── Main ──────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("SPEC-014 — Pipeline de Conformidade LGPD")
    print("Ecossistema OpenCode | UFC/PPGTE")
    print("=" * 60)

    run_l0()
    run_l1()
    run_l2()
    run_l3()
    run_l4()

    score = auto_score()

    print("\n" + "=" * 60)
    print("RESULTADOS")
    print("=" * 60)
    for r in results:
        icon = "\u2713" if r["status"] == "PASS" else "\u2717"
        print(f"  {icon} {r['id']} ({r['camada']}) — {r['label']}: {r['status']} ({r['ms']}ms)")

    print("\n" + "=" * 60)
    print("AUTO SCORE")
    print("=" * 60)
    print(f"  CTs:    {score['passed']}/{score['total_cts']} ({score['pass_rate']}%)")
    for layer, pts in score['layers'].items():
        print(f"  {layer}:   {pts}/20")
    print(f"  Total:  {score['total_score']}/100")
    print(f"  Qualis: {score['qualis_equivalent']}")

    # Salva resultado
    result_path = os.path.join(BASE, 'lgpd-pipeline', 'SPEC-014_result.json')
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump({
            "spec": "SPEC-014",
            "timestamp": datetime.utcnow().isoformat(),
            "score": score,
            "results": results,
        }, f, ensure_ascii=False, indent=2)
    print(f"\n  Resultado salvo em: {result_path}")

    return 0 if score['failed'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
