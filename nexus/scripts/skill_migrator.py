#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, re, logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

def parse_existing_skill(content):
    result = {"name": "unknown", "description": "", "body": content}
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
    if match:
        frontmatter = {}
        for line in match.group(1).strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                frontmatter[k.strip()] = v.strip().strip('"')
        result.update(frontmatter)
        result["body"] = match.group(2).strip()
    if result["name"] == "unknown":
        result["name"] = "skill-migrated"
    if not result.get("description"):
        result["description"] = "Migrated skill"
    return result

def migrate_skill(source_path, target_path=None):
    with open(source_path, "r", encoding="utf-8") as f:
        content = f.read()
    parsed = parse_existing_skill(content)
    source = Path(source_path)
    if target_path is None:
        target_dir = source.parent / "migrated"
        target_dir.mkdir(exist_ok=True)
        target_path = target_dir / source.name
    if not content.startswith("---\nname:"):
        new_content = f"""<!-- SAIDA OBRIGATORIA: PORTUGUES BRASILEIRO FORMAL -->
<!-- Modelo: big-pickle -->

---
name: {parsed['name']}
description: {parsed.get('description', 'Migrated skill')}
version: 1.0.0
author: ecosystem
inspired_by: deer-flow 2.0 / opencode
compatibility: big-pickle
migrated_at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
original_source: {source.name}
---

{content}
"""
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(new_content)
    return str(target_path)

def batch_migrate(source_dir, target_dir=None):
    source = Path(source_dir)
    target_dir = Path(target_dir) if target_dir else source / "migrated"
    target_dir.mkdir(parents=True, exist_ok=True)
    migrated = []
    for skill_file in source.glob("*.md"):
        if skill_file.name == "SKILL_TEMPLATE.md":
            continue
        target = target_dir / skill_file.name
        result = migrate_skill(str(skill_file), str(target))
        migrated.append(result)
    return migrated

def validate_skill_format(skill_path):
    with open(skill_path, "r", encoding="utf-8") as f:
        content = f.read()
    issues = []
    checks = {
        "has_frontmatter": content.startswith("---") or "SAIDA OBRIGATORIA" in content or "SAÍDA OBRIGATÓRIA" in content,
        "has_name": "name:" in content,
        "has_description": "description:" in content,
        "has_big_pickle": "big-pickle" in content.lower(),
        "has_workflow": "## Workflow" in content or "workflow" in content.lower(),
        "has_best_practices": "## Best Practices" in content or "best practices" in content.lower(),
    }
    for check, passed in checks.items():
        if not passed:
            issues.append(f"Missing: {check}")
    return {"file": skill_path, "passed": all(checks.values()), "checks": checks, "issues": issues}

if __name__ == "__main__":
    skills_base = os.path.join(os.path.dirname(__file__), "..", "..", "skills")
    print("=" * 60)
    print("SKILL MIGRATOR - deer-flow 2.0 Format")
    print("=" * 60)
    total = 0
    passed = 0
    for skill_dir in Path(skills_base).iterdir():
        if skill_dir.is_dir():
            md_files = list(skill_dir.glob("*.md"))
            if md_files:
                print(f"\nDirectory: {skill_dir.name} ({len(md_files)} files)")
                for mf in md_files:
                    total += 1
                    result = validate_skill_format(str(mf))
                    if result["passed"]:
                        passed += 1
                    status = "OK" if result["passed"] else f"ISSUES: {len(result['issues'])}"
                    print(f"  {mf.name}: {status}")
    print(f"\n" + "=" * 60)
    print(f"Validation: {passed}/{total} skills meet SKILL.md standard")
    print("=" * 60)
