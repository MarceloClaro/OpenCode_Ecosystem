# Boas Práticas de Testes para Computação Quântica

Este guia adapta a taxonomia IBM do `projeto_tests_kit` para o domínio quântico.

## Pirâmide de Testes Quânticos

1.  **Testes de Unidade (Base)**:
    -   Valide portas lógicas isoladas e pequenos sub-circuitos.
    -   Verifique estados conhecidos (ex: Bell, GHZ) usando simuladores ideais.
    -   Use `unittest` ou `pytest` para automatizar as asserções.

2.  **Testes de Integração**:
    -   Valide a interface entre o pré-processamento clássico e o circuito quântico.
    -   Garanta que a codificação de dados (ex: Amplitude Encoding) não perca informações críticas.
    -   Verifique o fluxo de gradientes em modelos híbridos (ex: PennyLane + TensorFlow).

3.  **Testes de Sistema (End-to-End)**:
    -   Execute o pipeline completo: Dados Reais -> QML -> Classificação.
    -   Valide a robustez contra ruído usando simuladores ruidosos (Noisy Simulation).

4.  **Teste de Fumaça (Smoke Test)**:
    -   Antes de uma simulação longa ou execução em hardware real, execute uma versão simplificada (menos qubits/shots) para garantir que o ambiente está configurado corretamente.

## Critérios de Aceite (DoD)
-   O circuito deve ser transpilado sem erros para a topologia alvo.
-   A fidelidade do estado final deve estar acima de um limiar definido em simuladores ideais.
-   O tempo de execução não deve exceder os limites de tempo de fila do hardware real.
