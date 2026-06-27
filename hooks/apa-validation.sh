#!/usr/bin/env bash
# Hook: PostToolUse — Validação APA para documentos acadêmicos
# Recebe JSON via stdin: {"tool_name": "Write|Edit", "tool_input": {"file_path": "..."}}
# Verifica conformidade com normas APA 7ª edição

INPUT=$(cat)

TOOL=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('tool_name', ''))
except:
    print('')
" 2>/dev/null)

# Só roda após edições de arquivo
[[ "$TOOL" != "Write" && "$TOOL" != "Edit" ]] && exit 0

FILE=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    inp = d.get('tool_input', {})
    print(inp.get('file_path', '') or inp.get('new_file_path', ''))
except:
    print('')
" 2>/dev/null)

[[ -z "$FILE" || ! -f "$FILE" ]] && exit 0

# Verifica se é arquivo acadêmico
EXT="${FILE##*.}"
case "$EXT" in
    md|tex|txt|docx)
        # Verifica se contém indicadores de documento acadêmico
        if grep -q -E "(Introdução|Metodologia|Resultados|Discussão|Conclusões|Referências)" "$FILE" 2>/dev/null; then
            echo "[APA Hook] Documento acadêmico detectado: $FILE"
            
            # Verificações básicas de APA
            ISSUES=()
            
            # 1. Verifica se tem seção de Referências
            if ! grep -q -E "^#+\s*(Referências|References|Bibliografia)" "$FILE" 2>/dev/null; then
                ISSUES+=("Seção 'Referências' não encontrada")
            fi
            
            # 2. Verifica formatação de citações (padrão básico)
            if grep -q -E "\[[0-9]+\]" "$FILE" 2>/dev/null; then
                ISSUES+=("Possível uso de numeração em vez de citações APA")
            fi
            
            # 3. Verifica se tem DOI ou URLs
            if grep -q -E "https?://[^\s]+" "$FILE" 2>/dev/null; then
                echo "[APA Hook] URLs/DOIs encontrados - verificar formatação"
            fi
            
            # Relata problemas encontrados
            if [ ${#ISSUES[@]} -gt 0 ]; then
                echo "[APA Hook] Possíveis problemas de conformidade APA:"
                for issue in "${ISSUES[@]}"; do
                    echo "  - $issue"
                done
                echo "[APA Hook] Consulte: skills/apa-academic-writing/SKILL.md"
            else
                echo "[APA Hook] Nenhum problema óbvio de conformidade APA detectado"
            fi
        fi
        ;;
esac

exit 0