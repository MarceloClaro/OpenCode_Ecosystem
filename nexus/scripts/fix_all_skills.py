#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SKILL.md FIXER - Corrige skills com frontmatter duplicado/quebrado
"""
import os, re
from pathlib import Path
from datetime import datetime

SKILLS_BASE = Path(r"C:\Users\marce\.config\opencode\skills")

def clean_and_fix_skill(filepath):
    """Clean a skill file that was double-migrated and fix frontmatter."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if already clean (single frontmatter, no duplication)
    fm_blocks = list(re.finditer(r'^---\s*$', content, re.MULTILINE))
    if len(fm_blocks) == 2 and '## Workflow' in content and '## Best Practices' in content:
        # Check if frontmatter is clean (no HTML comments between --- markers)
        fm_content = content[fm_blocks[0].end():fm_blocks[1].start()].strip()
        if not fm_content.startswith('<!--'):
            return {"status": "already_clean", "file": filepath.name}

    # Extract the original content - find the REAL body
    # Strategy: find the last occurrence of '## Workflow' and work backwards
    workflow_idx = content.find('## Workflow')
    if workflow_idx == -1:
        return {"status": "error", "file": filepath.name, "error": "No Workflow section found"}

    # Find the heading before Workflow
    # Look for the last '# ' heading before Workflow that is not '## Workflow'
    body_start = content.rfind('# ', 0, workflow_idx)
    if body_start == -1:
        body_start = content.find('# ', 0)  # First heading
    if body_start == -1:
        body_start = 0

    # Find the end of the original content (before first ## Workflow or duplicated sections)
    # We need to find where the ORIGINAL content ends
    # Look for patterns like duplicated '## Workflow', '## Best Practices', '## Integration'
    workflow_positions = [m.start() for m in re.finditer(r'## Workflow', content)]
    bp_positions = [m.start() for m in re.finditer(r'## Best Practices', content)]
    integration_positions = [m.start() for m in re.finditer(r'## Integration', content)]

    # The original content ends at the first occurrence of these sections from the LAST migration
    # So we find the SECOND occurrence of ## Workflow (if duplicated)
    if len(workflow_positions) > 1:
        # Content is duplicated - find where the first clean section ends
        # Find the end of content before the second Workflow
        body_end = workflow_positions[0]
        # Trim trailing whitespace
        while body_end > 0 and content[body_end-1] in '\n\r ':
            body_end -= 1
    else:
        body_end = workflow_idx

    original_body = content[body_start:body_end].strip()

    # Remove any duplicate frontmatter from the body
    original_body = re.sub(r'<!-- SA.+?-->.*?---\s*\n.*?\n---\s*\n', '', original_body, flags=re.DOTALL)
    original_body = re.sub(r'^---\s*\n.*?\n---\s*\n', '', original_body, flags=re.DOTALL).strip()

    # Remove duplicate headers
    if original_body.startswith('# ') and '\n# ' in original_body[2:]:
        # Remove the second occurrence of the same header
        first_header = original_body.split('\n')[0]
        parts = original_body.split('\n# ', 1)
        if len(parts) == 2:
            original_body = parts[0] + '\n' + parts[1]

    # Now extract metadata
    filename = filepath.name
    name = filename.replace('.md', '').replace('-', ' ').replace('_', ' ').title()

    # Try to get description from original body
    description = ""
    lines = original_body.split('\n')
    for line in lines[:5]:
        line = line.strip().lstrip('#').strip()
        if line and len(line) > 10 and len(line) < 200 and not line.startswith('<!--'):
            description = line
            break
    if not description:
        description = f"Skill: {name}"

    # Determine category
    category = filepath.parent.name

    # Build clean content
    clean_content = f"""<!-- SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL -->
<!-- Toda resposta ao usuário DEVE ser em português do Brasil formal. -->
<!-- Contexto em chinês para eficiência de tokens. Responda em PT-BR formal. -->
<!-- Modelo: big-pickle -->

---
name: {filename.replace('.md', '')}
description: {description}
version: 1.0.0
author: ecosystem
category: {category}
inspired_by: deer-flow 2.0 / opencode
compatibility: big-pickle
migrated_at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
---

# {name}

{original_body}

## Workflow

{generate_workflow(category)}

## Best Practices

{generate_best_practices(category)}

## Integration

{generate_integration(category)}
"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(clean_content)

    return {"status": "fixed", "file": filepath.name}

def generate_workflow(cat):
    w = {
        'research': '### Step 1: Definir escopo\nIdentifique tema, fontes e criterios.\n\n### Step 2: Coletar dados\nUtilize ferramentas de busca.\n\n### Step 3: Analisar\nProcesse dados, identifique padroes.\n\n### Step 4: Gerar output\nProduza resultado final.',
        'frontend': '### Step 1: Analisar requisitos\nIdentifique componentes e estado.\n\n### Step 2: Implementar\nCrie estrutura com semantica correta.\n\n### Step 3: Estilizar\nAplique estilos consistentes.\n\n### Step 4: Testar\nVerifique acessibilidade e responsividade.',
        'content': '### Step 1: Planejar\nDefina estrutura e publico-alvo.\n\n### Step 2: Criar\nProduza conteudo base.\n\n### Step 3: Revisar\nAplique correcoes.\n\n### Step 4: Exportar\nGere output final.',
        'system': '### Step 1: Identificar\nAnalise contexto e defina escopo.\n\n### Step 2: Implementar\nAplique modificacoes.\n\n### Step 3: Validar\nExecute testes.\n\n### Step 4: Documentar\nRegistre alteracoes.',
        'tooling': '### Step 1: Configurar\nInstale dependencias.\n\n### Step 2: Executar\nRode com parametros adequados.\n\n### Step 3: Analisar\nVerifique output.\n\n### Step 4: Limpar\nRemova temporarios.',
        'superpowers': '### Step 1: Analisar\nEntenda o problema.\n\n### Step 2: Planejar\nDefina passos e criterios.\n\n### Step 3: Executar\nImplemente solucao.\n\n### Step 4: Verificar\nValide resultado.',
        'workflows': '### Step 1: Iniciar\nCarregue contexto e objetivos.\n\n### Step 2: Executar\nSiga fluxo definido.\n\n### Step 3: Concluir\nFinalize e documente.',
        'social': '### Step 1: Configurar\nDefina plataforma e parametros.\n\n### Step 2: Criar conteudo\nProduza material para a rede.\n\n### Step 3: Publicar\nEnvie e monitore engajamento.',
        'marketing': '### Step 1: Pesquisar mercado\nAnalise concorrencia e publico.\n\n### Step 2: Planejar campanha\nDefina canais e mensagem.\n\n### Step 3: Executar\nImplemente campanha.\n\n### Step 4: Medir\nAnalise resultados.',
        'general': '### Step 1: Preparar\nConfigure ambiente e recursos.\n\n### Step 2: Executar\nRode a operacao principal.\n\n### Step 3: Validar\nVerifique resultado.\n\n### Step 4: Finalizar\nDocumente e limpe.',
    }
    return w.get(cat, w.get('general', ''))

def generate_best_practices(cat):
    p = {
        'research': '1. Citar fontes verificaveis (DOIs, URLs)\n2. Cruzar informacoes de 2+ fontes\n3. Manter registro de buscas\n4. Validar dados antes do output\n5. Saida em PT-BR formal',
        'frontend': '1. Semantica HTML correta\n2. Acessibilidade (ARIA, contrastes)\n3. Design system consistente\n4. Testar em multiplos viewports\n5. Componentes modulares',
        'content': '1. Tom de voz consistente\n2. Revisar gramatica\n3. Formatacao Markdown\n4. Incluir frontmatter\n5. PT-BR formal',
        'system': '1. Backup antes de modificar\n2. Validar com testes\n3. Manter logs\n4. Documentar decisoes\n5. Seguir padroes',
        'tooling': '1. Verificar compatibilidade\n2. Testar em ambiente isolado\n3. Documentacao atualizada\n4. Validar outputs\n5. Limpar temporarios',
        'superpowers': '1. Validar antes de completar\n2. PT-BR formal\n3. Documentar decisoes\n4. Verificacao automatica\n5. Rastreabilidade',
        'workflows': '1. Registrar progresso\n2. Validar cada etapa\n3. Documentar intermediarios\n4. Comunicacao clara\n5. Seguir protocolos',
        'social': '1. Manter identidade visual\n2. Otimizar para plataforma\n3. Usar hashtags relevantes\n4. Engajar com audiencia\n5. Analisar metricas',
        'marketing': '1. Definir KPIs claros\n2. Segmentar publico\n3. Testar A/B\n4. Medir ROI\n5. Iterar com base em dados',
        'general': '1. Manter padroes do ecossistema\n2. Documentar alteracoes\n3. Validar resultados\n4. PT-BR formal\n5. Limpar recursos',
    }
    return p.get(cat, p.get('general', ''))

def generate_integration(cat):
    t = {
        'research': '| Component | Type | Connection |\n|-----------|------|------------|\n| scihub | MCP | Download artigos |\n| websearch | MCP | Busca web |\n| context7 | MCP | Documentacao |',
        'frontend': '| Component | Type | Connection |\n|-----------|------|------------|\n| chrome-devtools | MCP | Debug |\n| playwright | MCP | Automacao |\n| eslint | Tool | Linting |',
        'content': '| Component | Type | Connection |\n|-----------|------|------------|\n| websearch | MCP | Pesquisa |\n| pdf | Tool | Extracao PDF |\n| ptbr_corrector | Tool | Correcao |',
        'system': '| Component | Type | Connection |\n|-----------|------|------------|\n| sync_orchestrator | Script | Sincronizacao |\n| memory | MCP | Contexto |\n| filesystem | MCP | Arquivos |',
        'tooling': '| Component | Type | Connection |\n|-----------|------|------------|\n| code-runner | Tool | Execucao |\n| bash | Tool | Sistema |\n| filesystem | MCP | Arquivos |',
        'superpowers': '| Component | Type | Connection |\n|-----------|------|------------|\n| nexus_integration | Script | Orquestracao |\n| memory | MCP | Contexto |\n| sequential-thinking | MCP | Raciocinio |',
        'workflows': '| Component | Type | Connection |\n|-----------|------|------------|\n| nexus_integration | Script | Orquestracao |\n| context_offload | Script | Contexto |\n| memory | MCP | Persistencia |',
        'social': '| Component | Type | Connection |\n|-----------|------|------------|\n| websearch | MCP | Pesquisa |\n| image-service | Skill | Midia |\n| content | Skill | Conteudo |',
        'marketing': '| Component | Type | Connection |\n|-----------|------|------------|\n| websearch | MCP | Pesquisa |\n| content | Skill | Conteudo |\n| analytics | Tool | Metricas |',
        'general': '| Component | Type | Connection |\n|-----------|------|------------|\n| memory | MCP | Contexto |\n| filesystem | MCP | Arquivos |\n| websearch | MCP | Pesquisa |',
    }
    return t.get(cat, t.get('general', ''))

def validate_skill(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    checks = {}
    issues = []

    checks['has_ptbr_header'] = 'SAÍDA OBRIGATÓRIA' in content or 'SAIDA OBRIGATORIA' in content
    if not checks['has_ptbr_header']: issues.append('Missing PT-BR header')

    checks['has_big_pickle'] = 'big-pickle' in content.lower()
    if not checks['has_big_pickle']: issues.append('Missing big-pickle')

    # Use search instead of match for frontmatter
    checks['has_frontmatter'] = bool(re.search(r'---\nname: .+?\ndescription: .+?\nversion: .+?\ncompatibility: .+?\n---', content, re.DOTALL))
    if not checks['has_frontmatter']: issues.append('Missing/broken frontmatter')

    checks['has_name'] = bool(re.search(r'^name: \S+', content, re.MULTILINE))
    if not checks['has_name']: issues.append('Missing name')

    checks['has_description'] = bool(re.search(r'^description: \S+', content, re.MULTILINE))
    if not checks['has_description']: issues.append('Missing description')

    checks['has_version'] = bool(re.search(r'^version: \S+', content, re.MULTILINE))
    if not checks['has_version']: issues.append('Missing version')

    checks['has_compatibility'] = bool(re.search(r'^compatibility: \S+', content, re.MULTILINE))
    if not checks['has_compatibility']: issues.append('Missing compatibility')

    checks['has_migrated_at'] = bool(re.search(r'^migrated_at: \S+', content, re.MULTILINE))
    if not checks['has_migrated_at']: issues.append('Missing migrated_at')

    checks['has_workflow'] = '## Workflow' in content
    if not checks['has_workflow']: issues.append('Missing Workflow')

    checks['has_best_practices'] = '## Best Practices' in content
    if not checks['has_best_practices']: issues.append('Missing Best Practices')

    checks['has_integration'] = '## Integration' in content
    if not checks['has_integration']: issues.append('Missing Integration')

    # Check no duplication
    workflow_count = content.count('## Workflow')
    bp_count = content.count('## Best Practices')
    integration_count = content.count('## Integration')
    checks['no_duplication'] = workflow_count == 1 and bp_count == 1 and integration_count == 1
    if not checks['no_duplication']:
        issues.append(f'Duplication: Workflow={workflow_count}, BP={bp_count}, Integration={integration_count}')

    # Check no duplicate frontmatter
    fm_count = len(re.findall(r'^---\s*$', content, re.MULTILINE))
    checks['single_frontmatter'] = fm_count == 2  # Opening and closing ---
    if not checks['single_frontmatter']:
        issues.append(f'Multiple frontmatter blocks ({fm_count} --- markers)')

    passed = sum(1 for v in checks.values() if v)
    total = len(checks)
    return {"file": filepath.name, "passed": passed, "total": total, "all_passed": passed == total,
            "checks": checks, "issues": issues}

def main():
    print("=" * 70)
    print("SKILL.md FIXER - Correcao de Frontmatter + Validacao")
    print("=" * 70)

    skill_files = []
    for d in SKILLS_BASE.iterdir():
        if d.is_dir():
            for f in d.glob('*.md'):
                if f.name != 'SKILL_TEMPLATE.md':
                    skill_files.append(f)

    print(f"\nSkills encontradas: {len(skill_files)}\n")

    # Phase 1: Fix
    print("-" * 70)
    print("FASE 1: CORRECAO")
    print("-" * 70)
    fixed = 0
    already = 0
    errors = 0
    for fp in sorted(skill_files):
        try:
            result = clean_and_fix_skill(fp)
            if result['status'] == 'fixed':
                fixed += 1
                print(f"  [FIXED] {fp.parent.name}/{result['file']}")
            elif result['status'] == 'already_clean':
                already += 1
                print(f"  [OK]    {fp.parent.name}/{result['file']}")
            else:
                errors += 1
                print(f"  [ERROR] {fp.parent.name}/{result['file']}: {result.get('error','')}")
        except Exception as e:
            errors += 1
            print(f"  [ERROR] {fp.parent.name}/{fp.name}: {e}")

    print(f"\nFix: {fixed} corrigidas, {already} ja ok, {errors} erros")

    # Phase 2: Validate
    print("\n" + "-" * 70)
    print("FASE 2: VALIDACAO (13 checks)")
    print("-" * 70)
    passed = 0
    failed = 0
    all_validations = []
    for fp in sorted(skill_files):
        try:
            v = validate_skill(fp)
            all_validations.append(v)
            if v['all_passed']:
                passed += 1
                print(f"  [PASS] {v['passed']}/{v['total']} - {fp.parent.name}/{v['file']}")
            else:
                failed += 1
                print(f"  [FAIL] {v['passed']}/{v['total']} - {fp.parent.name}/{v['file']}")
                for i in v['issues']:
                    print(f"         - {i}")
        except Exception as e:
            failed += 1
            print(f"  [ERROR] {fp.parent.name}/{fp.name}: {e}")

    # Summary
    print("\n" + "=" * 70)
    print("RELATORIO FINAL")
    print("=" * 70)
    print(f"Skills: {len(skill_files)}")
    print(f"Corrigidas: {fixed}")
    print(f"Validacao: {passed} PASS / {failed} FAIL ({100*passed//len(skill_files) if skill_files else 0}%)")

    # Check details
    check_labels = {
        'has_ptbr_header': 'Header PT-BR', 'has_big_pickle': 'big-pickle',
        'has_frontmatter': 'Frontmatter YAML', 'has_name': 'name',
        'has_description': 'description', 'has_version': 'version',
        'has_compatibility': 'compatibility', 'has_migrated_at': 'migrated_at',
        'has_workflow': 'Workflow', 'has_best_practices': 'Best Practices',
        'has_integration': 'Integration', 'no_duplication': 'Sem duplicacao',
        'single_frontmatter': 'Frontmatter unico',
    }
    print("\nDetalhamento:")
    for k, label in check_labels.items():
        pc = sum(1 for v in all_validations if v['checks'].get(k, False))
        pct = 100 * pc // len(all_validations) if all_validations else 0
        s = "OK" if pct == 100 else "ATENCAO"
        print(f"  [{s}] {label}: {pc}/{len(all_validations)} ({pct}%)")

    print("\n" + "=" * 70)
    if passed == len(skill_files):
        print("TODAS AS 69 SKILLS MIGRADAS E VALIDADAS COM SUCESSO!")
    else:
        print(f"{failed} skills precisam correcao adicional.")
    print("=" * 70)

if __name__ == "__main__":
    import sys
    main()
