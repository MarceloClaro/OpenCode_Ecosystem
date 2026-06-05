### Modo 1  -  Edição direta em arquivo (container)

Quando o arquivo está disponível no filesystem (`/home/claude/`, `/mnt/user-data/`), usar a ferramenta nativa `str_replace`:

```
str_replace(
  path: "caminho/do/arquivo",
  old_str: "trecho exato a substituir",
  new_str: "trecho novo"
)
```

Neste modo, **não** formatar a entrega como bloco visual  -  a ferramenta já é cirúrgica por natureza. Apenas explicar brevemente o que mudou e por quê.
