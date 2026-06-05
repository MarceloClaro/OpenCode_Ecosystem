### 1. Reproduzir
Confirme que consegue reproduzir o bug de forma confiável antes de tocar em qualquer código.
- Qual é o input ou sequência de ações que dispara o problema?
- O bug é determinístico ou intermitente?
- Se intermitente: qual é a taxa de ocorrência?

### 2. Localizar
Identifique a camada onde a falha ocorre:
- UI / frontend?
- Lógica de negócio / API?
- Banco de dados / query?
- Integração externa / rede?
- Build / tooling / ambiente?

### 3. Reduzir
Isole o caso mínimo que ainda reproduz o problema.
- Qual é o menor input que falha?
- Qual é o menor trecho de código envolvido?
- O problema existe em ambiente limpo (sem dados de estado anteriores)?

### 4. Corrigir
Corrija a **causa raiz**, não o sintoma.
- Se a correção precisar de mais de 20 linhas, questione se está atacando a causa certa
- Não faça refatorações adjacentes junto com o fix — escopo separado, commit separado
- Se descobrir outros bugs no caminho: registre como issue/TODO, não corrija agora

### 5. Guardar (regression coverage)
Adicione o menor teste que teria falhado antes do fix e passa agora.
- Testes unitários para lógica pura
- Testes de integração para boundary (DB, rede, I/O)
- O teste deve estar no mesmo commit do fix

### 6. Verificar
Confirme end-to-end para o report original:
- O comportamento esperado está correto?
- Os testes existentes continuam passando?
- O fix não introduz regressão?

---
