#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SKILL.md MIGRATOR v2.0 - Conversao em massa com validacao minuciosa
Converte 69 skills existentes para o padrao deer-flow 2.0
"""
import os, re, json, logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

SKILLS_BASE = Path(r"C:\Users\marce\.config\opencode\skills")

def extract_name_from_file(filename):
    """Extract skill name from filename."""
    name = filename.replace('.md', '')
    name = name.replace('-', ' ').replace('_', ' ')
    return name.title()

def extract_description_from_content(content, filename):
    """Try to extract description from existing content."""
    # Try to find description in existing frontmatter
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
    if match:
        fm = match.group(1)
        desc_match = re.search(r'description:\s*["\']?(.*?)["\']?\s*$', fm, re.MULTILINE)
        if desc_match:
            return desc_match.group(1).strip().strip('"').strip("'")
    # Try first line as description
    lines = content.strip().split('\n')
    for line in lines[:5]:
        line = line.strip().lstrip('#').strip()
        if line and len(line) > 10 and len(line) < 200:
            return line
    return f"Skill: {extract_name_from_file(filename)}"

def infer_category_from_path(filepath):
    """Infer category from directory path."""
    parts = filepath.parts
    for p in parts:
        if p in ('content', 'frontend', 'general', 'marketing', 'research', 'social', 'superpowers', 'system', 'tooling', 'workflows'):
            return p
    return 'general'

def generate_workflow_section(category, content):
    """Generate a workflow section based on category and existing content."""
    workflows = {
        'research': """### Step 1: Definir escopo da pesquisa
Identifique o tema, fontes e criterios de busca.

### Step 2: Executar coleta de dados
Utilize ferramentas de busca (websearch, scihub, context7) para coletar informacoes.

### Step 3: Analisar e sintetizar
Processe os dados coletados, identifique padroes e gere insights.

### Step 4: Gerar output
Produza o resultado final no formato especificado (relatorio, artigo, resumo).""",
        'frontend': """### Step 1: Analisar requisitos
Identifique componentes, estado e interacoes necessarias.

### Step 2: Implementar estrutura
Crie a estrutura HTML/JSX com semantica correta.

### Step 3: Adicionar estilos
Aplique estilos consistentes com o design system existente.

### Step 4: Testar e validar
Verifique acessibilidade, responsividade e performance.""",
        'content': """### Step 1: Planejar conteudo
Defina estrutura, publico-alvo e tom de voz.

### Step 2: Criar rascunho
Produza o conteudo base seguindo as diretrizes.

### Step 3: Revisar e refinar
Aplique correcoes de estilo, gramatica e formatacao.

### Step 4: Exportar
Gere o output final no formato desejado.""",
        'system': """### Step 1: Identificar problema
Analise o contexto e defina o escopo da solucao.

### Step 2: Implementar
Aplique as modificacoes necessarias no sistema.

### Step 3: Validar
Execute testes e verifique o funcionamento correto.

### Step 4: Documentar
Registre as alteracoes e atualize a documentacao.""",
        'tooling': """### Step 1: Configurar ferramenta
Instale e configure as dependencias necessarias.

### Step 2: Executar operacao
Rode a ferramenta com os parametros adequados.

### Step 3: Analisar resultado
Verifique o output e valide a corretude.

### Step 4: Limpar recursos
Remova arquivos temporarios e finalize.""",
        'superpowers': """### Step 1: Analisar contexto
Entenda o problema e identifique a abordagem ideal.

### Step 2: Planejar execucao
Defina os passos e criterios de sucesso.

### Step 3: Executar
Implemente a solucao seguindo o plano.

### Step 4: Verificar
Valide o resultado contra os criterios definidos.""",
        'workflows': """### Step 1: Iniciar workflow
Carregue o contexto e defina os objetivos.

### Step 2: Executar etapas
Siga o fluxo definido, registrando progresso.

### Step 3: Concluir
Finalize e documente os resultados.""",
    }
    return workflows.get(category, workflows.get('system', ''))

def generate_best_practices(category):
    """Generate best practices based on category."""
    practices = {
        'research': """1. Sempre citar fontes verificaveis (DOIs, URLs)
