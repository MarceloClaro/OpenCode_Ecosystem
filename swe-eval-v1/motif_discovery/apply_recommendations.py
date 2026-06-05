import sys, json, hashlib, os
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent.parent))
from motif_discovery.inventory_auditor import InventoryAuditor

ROOT = r"C:\Users\marce\.config\opencode"

auditor = InventoryAuditor(ROOT)
report_before = auditor.audit()

print("=== ANTES ===")
print(f"Skills no disco: {report_before.total_skills}")
print(f"No Registry: {report_before.registered_skills}")
print(f"Completude: {report_before.completeness_pct:.1f}%")
print(f"Gaps: {len(report_before.gaps)}")

# Gerar manifestos para TODAS skills (recursivo) que nao tem manifesto
valid_all = [g.entity for g in report_before.gaps if g.gap_type in ("missing_manifest", "unregistered")]
print(f"\nGerando manifestos para {len(valid_all)} skills...")

skills_dir = Path(ROOT) / "skills"
count = 0
for name in valid_all:
    skill_dir = skills_dir / name
    if skill_dir.exists() and (skill_dir / "SKILL.md").exists():
        sha = hashlib.sha256()
        for f in sorted(skill_dir.rglob("*")):
            if f.is_file() and f.name != "skill.manifest.json":
                sha.update(f.relative_to(skill_dir).as_posix().encode())
                sha.update(f.read_bytes())

        manifest = {
            "name": name, "version": "0.1.0", "semver": "0.1.0",
            "sha256": sha.hexdigest(), "signature": "", "public_key": "",
            "author": "opencode-ecosystem",
            "created": datetime.now(timezone.utc).isoformat(),
            "updated": datetime.now(timezone.utc).isoformat(),
            "dependencies": {},
            "changelog": [{"version": "0.1.0", "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "changes": ["Registro via Inventory Auditor (MDE)"]}],
            "permissions": ["read:filesystem"], "allowed_tools": [], "denied_tools": [],
            "human_approval_required": False, "min_opencode_version": "1.14.0",
            "skill_path": str(skill_dir.absolute()),
        }
        (skill_dir / "skill.manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        count += 1

print(f"{count} manifestos gerados com SHA256.")

# Re-auditar
report_after = auditor.audit()
print(f"\n=== DEPOIS ===")
print(f"No Registry: {report_after.registered_skills}")
print(f"Completude: {report_after.completeness_pct:.1f}%")
print(f"Gaps restantes: {len(report_after.gaps)}")
print(f"Lacunas resolvidas: {len(report_before.gaps) - len(report_after.gaps)}")

# Resumo dos gaps restantes
if report_after.gaps:
    print("\nGaps restantes (primeiros 5):")
    for g in report_after.gaps[:5]:
        print(f"  [{g.severity}] [{g.gap_type}] {g.entity}")
