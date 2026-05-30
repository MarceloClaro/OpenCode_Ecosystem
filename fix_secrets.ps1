# ============================================================
# fix_secrets.ps1 — Remove chaves Groq de todos os arquivos
# e reescreve o histórico git para que o push seja aceito.
# ============================================================

$repoPath   = "C:\Users\marce\.config\opencode"
$secretKey  = "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"
$placeholder = "GROQ_API_KEY_REMOVIDO_USE_VARIAVEL_DE_AMBIENTE"

Set-Location $repoPath

Write-Host "=== ETAPA 1: Substituindo chave em arquivos de trabalho ===" -ForegroundColor Cyan

# Busca recursiva em todos os arquivos de texto
$files = Get-ChildItem -Recurse -File | Where-Object {
    $_.Extension -in @(".md", ".txt", ".json", ".py", ".ts", ".js", ".yaml", ".yml", ".toml") -and
    $_.FullName -notmatch "\\.git\\"
}

$count = 0
foreach ($file in $files) {
    $content = Get-Content -Path $file.FullName -Raw -ErrorAction SilentlyContinue
    if ($content -and $content.Contains($secretKey)) {
        $newContent = $content.Replace($secretKey, $placeholder)
        Set-Content -Path $file.FullName -Value $newContent -NoNewline
        Write-Host "  [LIMPO] $($file.FullName)" -ForegroundColor Green
        $count++
    }
}

Write-Host "`n  Total de arquivos limpos: $count" -ForegroundColor Yellow

Write-Host "`n=== ETAPA 2: Commitando arquivos limpos ===" -ForegroundColor Cyan
git -C $repoPath add -A
git -C $repoPath commit -m "security: remove chaves Groq API — substituidas por placeholder de variavel de ambiente"

Write-Host "`n=== ETAPA 3: Reescrevendo historico com git filter-branch ===" -ForegroundColor Cyan
Write-Host "  Isso pode demorar alguns minutos..." -ForegroundColor Yellow

# Reescreve todos os commits substituindo o segredo
$env:FILTER_BRANCH_SQUELCH_WARNING = 1

git -C $repoPath filter-branch --force --tree-filter `
    "powershell -Command `"Get-ChildItem -Recurse -File | Where-Object { \`$_.Extension -in @('.md','.txt','.json','.py','.ts','.js','.yaml','.yml','.toml') -and \`$_.FullName -notmatch '\.git\\\\' } | ForEach-Object { \`$c = Get-Content \`$_.FullName -Raw -ErrorAction SilentlyContinue; if (\`$c -and \`$c.Contains('$secretKey')) { Set-Content \`$_.FullName (\`$c.Replace('$secretKey', '$placeholder')) -NoNewline } }`"" `
    --tag-name-filter cat -- --all

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n  Historico reescrito com sucesso!" -ForegroundColor Green
} else {
    Write-Host "`n  AVISO: filter-branch retornou codigo $LASTEXITCODE. Verificar manualmente." -ForegroundColor Red
}

Write-Host "`n=== ETAPA 4: Limpando refs antigas ===" -ForegroundColor Cyan
git -C $repoPath for-each-ref --format="delete %(refname)" refs/original/ | git -C $repoPath update-ref --stdin
git -C $repoPath reflog expire --expire=now --all
git -C $repoPath gc --prune=now --aggressive

Write-Host "`n=== CONCLUIDO ===" -ForegroundColor Green
Write-Host "Agora execute:" -ForegroundColor Yellow
Write-Host "  git push --force-with-lease origin master" -ForegroundColor White