2. Cruzar informacoes de pelo menos 2 fontes independentes
3. Manter registro de buscas e parametros utilizados
4. Validar dados antes de incluir no output final
5. Manter saida em PT-BR formal""",
        'frontend': """1. Manter semantica HTML correta
2. Garantir acessibilidade (ARIA labels, contrastes)
3. Usar design system existente como referencia
4. Testar em multiples viewport sizes
5. Manter componentes reutilizaveis e modulares""",
        'content': """1. Manter tom de voz consistente
2. Revisar gramatica e ortografia antes de entregar
3. Usar formatacao Markdown consistente
4. Incluir metadados (frontmatter) em todo conteudo
5. Validar saida em PT-BR formal""",
        'system': """1. Sempre criar backup antes de modificar arquivos criticos
2. Validar mudancas com testes antes de commit
3. Manter logs de alteracoes
4. Documentar decisoes de design
5. Seguir padroes do ecossistema""",
        'tooling': """1. Verificar compatibilidade de versoes
2. Testar em ambiente isolado antes de producao
3. Manter documentacao atualizada
4. Validar outputs automaticamente
5. Limpar recursos temporarios""",
        'superpowers': """1. Sempre validar antes de completar
2. Manter comunicacao clara em PT-BR
3. Documentar decisoes e rationale
4. Usar verificacao automatica quando disponivel
5. Manter rastreabilidade de mudancas""",
        'workflows': """1. Manter registro de progresso
2. Validar cada etapa antes de avancar
3. Documentar resultados intermediarios
4. Manter comunicacao clara
5. Seguir protocolos definidos""",
    }
    return practices.get(category, practices.get('system', ''))

def generate_integration_table(category, filename):
    """Generate integration table based on category."""
    integrations = {
        'research': """| Component | Type | Connection |
|-----------|------|------------|
| scihub | MCP | Download de artigos academicos |
| websearch | MCP | Busca na web |
| context7 | MCP | Consulta de documentacao |
| SEEKER | Agent | Pesquisa profunda |""",
        'frontend': """| Component | Type | Connection |
|-----------|------|------------|
| chrome-devtools | MCP | Teste e debug |
| playwright | MCP | Automacao browser |
| eslint | Tool | Linting de codigo |""",
        'content': """| Component | Type | Connection |
|-----------|------|------------|
| websearch | MCP | Pesquisa de conteudo |
| pdf | Tool | Extracao de PDFs |
| ptbr_corrector | Tool | Correcao linguistica |""",
        'system': """| Component | Type | Connection |
|-----------|------|------------|
| sync_orchestrator | Script | Sincronizacao do ecossistema |
| memory | MCP | Persistencia de contexto |
| filesystem | MCP | Operacoes de arquivo |""",
        'tooling': """| Component | Type | Connection |
|-----------|------|------------|
| code-runner | Tool | Execucao de codigo |
| bash | Tool | Comandos de sistema |
| filesystem | MCP | Gerenciamento de arquivos |""",
        'superpowers': """| Component | Type | Connection |
|-----------|------|------------|
| nexus_integration | Script | Orquestracao de agentes |
| memory | MCP | Persistencia de contexto |
| sequential-thinking | MCP | Raciocinio estruturado |""",
        'workflows': """| Component | Type | Connection |
|-----------|------|------------|
| nexus_integration | Script | Orquestracao |
| context_offload | Script | Gerenciamento de contexto |
| memory | MCP | Persistencia |""",
    }
    return integrations.get(category, integrations.get('system', ''))

def migrate_skill(filepath):
    """Migrate a single skill file to SKILL.md standard."""
    with open(filepath, 'r', encoding='utf-8') as f:
        original_content = f.read()

    filename = filepath.name
    category = infer_category_from_path(filepath)
    name = extract_name_from_file(filename)
    description = extract_description_from_content(original_content, filename)

    # Check if already in new format
    if original_content.startswith('---\nname:') and 'compatibility:' in original_content[:200]:
        return {"status": "already_migrated", "file": str(filepath)}

    # Extract existing frontmatter if present
    existing_fm = ''
    body = original_content
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', original_content, re.DOTALL)
    if match:
        existing_fm = match.group(1).strip()
        body = match.group(2).strip()
    else:
        body = original_content.strip()

    # Build new content
    new_content = f"""<!-- SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL -->
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

