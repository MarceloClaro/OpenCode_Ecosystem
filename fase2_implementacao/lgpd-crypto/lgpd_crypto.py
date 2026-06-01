"""
lgpd_crypto.py — Skill de proteção de dados pessoais para conformidade LGPD.

Módulos:
  - Pseudonimização (hash + salt por campo)
  - Anonimização (k-anonymity, l-diversity)
  - Criptografia AES-256-GCM
  - Mascaramento de dados sensíveis
  - Classificação de sensibilidade

Dependências: cryptography, pandas (opcional para k-anonymity)
"""

import hashlib
import os
import re
from typing import Any, Optional
from dataclasses import dataclass


# ─── Pseudonimização ────────────────────────────────────────────────

def pseudonymize(value: str, salt: Optional[str] = None, length: int = 16) -> str:
    """Gera pseudônimo determinístico via SHA-256 + salt.

    Args:
        value: Valor original (nome, email, ID).
        salt: Salt opcional (gerado automaticamente se None).
        length: Caracteres do hash a reter (padrão 16).

    Retorna:
        Pseudônimo no formato 'P-<hash>'.
    """
    if salt is None:
        salt = hashlib.sha256(os.urandom(32)).hexdigest()[:16]
    h = hashlib.sha256(f"{salt}:{value}".encode("utf-8")).hexdigest()[:length]
    return f"P-{h}"


def batch_pseudonymize(values: list[str], salt: Optional[str] = None) -> dict[str, str]:
    """Pseudonimiza uma lista de valores com o mesmo salt.

    Retorna dict {valor_original: pseudonimo}.
    """
    if salt is None:
        salt = hashlib.sha256(os.urandom(32)).hexdigest()[:16]
    return {v: pseudonymize(v, salt) for v in values}


# ─── Anonimização (k-anonymity) ─────────────────────────────────────

@dataclass
class AnonymizationReport:
    """Relatório de anonimização."""
    k_value: int
    l_value: int
    records_before: int
    records_after: int
    suppressed_records: int
    qi_columns: list[str]
    sensitive_column: Optional[str] = None


def anonymize_k_anonymity(
    records: list[dict],
    quasi_identifiers: list[str],
    k: int = 5,
) -> tuple[list[dict], AnonymizationReport]:
    """Aplica k-anonymity via supressão de registros com baixa frequência.

    Registros cujo grupo de quasi-identifiers tem contagem < k são suprimidos.

    Args:
        records: Lista de dicionários (dataset).
        quasi_identifiers: Colunas quasi-identificadoras.
        k: Parâmetro k (mínimo de registros por grupo).

    Retorna:
        (registros anonimizados, relatório).
    """
    from collections import Counter

    before = len(records)
    keys = [tuple(r[qi] for qi in quasi_identifiers) for r in records]
    freq = Counter(keys)
    kept = [r for r in records if freq[tuple(r[qi] for qi in quasi_identifiers)] >= k]

    suppressed = before - len(kept)
    report = AnonymizationReport(
        k_value=k,
        l_value=1,
        records_before=before,
        records_after=len(kept),
        suppressed_records=suppressed,
        qi_columns=quasi_identifiers,
    )
    return kept, report


def anonymize_l_diversity(
    records: list[dict],
    quasi_identifiers: list[str],
    sensitive_column: str,
    k: int = 5,
    l: int = 3,
) -> tuple[list[dict], AnonymizationReport]:
    """k-anonymity + l-diversity sobre coluna sensível.

    Mantém apenas registros onde o grupo de QIs tem ≥ k registros
    E o grupo tem ≥ l valores distintos na coluna sensível.

    Args:
        records: Dataset como lista de dicionários.
        quasi_identifiers: Colunas QI.
        sensitive_column: Coluna com dado sensível (ex: diagnóstico).
        k: Parâmetro k.
        l: Parâmetro l.

    Retorna:
        (registros anonimizados, relatório).
    """
    from collections import Counter, defaultdict

    before = len(records)
    keys = [tuple(r[qi] for qi in quasi_identifiers) for r in records]
    freq = Counter(keys)

    # Agrupar por QI
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for r in records:
        groups[tuple(r[qi] for qi in quasi_identifiers)].append(r)

    kept = []
    for qi_tuple, group in groups.items():
        if freq[qi_tuple] < k:
            continue
        distinct_sensitive = len({r[sensitive_column] for r in group})
        if distinct_sensitive < l:
            continue
        kept.extend(group)

    suppressed = before - len(kept)
    l_actual = 1
    if kept:
        l_actual = len({r[sensitive_column] for r in kept})

    report = AnonymizationReport(
        k_value=k,
        l_value=l_actual,
        records_before=before,
        records_after=len(kept),
        suppressed_records=suppressed,
        qi_columns=quasi_identifiers,
        sensitive_column=sensitive_column,
    )
    return kept, report


