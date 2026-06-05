# Corretor Linguistico PT-BR (v2.0)

## Corretor Linguistico PT-BR (v2.0)

### Pipeline de Correcao Obrigatoria
```
Geracao de texto → [ptbr_corrector.py] → Validacao CJK → Correcao ortografica → Entrega
```

### Componentes
- **Script**: `criador-artigo/banca/ptbr_corrector.py`
- **Agente**: `agents/linguistic-corrector.md`
- **Detecção**: 17 blocos Unicode CJK (chines, japones, coreano, pontuacao)
- **Correcao**: Ortografia, acentuacao, concordancia, espacos, aspas

### Quando Executar
1. **ANTES de toda entrega ao usuario** — NAO NEGOCIÁVEL
2. Ao gerar artigos, relatorios, documentos .md
3. Sempre que contexto chines foi carregado
4. Ao escrever qualquer arquivo no diretorio documentos/

### Comandos
```bash