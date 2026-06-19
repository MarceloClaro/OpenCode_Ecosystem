const { OrchestrationEngine } = require('./engines/orchestration_engine');

async function testN35() {
  console.log('===============================================================');
  console.log('🤖 AGENTE ORQUESTRADOR UNIVERSAL (/marceloclaro)');
  console.log('===============================================================\n');
  
  const orchestrator = new OrchestrationEngine();
  
  // 1. Ativando N3.5+
  orchestrator.activateN3_5Safety();
  console.log('✅ Autonomia N3.5+ ativada com sucesso.');

  // 2. Testando a Barreira de Segurança
  console.log('\n🛡️ Testando Barreira de Prevenção (Safety Barrier)...');
  const dangerousTask = {
    skill: 'data_analysis',
    priority: 'doom', // priority que aciona o circuit breaker no _detectAnomalousStress
    payload: { risky: true }
  };
  
  const result = await orchestrator.dispatch(dangerousTask);
  console.log('Resultado do dispatch da tarefa perigosa:', result);

  // 3. Executando o Scanner Noológico/Potencialidade
  console.log('\n🔍 Executando Scanner de Correlações Latentes (SPEC-043)...');
  const report = await orchestrator.applyPotentialityScan();
  console.log(`✅ Scan concluído. ${report.novel_discoveries_found} descobertas validadas.`);

  console.log('\n📜 Últimos Eventos de Telemetria (Logs do N3.5+):');
  const diagnostics = orchestrator.getDiagnostics();
  diagnostics.recent_events.forEach(log => {
    if (log.type.startsWith('N3.5') || log.type.startsWith('SPEC-043')) {
      console.log(`[${log.timestamp}] [${log.type}] ${log.message}`);
    }
  });
}

testN35().catch(console.error);
