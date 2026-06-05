# =============================================================================
# SMOKE CHECK — Harness Engineering para dissertacao OpenCode
# Executa verificacoes deterministicas em <30s.
# Falha = agente NAO pode prosseguir.
# =============================================================================
$ErrorActionPreference = "Stop"
$TEX = "dissertacao_opencode_final.tex"
$PASS = 0; $FAIL = 0

function Check($name, $script) {
    Write-Host -NoNewline "[...] $name "
    $oldEAP = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        & $script *>$null
        if ($LASTEXITCODE -ne 0 -and $LASTEXITCODE -ne $null) {
            throw "Exit code: $LASTEXITCODE"
        }
        Write-Host "`r[OK]  $name" -ForegroundColor Green
        $global:PASS++
    } catch {
        Write-Host "`r[FAIL] $name" -ForegroundColor Red
        Write-Host "       $_" -ForegroundColor DarkYellow
        $global:FAIL++
    } finally {
        $ErrorActionPreference = $oldEAP
    }
}

Write-Host "`n===== SMOKE CHECK: dissertacao_opencode_final =====" -ForegroundColor Cyan
Write-Host ""

# 1. Compilacao rapida
Check "Compilacao LaTeX" {
    $result = cmd /c "pdflatex -interaction=nonstopmode $TEX" 2>&1 | Out-String
    if ($result -match "Fatal error") {
        throw "Compilacao falhou. Verifique o log."
    }
}

# 2. Zero overfull hboxes (margens)
Check "Zero overfull hboxes" {
    $over = Select-String -Path "dissertacao_opencode_final.log" -Pattern "Overfull" -Quiet
    if ($over) { throw "Ha overfull hboxes. Execute: Select-String -Path dissertacao_opencode_final.log -Pattern 'Overfull'" }
}

# 3. Referencias sem citacao indefinida
Check "Referencias resolvidas" {
    $undef = Select-String -Path "dissertacao_opencode_final.log" -Pattern "Citation.*undefined" -Quiet
    if ($undef) { throw "Ha citacoes indefinidas. Execute bibtex e recompile." }
}

# 4. Cross-references resolvidas
Check "Cross-references" {
    $undef = Select-String -Path "dissertacao_opencode_final.log" -Pattern "Reference.*undefined" -Quiet
    if ($undef) { throw "Ha referencias cruzadas nao resolvidas." }
}

# 5. DOI consistency (todo .bib entry deve ter doi ou url)
Check "DOIs no .bib" {
    $bib = Get-Content "dissertacao_opencode_referencias.bib" -Raw
    $entries = ($bib | Select-String "@" -AllMatches).Matches.Count
    $withDOI = ($bib | Select-String "doi\s*=" -AllMatches).Matches.Count
    if ($withDOI -lt $entries * 0.8) {
        throw "Apenas $withDOI/$entries entradas tem DOI (<80%). Auditoria necessaria."
    }
}

# 6. TSAC check — palavras banidas
Check "TSAC (87 palavras banidas)" {
    $banned = @("crucial", "essencialmente", "notavelmente", "fundamentalmente",
                 "intrinsecamente", "profundamente", "verdadeiramente",
                 "nao apenas.+mas tambem", "paisagem atual")
    $tex = Get-Content $TEX -Raw
    $found = @()
    foreach ($w in $banned) {
        if ($tex -match $w) { $found += $w }
    }
    if ($found.Count -gt 0) {
        throw "Palavras banidas encontradas: $($found -join ', ')"
    }
}

# 7. Arquivo PDF existe e tem tamanho minimo
Check "Arquivo PDF" {
    $pdf = "dissertacao_opencode_final.pdf"
    if (-not (Test-Path $pdf)) { throw "$pdf nao encontrado" }
    $size = (Get-Item $pdf).Length
    if ($size -lt 100KB) { throw "$pdf muito pequeno ($size bytes)" }
}

Write-Host ""
Write-Host "===== RESULTADO: $PASS pass, $FAIL fail =====" -ForegroundColor $(if ($FAIL -eq 0) { "Green" } else { "Red" })

if ($FAIL -gt 0) {
    Write-Host "SMOKE CHECK FALHOU — corrija antes de prosseguir." -ForegroundColor Red
    exit 1
} else {
    Write-Host "SMOKE CHECK APROVADO — prosseguir." -ForegroundColor Green
    exit 0
}
