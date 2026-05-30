# Entity Filtering Logic

## Regra de Filtragem

Uma entidade é considerada **significativa** se suas labels incluirem
algo além de "Entity" e "Node":

```python
custom_labels = [la for la in labels if la not in ("Entity", "Node")]
if custom_labels:
    # Entidade com tipo significativo
    entity_type = custom_labels[0]
```

## Exemplos

| Labels | Significativa? | Tipo |
|--------|---------------|------|
| `["Entity"]` | ❌ Não | — |
| `["Person", "Student"]` | ✅ Sim | Student |
| `["Organization", "University"]` | ✅ Sim | University |
| `["Entity", "Node"]` | ❌ Não | — |
| `["Topic"]` | ✅ Sim | Topic |

## Performance

- `filter_defined_entities()` carrega **todos** os nós (O(n)) e filtra
- `get_entity_with_context()` carrega apenas o nó alvo (O(1)) e suas arestas (O(degree))
- `get_entities_by_type()` reusa `filter_defined_entities()` com pré-filtro
