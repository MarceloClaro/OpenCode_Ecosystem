#!/usr/bin/env node
/**
 * OpenCode Social Impact - Orchestrator
 * Agent: marceloclaro
 * 
 * Run all impact measurement tools in sequence:
 * 1. Scanner SROI autônomo
 * 2. Research Writer
 * 3. Dashboard Generator
 */

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const IMPACT_DIR = __dirname;

function run(script, label) {
  console.log(`\n${'═'.repeat(60)}`);
  console.log(`▶  ${label}`);
  console.log('═'.repeat(60));
  try {
    const result = execSync(`node "${path.join(IMPACT_DIR, script)}"`, {
      encoding: 'utf8',
      cwd: IMPACT_DIR
    });
    console.log(result);
    return true;
  } catch(e) {
    console.error(`❌ Erro em ${label}:`, e.message);
    return false;
  }
}

async function main() {
  console.log('\n🚀 OPENCODE SOCIAL IMPACT SUITE');
  console.log('   Agent: marceloclaro | Ecosystem: OpenCode');
  console.log('   ' + new Date().toLocaleString('pt-BR'));
  console.log('═'.repeat(60));

  // Step 1: Run scanner
  const scanOk = run('sroi/scanner.js', '1/3 → Scanner SROI Autônomo');

  if (!scanOk) {
    console.log('⚠️  Scanner falhou. Verificar configuração.');
    process.exit(1);
  }

  // Step 2: Research writer
  run('research_writer.js', '2/3 → Research Writer (Artigo Científico)');

  // Step 3: Dashboard
  run('dashboard_generator.js', '3/3 → Dashboard HTML Interativo');

  // Final summary
  console.log('\n' + '═'.repeat(60));
  console.log('✅ SUITE DE IMPACTO SOCIAL CONCLUÍDA');
  console.log('═'.repeat(60));

  const outputs = {
    scan_report: path.join(IMPACT_DIR, 'reports', 'latest_impact_report.json'),
    research_paper: path.join(IMPACT_DIR, 'research', 'latest_research.md'),
    policy_brief: path.join(IMPACT_DIR, 'research', 'latest_policy_brief.md'),
    dashboard: path.join(IMPACT_DIR, 'dashboard', 'index.html'),
    research_index: path.join(IMPACT_DIR, 'research', 'INDEX.md')
  };

  console.log('\n📁 OUTPUTS GERADOS:');
  Object.entries(outputs).forEach(([key, p]) => {
    const exists = fs.existsSync(p);
    console.log(`  ${exists ? '✅' : '❌'} [${key}] ${p}`);
  });

  console.log('\n💡 Para abrir o dashboard:');
  console.log(`   start "${outputs.dashboard}"`);
  console.log('\n💡 Para ler o artigo de pesquisa:');
  console.log(`   type "${outputs.research_paper}"`);
}

main().catch(console.error);
