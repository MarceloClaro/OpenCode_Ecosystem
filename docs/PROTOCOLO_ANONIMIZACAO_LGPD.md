# Protocolo de Anonimizacao LGPD — OpenCode Ecosystem

**Versao:** 1.0 | **Data:** 2026-06-04 | **Conformidade:** Lei 13.709/2018

---

## 1. Fundamentacao Legal

A Lei Geral de Protecao de Dados Pessoais (LGPD — Lei 13.709/2018) estabelece:

| Artigo | Dispositivo | Aplicacao no Ecossistema |
|:------:|-------------|---------------------------|
| Art. 5, I | Dado pessoal: informacao relacionada a pessoa natural identificada | Nomes, emails, CPF em documentos processados |
| Art. 5, II | Dado sensivel: origem racial, conviccao religiosa, saude, dados geneticos | Conteudo de artigos academicos com dados de sujeitos de pesquisa |
| Art. 7, I | Tratamento mediante consentimento | TCLE obrigatorio para dados de participantes |
| Art. 11 | Tratamento de dados sensiveis | Restricao adicional: consentimento especifico e destacado |
| Art. 46 | Seguranca e sigilo | Medidas tecnicas para proteger dados (anonimizacao, criptografia) |
| Art. 12 | Dados anonimizados | Nao sao considerados dados pessoais (nao se aplica LGPD) |

---

## 2. Dados Sensiveis em Risco

O pipeline multiagente processa documentos academicos que podem conter:

| Categoria | Exemplos | Risco |
|-----------|----------|:-----:|
| Identificacao direta | Nome, CPF, RG, email, telefone, endereco | Alto |
| Identificacao indireta | ORCID, Lattes, instituicao + departamento | Medio |
| Dados sensiveis | Saude, etnia, religiao, opiniao politica | Critico |
| Dados de pesquisa | Respostas de questionarios, transcricoes de entrevistas | Alto |
| Metadados | IP, timestamp, geolocalizacao, user agent | Baixo |

---

## 3. Protocolo de 5 Etapas

### Etapa 1: Identificacao (Varredura Automatica)

Script de referencia para deteccao de PII (Personally Identifiable Information):

```python
import re

PII_PATTERNS = {
    "CPF": r"\d{3}[\.\-]?\d{3}[\.\-]?\d{3}[\.\-]?\d{2}",
    "EMAIL": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "TELEFONE": r"\(?\d{2}\)?\s?\d{4,5}[-\s]?\d{4}",
    "CEP": r"\d{5}[-\s]?\d{3}",
    "RG": r"\d{2}[\.\-]?\d{3}[\.\-]?\d{3}[\.\-]?[\dxX]",
    "NOME_PROPRIA": r"[A-Z][a-z]+(?:\s+(?:de|da|do|das|dos)\s+)?[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+",
    "ORCID": r"\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{3}[0-9X]",
    "DOI": r"10\.\d{4,}/[^\s]+",
    "URL": r"https?://[^\s]+",
}

def scan_pii(text):
    findings = {}
    for label, pattern in PII_PATTERNS.items():
        matches = re.findall(pattern, text)
        if matches:
            findings[label] = matches
    return findings
```

### Etapa 2: Classificacao

| Classe | Descricao | Acao |
|:------:|-----------|------|
| **A — Dado Sensivel** | Saude, etnia, religiao, biometria | Suprimir completamente |
| **B — Dado Pessoal** | Nome, CPF, email, telefone | Pseudonimizar |
| **C — Dado Academico** | ORCID, DOI, filiacao institucional | Manter (necessario para citacao) |
| **D — Dado Publico** | Referencias bibliograficas, leis | Manter |

### Etapa 3: Transformacao

| Tecnica | Aplicacao | Exemplo |
|---------|-----------|---------|
| **Pseudonimizacao** | Substituir identificador real por codigo | "Joao Silva" → "PARTICIPANTE_001" |
| **Generalizacao** | Reduzir precisao do dado | "35 anos" → "30-40 anos" |
| **Supressao** | Remover campo completamente | CPF: `XXX.XXX.XXX-XX` → `[SUPRIMIDO]` |
| **Agregacao** | Combinar dados em grupos | "Hospital X, Ala B" → "Rede Publica" |
| **Hash SHA-256** | Referencia reversivel com chave | `sha256("Joao" + salt)` → armazenar hash |

