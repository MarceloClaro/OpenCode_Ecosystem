# RELATORIO DE VALIDACAO — Ollama + OpenCode Ecosystem
## LLM Local (qwen2.5-coder:7b) como Verificador Auxiliar

**Data:** 27/05/2026 | **Modelo:** qwen2.5-coder:7b (7B params, 4.7GB) | **Hardware:** CPU-only, 8GB RAM

---

## Teste Real — Formula de Cartan (DCA Lista 1, Problema 1)

### Prompt submetido

> "Use Cartans formula to prove L_{X_H} omega = 0 for Hamiltonian field
> i_{X_H} omega = -dH. Show steps: 1) Cartan formula, 2) d(omega)=0 since
> symplectic, 3) i_{X_H} omega = -dH, 4) d^2 = 0. Conclude."

### Resposta do Ollama (qwen2.5-coder:7b)

O modelo produziu uma demonstracao completa de 4 passos:

1. **Formula de Cartan:** $L_X \alpha = d(i_X \alpha) + i_X(d\alpha)$
2. **Forma simpletica:** $d\omega = 0$ (fechada por definicao)
3. **Campo Hamiltoniano:** $i_{X_H}\omega = -dH$ (definicao)
4. **Conclusao:** $L_{X_H}\omega = d(-dH) + i_{X_H}(0) = -d^2 H = 0$ ✓

### Avaliacao

| Criterio | Resultado |
|----------|:---:|
| Corretude matematica | ✅ 100% |
| Estrutura logica (4 passos) | ✅ Completa |
| Uso correto de Cartan | ✅ |
| Uso correto de $d^2 = 0$ | ✅ |
| Tempo de resposta | ~120s (CPU) |

---

## Status da Integracao

| Componente | Status |
|-----------|:------:|
| Ollama instalado | ✅ v0.9+ |
| Modelo disponivel | ✅ qwen2.5-coder:7b (4.7GB) |
| API funcional (localhost:11434) | ✅ Respondendo |
| Raciocinio matematico | ✅ Funcional (basico/intermediario) |
| Integracao OpenCode | 🟡 Bridge pronto (`ollama_validate.py`) |

## Recomendacoes

| Cenario | Modelo | RAM |
|---------|--------|:---:|
| 8GB RAM, rapido | phi3:mini (3.8B, 2.2GB) | ✅ |
| 8GB RAM, matematico | qwen2.5-coder:7b (4.7GB) | ⚠️ Lento |
| 16GB+ RAM, qualidade | mistral:7b / llama3.1:8b | ✅ |

## Para ativar no OpenCode

```json
// opencode.json
"mcpServers": {
  "ollama-local": {
    "command": "python",
    "args": ["skills/reasoning-orchestrator-v11/agents/ollama_validate.py"]
  }
}
```

*Validacao executada com dados REAIS — nao simulada — 27/05/2026*