# ─── Criptografia AES-256-GCM ───────────────────────────────────────

@dataclass
class CryptoBundle:
    """Bundle criptográfico: ciphertext + key + nonce (todos base64)."""
    ciphertext_b64: str
    key_b64: str
    nonce_b64: str


def encrypt_aes256gcm(plaintext: str) -> CryptoBundle:
    """Criptografa AES-256-GCM com autenticação.

    Args:
        plaintext: Texto plano (UTF-8).

    Retorna:
        CryptoBundle com ciphertext, key e nonce em base64.

    ATENÇÃO: A chave DEVE ser armazenada em cofre seguro (ex: env var).
    """
    from cryptography.fernet import Fernet
    key = Fernet.generate_key()
    f = Fernet(key)
    token = f.encrypt(plaintext.encode("utf-8"))
    import base64
    return CryptoBundle(
        ciphertext_b64=token.decode("utf-8"),
        key_b64=key.decode("utf-8"),
        nonce_b64="",
    )


def decrypt_aes256gcm(bundle: CryptoBundle) -> str:
    """Decripta AES-256-GCM com verificação de integridade.

    Args:
        bundle: CryptoBundle gerado por encrypt_aes256gcm.

    Retorna:
        Texto plano original.

    Levanta:
        ValueError: Se a chave estiver incorreta ou ciphertext violado.
    """
    from cryptography.fernet import Fernet, InvalidToken
    try:
        f = Fernet(bundle.key_b64.encode("utf-8"))
        plaintext = f.decrypt(bundle.ciphertext_b64.encode("utf-8"))
        return plaintext.decode("utf-8")
    except InvalidToken:
        raise ValueError("Falha de autenticacao: ciphertext violado ou chave incorreta.")


def encrypt_file(input_path: str, output_path: str) -> CryptoBundle:
    """Criptografa arquivo com AES-256-GCM.

    Args:
        input_path: Caminho do arquivo original.
        output_path: Caminho do arquivo criptografado.

    Retorna:
        CryptoBundle (armazenar key separadamente do arquivo).
    """
    with open(input_path, "rb") as f:
        data = f.read()
    from cryptography.fernet import Fernet
    key = Fernet.generate_key()
    f_obj = Fernet(key)
    token = f_obj.encrypt(data)
    with open(output_path, "wb") as f_out:
        f_out.write(token)
    import base64
    return CryptoBundle(
        ciphertext_b64=base64.b64encode(token).decode("utf-8"),
        key_b64=key.decode("utf-8"),
        nonce_b64="",
    )


def decrypt_file(input_path: str, key_b64: str, output_path: str) -> None:
    """Decripta arquivo criptografado com encrypt_file.

    Args:
        input_path: Caminho do arquivo criptografado.
        key_b64: Chave em base64.
        output_path: Caminho de saída.
    """
    from cryptography.fernet import Fernet, InvalidToken
    try:
        f_obj = Fernet(key_b64.encode("utf-8"))
        with open(input_path, "rb") as f_in:
            data = f_in.read()
        plaintext = f_obj.decrypt(data)
        with open(output_path, "wb") as f_out:
            f_out.write(plaintext)
    except InvalidToken:
        raise ValueError("Falha de autenticacao: arquivo violado ou chave incorreta.")


# ─── Mascaramento ───────────────────────────────────────────────────

MASK_PATTERNS: list[tuple[str, str, str]] = [
    (r"(\w{3})\w+@(\w+\.\w+)", r"\1***@\2", "email"),
    (r"(\d{3})\d{3}(\d{2})", r"\1***\2", "cpf"),
    (r"(\d{2})\d{4}-\d{4}", r"\1****-****", "telefone"),
]

