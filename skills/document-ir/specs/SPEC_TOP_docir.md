# SPEC_TOP_docir — Document IR TDD Specification

**Skill:** document-ir  
**Source:** scripts/schema.py + composer.py + renderer.py  
**Framework:** pytest  
**Status:** Spec-Driven

---

## CT-1: test_init — Criacao de Block, Anchor e Document

**Objetivo:** Verificar que `Block`, `Anchor` e `Document` sao
instanciaveis com campos obrigatorios e `word_count` calculado.

**Passos:**
1. Criar `Block(type=HEADING1, content="Intro", position=0)`
2. Criar `Anchor(anchor_id="ref-1", target="#intro", block_type=HEADING1)`
3. Criar `Document(title="Teste", blocks, anchors, metadata, template)`
4. Verificar `doc.word_count > 0`

**Esperado:** Objetos criados com campos corretos.

---

## CT-2: test_compose — DocumentComposer com dedup e ordenacao

**Objetivo:** Confirmar que `DocumentComposer.compose()` ordena blocos
por `position` e gera `reference_index` no metadata.

**Passos:**
1. Criar blocos com posicoes [2, 1]
2. `composer.compose(blocks, anchors, title)`
3. Verificar `doc.blocks[0].position <= doc.blocks[1].position`
4. Verificar `"reference_index" in doc.metadata`

**Esperado:** Blocos ordenados, indice de referencias presente.

---

## CT-3: test_pipeline — DocumentPipeline com 7 estagios

**Objetivo:** Validar que `DocumentPipeline.run()` executa o pipeline
completo e `render_markdown()` produz saida legivel.

**Passos:**
1. Criar pipeline, definir 4 blocos
2. `pipeline.run(...)` → Document com titulo e metadata
3. `pipeline.render_markdown(doc)` → markdown contem conteudo dos blocos

**Esperado:** Pipeline completo funcional.

---

## CT-4: test_available — Validacao de schema e 16 BlockTypes

**Objetivo:** Garantir que `BlockType` tem 16 membros, `SCHEMA_REGISTRY`
tem 3 schemas, e `validate_block()` funciona para casos validos e invalidos.

**Passos:**
1. `len(BlockType) == 16`, `len(SCHEMA_REGISTRY) == 3`
2. `validate_block({"type":"paragraph","content":"x"})` → `(True, [])`
3. `validate_block({"type":"invalid","content":"x"})` → `(False, [...])`
4. `block_to_dict()` / `block_from_dict()` round-trip

**Esperado:** Validacao e serializacao funcionais.