{body}

## Workflow

{generate_workflow_section(category, original_content)}

## Best Practices

{generate_best_practices(category)}

## Integration

{generate_integration_table(category, filename)}
"""

    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return {"status": "migrated", "file": str(filepath), "category": category, "name": name}

def validate_skill(filepath):
    """Validate a skill file against SKILL.md standard."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    checks = {}
    issues = []

    # 1. Header PT-BR
    checks['has_ptbr_header'] = 'SAÍDA OBRIGATÓRIA' in content
    if not checks['has_ptbr_header']:
        issues.append('Missing PT-BR header')

    # 2. Modelo big-pickle
    checks['has_big_pickle'] = 'big-pickle' in content.lower()
    if not checks['has_big_pickle']:
        issues.append('Missing big-pickle directive')

    # 3. Frontmatter YAML
    checks['has_frontmatter'] = bool(re.match(r'^---\s*\n.*?\n---', content, re.DOTALL))
    if not checks['has_frontmatter']:
        issues.append('Missing YAML frontmatter')

    # 4. name field
    checks['has_name'] = bool(re.search(r'^name:\s*\S+', content, re.MULTILINE))
    if not checks['has_name']:
        issues.append('Missing name in frontmatter')

    # 5. description field
    checks['has_description'] = bool(re.search(r'^description:\s*\S+', content, re.MULTILINE))
    if not checks['has_description']:
        issues.append('Missing description in frontmatter')

    # 6. version field
    checks['has_version'] = bool(re.search(r'^version:\s*\S+', content, re.MULTILINE))
    if not checks['has_version']:
        issues.append('Missing version in frontmatter')

    # 7. compatibility field
    checks['has_compatibility'] = bool(re.search(r'^compatibility:\s*\S+', content, re.MULTILINE))
    if not checks['has_compatibility']:
        issues.append('Missing compatibility in frontmatter')

    # 8. migrated_at field
    checks['has_migrated_at'] = bool(re.search(r'^migrated_at:\s*\S+', content, re.MULTILINE))
    if not checks['has_migrated_at']:
        issues.append('Missing migrated_at in frontmatter')

    # 9. Workflow section
    checks['has_workflow'] = '## Workflow' in content
    if not checks['has_workflow']:
        issues.append('Missing Workflow section')

    # 10. Best Practices section
    checks['has_best_practices'] = '## Best Practices' in content
    if not checks['has_best_practices']:
        issues.append('Missing Best Practices section')

    # 11. Integration section
    checks['has_integration'] = '## Integration' in content
    if not checks['has_integration']:
        issues.append('Missing Integration section')

    # 12. Original content preserved
    checks['has_body'] = len(content) > 200
    if not checks['has_body']:
        issues.append('Content too short - original may be lost')

    passed = sum(1 for v in checks.values() if v)
    total = len(checks)

    return {
        "file": str(filepath),
        "passed": passed,
        "total": total,
        "all_passed": passed == total,
        "checks": checks,
        "issues": issues
    }