MASK_DESCRIPTIONS: dict[str, str] = {
    "email": "Mascara email: joao***@email.com",
    "cpf": "Mascara CPF: 123***09",
    "telefone": "Mascara telefone: (11)****-****",
    "nome_curto": "Mascara nome: J***o",
}


def mask_data(value: str, pattern: Optional[str] = None) -> str:
    """Aplica mascaramento a dados sensíveis.

    Args:
        value: String contendo dados potencialmente sensíveis.
        pattern: Tipo específico ('email', 'cpf', 'telefone') ou None para todos.

    Retorna:
        String com dados mascarados.
    """
    result = value
    for regex, replacement, name in MASK_PATTERNS:
        if pattern and name != pattern:
            continue
        result = re.sub(regex, replacement, result)
    return result


def mask_dataframe(df, columns: Optional[list[str]] = None, pattern: Optional[str] = None):
    """Aplica mascaramento a colunas de um DataFrame (pandas).

    Args:
        df: pandas DataFrame.
        columns: Colunas a mascarar (padrão: todas string).
        pattern: Tipo de mascaramento (padrão: auto-detect).

    Retorna:
        DataFrame com dados mascarados.
    """
    import pandas as pd
    result = df.copy()
    cols = columns or [c for c in df.columns if df[c].dtype == object]
    for col in cols:
        result[col] = result[col].astype(str).apply(lambda x: mask_data(x, pattern))
    return result


# ─── Classificação de Sensibilidade ─────────────────────────────────

SENSITIVE_PATTERNS: dict[str, int] = {
    "cpf": 5,
    "rg": 5,
    "passaporte": 5,
    "cartao credito": 5,
    "diagnostico": 5,
    "biometria": 5,
    "orientacao sexual": 5,
    "religiao": 5,
    "saude": 4,
    "doenca": 4,
    "renda": 3,
    "cep": 2,
    "idade": 1,
    "genero": 1,
}

SENSITIVITY_LABELS: dict[int, str] = {
    5: "CRITICO (art. 5º LGPD - dado sensivel)",
    4: "ALTO (art. 5º LGPD)",
    3: "MEDIO",
    2: "BAIXO",
    1: "MINIMO",
}


def classify_sensitivity(field_name: str, sample_value: Optional[str] = None) -> dict:
    """Classifica a sensibilidade de um campo conforme LGPD Art. 5º.

    Args:
        field_name: Nome do campo (ex: 'cpf', 'diagnostico').
        sample_value: Valor opcional para detecção por padrão.

    Retorna:
        Dict com classificação.
    """
    name_lower = field_name.lower()
    max_level = 1

    for pattern, level in SENSITIVE_PATTERNS.items():
        if pattern in name_lower:
            max_level = max(max_level, level)

    if sample_value:
        for regex, _, name in MASK_PATTERNS:
            if re.search(regex, sample_value):
                from collections import Counter
                level_map = {"cpf": 5, "email": 3, "telefone": 3}
                if name in level_map:
                    max_level = max(max_level, level_map[name])

    return {
        "field": field_name,
        "sensitivity_level": max_level,
        "label": SENSITIVITY_LABELS.get(max_level, "INDEFINIDO"),
        "lgpd_article": "Art. 5º, II" if max_level >= 5 else "Art. 5º, I",
        "requires_encryption": max_level >= 4,
        "requires_anonymization": max_level >= 2,
    }


# ─── Utilitários ────────────────────────────────────────────────────

def generate_salt(length: int = 16) -> str:
    """Gera salt criptográfico aleatório."""
    return hashlib.sha256(os.urandom(32)).hexdigest()[:length]


def verify_anonymization(
    records: list[dict],
    quasi_identifiers: list[str],
    k: int = 5,
) -> dict:
    """Verifica se um dataset satisfaz k-anonymity.

    Retorna dict com status (pass/fail), k real mínimo e detalhes.
    """
    from collections import Counter
    keys = [tuple(r[qi] for qi in quasi_identifiers) for r in records]
    freq = Counter(keys)
    min_k = min(freq.values())
    violations = [key for key, count in freq.items() if count < k]
    return {
        "pass": min_k >= k,
        "min_k": min_k,
        "required_k": k,
        "total_groups": len(freq),
        "violations": len(violations),
        "violation_groups": violations[:10],
    }