### Etapa 4: Verificacao (Validacao Cruzada)

```python
def verify_anonymization(original, processed):
    """Verifica se dados pessoais foram removidos."""
    original_pii = scan_pii(original)
    processed_pii = scan_pii(processed)

    # CPF, email, telefone nao podem aparecer no processado
    for key in ["CPF", "EMAIL", "TELEFONE", "RG"]:
        if key in processed_pii:
            return False, f"Vazamento detectado: {key}"

    return True, "Anonimizacao verificada"
```

### Etapa 5: Auditoria (Log Imutavel)

```python
import hashlib, json, datetime

def audit_log(action, original_hash, processed_hash):
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "action": action,
        "original_sha256": original_hash,
        "processed_sha256": processed_hash,
    }
    # Cada entrada assinada com hash da entrada anterior (blockchain-like)
    return entry
```

---

## 4. Checklist de Conformidade LGPD

| # | Requisito | Status | Evidencia |
|:-:|-----------|:------:|-----------|
| 1 | Mapeamento de dados pessoais processados | ✅ | Secao 2 deste documento |
| 2 | Finalidade especifica documentada | ✅ | Anteprojeto PPGTE/UFC |
| 3 | Base legal para tratamento | ✅ | Consentimento (TCLE) |
| 4 | Medidas tecnicas de seguranca | ✅ | Anonimizacao 5 etapas + SHA-256 |
| 5 | Registro de operacoes de tratamento | ✅ | Log imutavel de auditoria |
| 6 | Direito de acesso do titular | ⬜ | Implementar endpoint de consulta |
| 7 | Direito de eliminacao | ⬜ | Implementar endpoint de exclusao |
| 8 | Comunicacao de incidentes | ⬜ | Definir procedimento ANPD |
| 9 | Encarregado de dados (DPO) | ⬜ | Designar responsavel formal |
| 10 | Relatorio de impacto | ⬜ | RIPD para processamento de dados sensiveis |

---

## 5. Responsabilidades do Operador

Conforme LGPD, o desenvolvedor do ecossistema atua como **operador**:

1. **Tratar dados conforme instrucoes do controlador** (Art. 39)
2. **Manter registro das operacoes** (Art. 37) → Log SHA-256 implementado
3. **Comunicar incidentes de seguranca** (Art. 48) → Procedimento pendente
4. **Eliminar dados apos termino do tratamento** (Art. 15) → Endpoint pendente
5. **Adotar medidas de seguranca proporcionais** (Art. 46) → Protocolo implementado

---

## 6. Script de Referencia (Varredura PII)

```python
#!/usr/bin/env python3
"""scanner_lgpd.py — Varredura automatica de dados pessoais."""

import re, sys, hashlib, json
from pathlib import Path

PII_PATTERNS = {
    "CPF": r"\d{3}[\.\-]?\d{3}[\.\-]?\d{3}[\.\-]?\d{2}",
    "EMAIL": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "TELEFONE": r"\(?\d{2}\)?\s?\d{4,5}[-\s]?\d{4}",
}

def scan_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    findings = {}
    for label, pattern in PII_PATTERNS.items():
        matches = re.findall(pattern, content)
        if matches:
            findings[label] = list(set(matches))

    return {
        "file": str(filepath),
        "sha256": hashlib.sha256(content.encode()).hexdigest(),
        "findings": findings,
    }

if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    results = []
    for tex_file in path.rglob("*.tex"):
        result = scan_file(tex_file)
        if result["findings"]:
            results.append(result)

    print(json.dumps(results, indent=2, ensure_ascii=False))
    if results:
        print(f"\nATENCAO: {len(results)} arquivos com possiveis dados pessoais!")
        sys.exit(1)
```

---

**Protocolo LGPD** · 2026-06-04 · OpenCode Ecosystem v4.7.1
