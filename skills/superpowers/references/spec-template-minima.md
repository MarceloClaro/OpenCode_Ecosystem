<!-- SAIDA OBRIGATORIA: PORTUGUES BRASILEIRO FORMAL -->
<!-- Inspirado por: Engenharia de Software com Agentes Inteligentes (Sandeco, 2026), Cap. 6 -->

# Template de Spec Minima (SDD)

> "O agente implementa o que foi especificado. Se a spec estava errada, o agente implementa o erro com eficiencia impecavel." — Cap. 6

Toda instrucao a um agente inteligente deve conter, no minimo, estas 5 dimensoes:

## 1. Comportamento Esperado

```
O que o sistema deve fazer?
- Funcionalidade principal: [descreva em 1-2 frases]
- Fluxo feliz: [passo 1] → [passo 2] → [resultado]
- O que NAO deve fazer: [comportamentos explicitamente excluidos]
```

## 2. Usuarios e Contexto

```
Quem vai usar e em que condicoes?
- Perfil de usuario: [admin | cliente | sistema externo | publico]
- Volume esperado: [N usuarios simultaneos | N requisicoes/dia]
- Ambiente: [web | mobile | CLI | API | embarcado]
- Dados: [estrutura, volume, sensibilidade]
```

## 3. Restricoes

```
Quais os limites obrigatorios?
- Seguranca: [autenticacao | autorizacao | criptografia | sanitizacao]
- Performance: [tempo maximo de resposta | throughput minimo]
- Escala: [limite de armazenamento | taxa de crescimento]
- Compatibilidade: [versoes de dependencias | navegadores | SO]
- Regulatorio: [LGPD | PCI | SOX | normas setoriais]
```

## 4. Casos de Borda

```
O que acontece quando algo sai do esperado?
- Entrada invalida: [o que o sistema deve retornar]
- Timeout: [comportamento apos X segundos sem resposta]
- Dependencia indisponivel: [fallback ou degradacao graciosa]
- Concorrencia: [dois usuarios modificando o mesmo recurso]
- Dados ausentes: [o que fazer quando o recurso nao existe]
```

## 5. Criterios de Aceitacao

```
Como verificar que a spec foi atendida?
- [ ] Criterio 1: [descricao verificavel]
- [ ] Criterio 2: [descricao verificavel]
- [ ] Criterio 3: [descricao verificavel]
- [ ] Teste automatizado cobre cada criterio? [sim/nao]
```

## Exemplo Preenchido: Endpoint de Upload

```
1. Comportamento:
   - Aceitar upload de arquivo via POST /upload
   - Retornar URL do arquivo e metadata
   - NAO aceitar arquivos > 10MB
   - NAO aceitar extensoes nao permitidas (.exe, .sh, .bat)

2. Usuarios:
   - Clientes autenticados (JWT)
   - Ate 100 uploads simultaneos
   - Arquivos armazenados em S3-compatible

3. Restricoes:
   - Autenticacao obrigatoria (401 sem token)
   - Limite 10MB por arquivo (413 se exceder)
   - Sanitizar nome do arquivo (remover ../ e caracteres especiais)
   - Content-Type validado contra lista branca

4. Bordas:
   - Arquivo vazio: rejeitar com 400
   - Token expirado: retornar 401
   - Storage indisponivel: retornar 503, nao perder o arquivo
   - Nome duplicado: adicionar suffixo unico, nao sobrescrever

5. Criterios:
   - [ ] Upload de PNG 2MB → 201 + URL
   - [ ] Upload sem token → 401
   - [ ] Upload 15MB → 413
   - [ ] Upload .exe → 400
   - [ ] Storage offline → 503, arquivo preservado em buffer
```