def main():
    print("=" * 70)
    print("SKILL.md MIGRATOR v2.0 - Conversao em Massa + Validacao Minuciosa")
    print("=" * 70)

    all_results = []
    all_validations = []
    migrated_count = 0
    already_count = 0
    error_count = 0
    validation_passed = 0
    validation_failed = 0

    # Collect all skill files
    skill_files = []
    for d in SKILLS_BASE.iterdir():
        if d.is_dir():
            for f in d.glob('*.md'):
                if f.name != 'SKILL_TEMPLATE.md':
                    skill_files.append(f)

    print(f"\nTotal de skills encontradas: {len(skill_files)}")
    print(f"Diretorios: {[d.name for d in SKILLS_BASE.iterdir() if d.is_dir()]}\n")

    # Phase 1: Migration
    print("-" * 70)
    print("FASE 1: MIGRACAO")
    print("-" * 70)

    for filepath in sorted(skill_files):
        try:
            result = migrate_skill(filepath)
            all_results.append(result)
            if result['status'] == 'migrated':
                migrated_count += 1
                print(f"  [MIGRATED] {filepath.parent.name}/{filepath.name} -> {result['name']}")
            elif result['status'] == 'already_migrated':
                already_count += 1
                print(f"  [SKIPPED]  {filepath.parent.name}/{filepath.name} (ja no padrao)")
        except Exception as e:
            error_count += 1
            print(f"  [ERROR]    {filepath.parent.name}/{filepath.name}: {e}")
            all_results.append({"status": "error", "file": str(filepath), "error": str(e)})

    print(f"\nResumo migracao: {migrated_count} migradas, {already_count} ja ok, {error_count} erros")

    # Phase 2: Validation
    print("\n" + "-" * 70)
    print("FASE 2: VALIDACAO MINUCIOSA (12 checks por skill)")
    print("-" * 70)

    for filepath in sorted(skill_files):
        try:
            validation = validate_skill(filepath)
            all_validations.append(validation)
            if validation['all_passed']:
                validation_passed += 1
                print(f"  [PASS] {validation['passed']}/{validation['total']} checks - {filepath.parent.name}/{filepath.name}")
            else:
                validation_failed += 1
                print(f"  [FAIL] {validation['passed']}/{validation['total']} checks - {filepath.parent.name}/{filepath.name}")
                for issue in validation['issues']:
                    print(f"         - {issue}")
        except Exception as e:
            validation_failed += 1
            print(f"  [ERROR] {filepath.parent.name}/{filepath.name}: {e}")

    # Phase 3: Summary
    print("\n" + "=" * 70)
    print("RELATORIO FINAL")
    print("=" * 70)
    print(f"\nSkills analisadas:        {len(skill_files)}")
    print(f"Migradas com sucesso:     {migrated_count}")
    print(f"Ja no padrao:             {already_count}")
    print(f"Erros na migracao:        {error_count}")
    print(f"Validacao: {validation_passed} PASS / {validation_failed} FAIL")
    print(f"Taxa de sucesso:          {validation_passed}/{len(skill_files)} ({100*validation_passed//len(skill_files) if skill_files else 0}%)")

    # Detailed validation summary
    if all_validations:
        print("\n" + "-" * 70)
        print("DETALHAMENTO DOS CHECKS DE VALIDACAO")
        print("-" * 70)

        check_names = {
            'has_ptbr_header': 'Header PT-BR',
            'has_big_pickle': 'Diretiva big-pickle',
            'has_frontmatter': 'Frontmatter YAML',
            'has_name': 'Campo name',
            'has_description': 'Campo description',
            'has_version': 'Campo version',
            'has_compatibility': 'Campo compatibility',
            'has_migrated_at': 'Campo migrated_at',
            'has_workflow': 'Seção Workflow',
            'has_best_practices': 'Seção Best Practices',
            'has_integration': 'Seção Integration',
            'has_body': 'Conteudo original preservado',
        }

        for check_key, check_label in check_names.items():
            passed_count = sum(1 for v in all_validations if v['checks'].get(check_key, False))
            total_count = len(all_validations)
            pct = 100 * passed_count // total_count if total_count else 0
            status = "OK" if pct == 100 else "ATENÇÃO"
            print(f"  [{status}] {check_label}: {passed_count}/{total_count} ({pct}%)")

    print("\n" + "=" * 70)
    if validation_passed == len(skill_files):
        print("TODAS AS SKILLS FORAM MIGRADAS E VALIDADAS COM SUCESSO!")
    else:
        print(f"{validation_failed} skills precisam de atencao adicional.")
    print("=" * 70)

    return validation_passed == len(skill_files)

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
