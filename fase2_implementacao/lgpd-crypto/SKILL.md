---
name: lgpd-crypto
description: "Skill de criptografia e anonimizacao para conformidade LGPD. Pseudonimizacao (hash+salt), anonimizacao (k-anonymity, l-diversity), criptografia AES-256-GCM, mascaramento de dados. Integra com ecossistema OpenCode para protecao de dados pessoais em pipelines de pesquisa."
---

# lgpd-crypto v1.0 — Proteção de Dados Pessoais (LGPD Art. 6º, 46º)

## Quando Usar
- **Pseudonimização**: Substituir identificadores diretos por pseudônimos reversíveis
- **Anonimização**: Remover identificação irreversível (k-anonymity ≥ 5, l-diversity ≥ 3)
- **Criptografia**: Dados em repouso (AES-256-GCM) ou em trânsito (TLS 1.3)
- **Mascaramento**: Logs, debugging, ambientes de teste
- **Auditoria**: Verificar conformidade com art. 46 (segurança) e art. 18 (direitos do titular)

## Instalação
```bash
pip install cryptography pandas
```

## Módulos

| Módulo | Função | LGPD |
|--------|--------|------|
| `pseudonymize()` | Hash SHA-256 + salt por campo | Art. 12 (dados pseudonimizados) |
| `anonymize_k_anonymity()` | Generalização/supressão para k-anonymity | Art. 12 (dados anonimizados) |
| `anonymize_l_diversity()` | k-anonymity + l-diversity | Art. 12 + relatório de impacto |
| `encrypt_aes256gcm()` | Criptografia autenticada AES-256-GCM | Art. 46 (segurança) |
| `decrypt_aes256gcm()` | Decriptografia com verificação de integridade | Art. 46 |
| `mask_data()` | Mascaramento seletivo (CPF, email, nome) | Art. 48 (incidentes) |
| `classify_data()` | Classificação automática de sensibilidade | Art. 5º (dado sensível) |

## Exemplos

```python
from lgpd_crypto import pseudonymize, anonymize_k_anonymity, encrypt_aes256gcm, mask_data

# Pseudonimizar dados de pesquisa
pid = pseudonymize("João Silva", salt="projeto-x")

# Anonimizar dataset (k=5)
anon = anonymize_k_anonymity(df, k=5, quasi_identifiers=["idade", "cep", "genero"])

# Criptografar arquivo
ct, key, nonce = encrypt_aes256gcm(dados_sensiveis)

# Mascarar para log
mask_data("joao@email.com")  # joao***@email.com
```
