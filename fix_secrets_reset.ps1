# ============================================================
# fix_secrets_reset.ps1
# Estrategia: squash de todo o historico em 1 commit limpo
# (mais rapido e confiavel no Windows do que filter-branch)
# ============================================================

param(
    [string]$RepoPath = "C:\Users\marce\.config\opencode"
)

$secretKey   = "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"
$placeholder = "GROQ_API_KEY_REMOVIDO_USE_VARIAVEL_DE_AMBIENTE"

Set-Location $RepoPath

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  LIMPEZA DE SEGREDOS — Repositorio OpenCode Ecosystem          " -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

# ----------------------------------------------------------
# ETAPA 1 — Substituir o segredo nos arquivos do working tree
# ----------------------------------------------------------
Write-Host "`n[1/4] Substituindo chave Groq em arquivos de trabalho..." -ForegroundColor Yellow

$exts  = @(".md", ".txt", ".json", ".py", ".ts", ".js", ".yaml", ".yml", ".toml", ".rst")
$files = Get-ChildItem -Path $RepoPath -Recurse -File | Where-Object {
    $exts -contains $_.Extension -and
    $_.FullName -notmatch [regex]::Escape("\.git\")
}

$cleaned = 0
foreach ($f in $files) {
    try {
        $raw = [System.IO.File]::ReadAllText($f.FullName)
        if ($raw.Contains($secretKey)) {
            $fixed = $raw.Replace($secretKey, $placeholder)
            [System.IO.File]::WriteAllText($f.FullName, $fixed, [System.Text.Encoding]::UTF8)
            Write-Host "   OK  $($f.FullName.Replace($RepoPath,''))" -ForegroundColor Green
            $cleaned++
        }
    } catch {
        Write-Host "   ERR $($f.FullName): $_" -ForegroundColor Red
    }
}
Write-Host "  -> $cleaned arquivo(s) limpo(s)." -ForegroundColor Cyan

# Verificacao final
$remaining = (Get-ChildItem -Path $RepoPath -Recurse -File |
    Where-Object { $exts -contains $_.Extension -and $_.FullName -notmatch '\\\.git\\' } |
    ForEach-Object { [System.IO.File]::ReadAllText($_.FullName) } |
    Where-Object { $_.Contains($secretKey) }).Count

if ($remaining -gt 0) {
    Write-Host "  AVISO: Ainda existem $remaining arquivo(s) com o segredo!" -ForegroundColor Red
    exit 1
}
Write-Host "  Verificacao OK — nenhum segredo restante nos arquivos." -ForegroundColor Green

# ----------------------------------------------------------
# ETAPA 2 — Criar orfao (historico limpo de 1 commit)
# ----------------------------------------------------------
Write-Host "`n[2/4] Criando branch orfao com historico limpo..." -ForegroundColor Yellow

git checkout --orphan master-clean
if ($LASTEXITCODE -ne 0) { Write-Host "ERRO no checkout orphan" -ForegroundColor Red; exit 1 }

git add -A
if ($LASTEXITCODE -ne 0) { Write-Host "ERRO no git add" -ForegroundColor Red; exit 1 }

git commit -m "chore: commit inicial limpo — segredos removidos do historico"
if ($LASTEXITCODE -ne 0) { Write-Host "ERRO no git commit" -ForegroundColor Red; exit 1 }

Write-Host "  Branch orfao criado com sucesso." -ForegroundColor Green

# ----------------------------------------------------------
# ETAPA 3 — Substituir master pelo branch limpo
# ----------------------------------------------------------
Write-Host "`n[3/4] Substituindo branch master pelo historico limpo..." -ForegroundColor Yellow

git branch -D master
git branch -m master-clean master

Write-Host "  Branch master substituido." -ForegroundColor Green

# ----------------------------------------------------------
# ETAPA 4 — Limpar GC
# ----------------------------------------------------------
Write-Host "`n[4/4] Executando garbage collection..." -ForegroundColor Yellow
git reflog expire --expire=now --all
git gc --prune=now --aggressive

Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "  CONCLUIDO COM SUCESSO!                                        " -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Proximo passo — faca o push forcado:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  git push --force origin master" -ForegroundColor White
Write-Host ""
Write-Host "LEMBRETE: Revogue a chave Groq exposta em:" -ForegroundColor Red
Write-Host "  https://console.groq.com/keys" -ForegroundColor Red
Write-Host ""
