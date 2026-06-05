# SPEC-02: Supply Chain Security + SPEC-07: Registry v2.0 (P0)

> Lacunas 2+7: Seguranca criptografica para skills + registro versionado com integridade

## Arquitetura

```
supply_chain/
├── __init__.py
├── registry_v2.py          # Registry com SemVer + SHA256 + assinatura
├── skill_signer.py         # Assinatura Ed25519 de skills
├── skill_verifier.py       # Verificacao de integridade na carga
├── audit_trail.py          # Trilha de auditoria de atualizacoes
├── secure_loader.py        # Carregador com modo --secure
├── schema.sql              # Schema SQLite para registry v2
└── migrate_v1_to_v2.py     # Migracao do registry v1 -> v2
```

## Estrutura do Manifesto (skill.manifest.json)

```json
{
  "name": "supply-chain-security",
  "version": "1.0.0",
  "semver": "1.0.0",
  "sha256": "a1b2c3d4...",
  "signature": "Ed25519:...",
  "public_key": "MCowBQYD...",
  "author": "opencode-ecosystem",
  "created": "2026-06-04T12:00:00Z",
  "updated": "2026-06-04T12:00:00Z",
  "dependencies": {},
  "changelog": [
    {"version": "1.0.0", "date": "2026-06-04", "changes": ["Initial release"]}
  ],
  "permissions": ["read:filesystem", "write:filesystem"],
  "allowed_tools": ["bash", "edit", "write"],
  "denied_tools": [],
  "human_approval_required": false,
  "min_opencode_version": "1.14.0"
}
```

## Fluxo de Carga Segura

```
Skill Carregada
      │
      ▼
[1] Manifesto presente? ──── NÃO ──► MODO DEV: carrega com warning
      │ SIM                           MODO SECURE: BLOQUEIA
      ▼
[2] SHA256 do conteudo bate? ── NÃO ─► BLOQUEIA (integrity failure)
      │ SIM
      ▼
[3] Assinatura Ed25519 valida? ─ NÃO ─► BLOQUEIA (untrusted source)
      │ SIM
      ▼
[4] Lista de permissoes compativel? ─ NÃO ─► BLOQUEIA (policy violation)
      │ SIM
      ▼
[5] SemVer >= min_opencode_version? ─ NÃO ─► WARNING (version mismatch)
      │ SIM
      ▼
CARREGA skill
```
