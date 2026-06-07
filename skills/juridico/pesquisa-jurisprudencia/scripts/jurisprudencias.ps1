#Requires -Version 5.1

<#
.SYNOPSIS
  Cliente PowerShell para a API Jurisprudencias.ai com cache local.
.DESCRIPTION
  Fornece funcoes para buscar decisoes judiciais, consultar tribunais
  e resolver processos, com cache JSON para evitar o rate limit de 5 buscas/dia.
#>

$Script:CacheDir     = if ($env:JURISPRUDENCIAS_CACHE_DIR) { $env:JURISPRUDENCIAS_CACHE_DIR } else { "$env:USERPROFILE\.jurisprudencias\cache" }
$Script:CacheTTLHours = if ($env:JURISPRUDENCIAS_CACHE_TTL) { [int]$env:JURISPRUDENCIAS_CACHE_TTL } else { 24 }
$Script:ApiBaseUrl   = "https://jurisprudencias.ai/api/v1"

$Script:Token = $env:JURISPRUDENCIAS_API_TOKEN
if (-not $Script:Token) {
    Write-Warning "Variavel JURISPRUDENCIAS_API_TOKEN nao definida"
    Write-Warning "Configure com: `$env:JURISPRUDENCIAS_API_TOKEN = 'jur_...'"
}

function _remove-diacritics($s) {
    $normalized = $s.Normalize([System.text.NormalizationForm]::FormD)
    return [Text.RegularExpressions.Regex]::Replace($normalized, '\p{M}', '')
}

function _ensure-cache-dir {
    if (-not (Test-Path $Script:CacheDir)) {
        $null = New-Item -ItemType Directory -Path $Script:CacheDir -Force
    }
}

function _cache-path($key) {
    $bytes    = [text.encoding]::UTF8.GetBytes($key)
    $hashAlgo = [Security.Cryptography.SHA256]::Create()
    $hashBytes = $hashAlgo.ComputeHash($bytes)
    $hash     = [System.BitConverter]::ToString($hashBytes) -replace '-', ''
    return Join-Path $Script:CacheDir "$hash.json"
}

function _cache-get($key) {
    _ensure-cache-dir
    $path = _cache-path $key
    if (-not (Test-Path $path)) { return $null }
    try {
        $o = Get-Content -Raw -Encoding UTF8 -LiteralPath $path | ConvertFrom-Json
        $age = [datetime]::Now - [datetime]::Parse($o._cached_at)
        if ($age.TotalHours -gt $Script:CacheTTLHours) {
            Remove-Item -LiteralPath $path -Force
            return $null
        }
        return $o.data
    } catch { return $null }
}

function _cache-set($key, $data) {
    _ensure-cache-dir
    $path = _cache-path $key
    $o = [PSCustomObject]@{ _cached_at = [datetime]::Now.ToString('o'); data = $data }
    $o | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $path -Encoding UTF8
}

function _api-get($url) {
    $token = $Script:Token
    if (-not $token) { throw "Token nao disponivel. Defina JURISPRUDENCIAS_API_TOKEN" }
    try {
        $output = & "curl.exe" -s -w "%{http_code}" -H "Authorization: Bearer $token" $url 2>&1
        $combined = $output -join "`n"
        $code = $combined.Substring($combined.Length - 3)
        $body = $combined.Substring(0, $combined.Length - 3)
        if ($code -eq "429") {
            Write-Warning "Rate limit excedido (429). Use cache ou aguarde reset a meia-noite."
            return $null
        }
        if ($code -eq "404") { return $null }
        if ($code -ne "200") {
            Write-Warning "HTTP $code -- $url"
            return $null
        }
        $trimmed = $body.Trim()
        if (-not $trimmed) { return @() }
        $parsed = $trimmed | ConvertFrom-Json
        if ($parsed.PSObject.Properties.Name -contains "data") { return $parsed.data }
        return $parsed
    } catch {
        Write-Warning "Erro na requisicao: $_"
        return $null
    }
}

function Get-JurCourts {
    $url = "$($Script:ApiBaseUrl)/courts"
    $data = _api-get $url
    if (-not $data) { return }
    $data | ForEach-Object {
        [PSCustomObject]@{ Slug = $_.id; Nome = $_.name; Decisoes = $_.decisions_count }
    }
}

function Search-JurDecisions {
    param(
        [Parameter(Mandatory)] [string] $Court,
        [Parameter(Mandatory)] [string] $Query,
        [int]    $Page = 0,
        [string] $PubFrom,
        [string] $PubTo,
        [string] $TrialFrom,
        [string] $TrialTo,
        [switch] $Force,
        [switch] $NoCache
    )
    $eq = [uri]::EscapeDataString($Query)
    $url = "{0}/courts/{1}/decisions?q={2}" -f $Script:ApiBaseUrl, $Court, $eq
    $url = "{0}{1}page={2}" -f $url, "&", $Page
    if ($PubFrom)  { $url = "{0}{1}pub_from={2}" -f $url, "&", $PubFrom }
    if ($PubTo)    { $url = "{0}{1}pub_to={2}" -f $url, "&", $PubTo }
    if ($TrialFrom) { $url = "{0}{1}trial_from={2}" -f $url, "&", $TrialFrom }
    if ($TrialTo)  { $url = "{0}{1}trial_to={2}" -f $url, "&", $TrialTo }

    $ck = "{0}|{1}|p={2}|pub={3}-{4}|tri={5}-{6}" -f $Court, $Query, $Page, $PubFrom, $PubTo, $TrialFrom, $TrialTo

    if (-not $Force -and -not $NoCache) {
        $cached = _cache-get $ck
        if ($cached) { Write-Host "[cache]" -NoNewline -ForegroundColor DarkGray; return $cached }
    }
    $data = _api-get $url
    if ($null -eq $data) { return }
    if (-not $NoCache -and $data) { _cache-set $ck $data }
    return $data
}

function Get-JurDecision {
    param(
        [Parameter(Mandatory)] [string] $Court,
        [Parameter(Mandatory)] [string] $Number
    )
    $en = [uri]::EscapeDataString($Number)
    $url = "{0}/courts/{1}/decisions/lookup?n={2}" -f $Script:ApiBaseUrl, $Court, $en
    $data = _api-get $url
    if (-not $data) { return }
    [PSCustomObject]@{
        Processo = $data.process_number
        Ementa   = $data.summary
        URL      = $data.url
        Tribunal = $data.court
    }
}

function Clear-JurCache {
    param([int] $OlderThanHours = 0)
    _ensure-cache-dir
    $files = Get-ChildItem "$($Script:CacheDir)\*.json" -ErrorAction SilentlyContinue
    if (-not $files) { Write-Host "Cache vazio."; return }
    $removed = 0
    $files | ForEach-Object {
        if ($OlderThanHours -gt 0) {
            $age = ([datetime]::Now - $_.LastWriteTime).TotalHours
            if ($age -ge $OlderThanHours) { Remove-Item $_.FullName -Force; $removed++ }
        } else { Remove-Item $_.FullName -Force; $removed++ }
    }
    Write-Host "Cache limpo. Removidos $removed arquivos." -ForegroundColor Green
}

function Get-JurCacheStatus {
    _ensure-cache-dir
    $files = Get-ChildItem "$($Script:CacheDir)\*.json" -ErrorAction SilentlyContinue
    if (-not $files) { Write-Host "Cache vazio."; return }
    $total = @($files).Count
    $size  = ($files | Measure-Object Length -Sum).Sum
    $now   = [datetime]::Now
    $expiredCount = 0
    $files | ForEach-Object {
        $age = ($now - $_.LastWriteTime).TotalHours
        if ($age -gt $Script:CacheTTLHours) { $expiredCount++ }
        $shortName = $_.Name.Substring(0, [Math]::Min(16, $_.Name.Length)) + ".."
        [PSCustomObject]@{
            Arquivo = $shortName
            IdadeH  = [math]::Round($age, 1)
            Status  = if ($age -gt $Script:CacheTTLHours) { "expirado" } else { "valido" }
            Tamanho = "{0:N1}KB" -f ($_.Length / 1KB)
        }
    } | Sort-Object IdadeH -Descending | Format-Table -AutoSize
    $msg = "Total: {0} itens, {1:N1}KB, {2} expirados (TTL={3}h)" -f $total, ($size/1KB), $expiredCount, $Script:CacheTTLHours
    Write-Host $msg -ForegroundColor Cyan
}

function Search-JurCache {
    param(
        [Parameter(Mandatory)] [string] $Term,
        [string] $Court,
        [switch] $SimpleOutput
    )
    _ensure-cache-dir
    $files = Get-ChildItem "$($Script:CacheDir)\*.json" -ErrorAction SilentlyContinue
    if (-not $files) { Write-Host "Cache vazio. Nada para buscar."; return }

    $results = [System.Collections.ArrayList]@()
    $termNorm = _remove-diacritics $Term.ToLower()

    foreach ($f in $files) {
        try {
            $o = Get-Content -Raw -Encoding UTF8 -LiteralPath $f.FullName | ConvertFrom-Json
            $entries = $o.data
            if (-not $entries) { continue }
            if ($entries -isnot [array]) { $entries = @($entries) }
            foreach ($entry in $entries) {
                $courtMatch = (-not $Court) -or ($entry.court -eq $Court) -or ($entry.court_slug -eq $Court)
                if (-not $courtMatch) { continue }

                $haystackParts = @(
                    $entry.excerpt; $entry.process_number; $entry.summary
                    $entry.process_type; $entry.rapporteur
                ) | Where-Object { $_ } | ForEach-Object { _remove-diacritics $_.ToLower() }
                $haystack = $haystackParts -join " "
                if ($haystack -match [regex]::Escape($termNorm)) {
                    $null = $results.Add([PSCustomObject]@{
                        Processo = $entry.process_number
                        Tribunal = $entry.court
                        DataPublicacao = $entry.publication_date
                        DataJulgamento = $entry.trial_date
                        Relator  = $entry.rapporteur
                        Ementa   = if ($entry.excerpt) { ($entry.excerpt -replace '\s+', ' ').Substring(0, [Math]::Min(200, $entry.excerpt.Length)) + "..." } else { "" }
                        URL      = $entry.url
                    })
                }
            }
        } catch { continue }
    }
    if ($results.Count -eq 0) { Write-Host "Nenhum resultado offline para '$Term'."; return }
    if ($SimpleOutput) {
        $results | Select-Object Processo, DataPublicacao | Format-Table -AutoSize
    } else {
        $results | Format-Table -Property Processo, Tribunal, DataPublicacao, Ementa -AutoSize -Wrap
    }
    Write-Host "($($results.Count) resultados offline)" -ForegroundColor Cyan
}

function Export-JurDocs {
    param(
        [string] $OutputPath = ".\jurisprudencias_offline.html",
        [string] $Court,
        [switch] $Open
    )
    _ensure-cache-dir
    $files = Get-ChildItem "$($Script:CacheDir)\*.json" -ErrorAction SilentlyContinue
    if (-not $files) { Write-Host "Cache vazio."; return }

    $allDecisions = [System.Collections.ArrayList]@()
    foreach ($f in $files) {
        try {
            $o = Get-Content -Raw -Encoding UTF8 -LiteralPath $f.FullName | ConvertFrom-Json
            $entries = $o.data
            if (-not $entries -or ($entries -isnot [array])) { continue }
            foreach ($entry in $entries) {
                if ($Court -and $entry.court -ne $Court) { continue }
                $null = $allDecisions.Add($entry)
            }
        } catch { continue }
    }
    if ($allDecisions.Count -eq 0) { Write-Host "Nenhuma decisao no cache para exportar."; return }

    $count = $allDecisions.Count
    $rows = $allDecisions | Sort-Object publication_date -Descending | ForEach-Object {
        $num = $_.process_number; $date = $_.publication_date; $trial = $_.trial_date
        $court = $_.court; $rel = $_.rapporteur; $body = $_.excerpt; $url = $_.url
        $title = if ($num) { $num } else { "(sem numero)" }
        $meta = @()
        if ($court) { $meta += "Tribunal: $court" }
        if ($date)  { $meta += "Publicacao: $date" }
        if ($trial) { $meta += "Julgamento: $trial" }
        if ($rel)   { $meta += "Relator: $rel" }
        $metaStr = $meta -join " &middot; "
        $bodyHtml = if ($body) {
            $escaped = [System.Net.WebUtility]::HtmlEncode(($body -replace '\s+', ' ').Trim())
            "<p>$escaped</p>"
        } else { "" }
        $urlHtml = if ($url) { "<a href=`"$([System.Net.WebUtility]::HtmlEncode($url))`" target=`"_blank`">$([System.Net.WebUtility]::HtmlEncode($url))</a>" } else { "" }
@"
<div class="card"><div class="card-title"><a href="#$([System.Net.WebUtility]::HtmlEncode($num))">$([System.Net.WebUtility]::HtmlEncode($title))</a></div><div class="card-meta">$metaStr</div>$bodyHtml<div class="card-url">$urlHtml</div></div>
"@
    }

    $html = @"
<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Jurisprudencias - Offline</title>
<style>*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',system-ui,sans-serif;background:#f5f5f5;color:#222;line-height:1.6;padding:2rem}
.container{max-width:960px;margin:0 auto}
h1{font-size:1.75rem;font-weight:600;margin-bottom:0.25rem}
.subtitle{color:#666;font-size:0.9rem;margin-bottom:2rem}
.stats{display:flex;gap:1rem;margin-bottom:2rem;flex-wrap:wrap}
.stat{background:#fff;border-radius:8px;padding:1rem 1.25rem;box-shadow:0 1px 3px rgba(0,0,0,0.08);flex:1;min-width:120px}
.stat-num{font-size:1.5rem;font-weight:700;color:#1a56db}
.stat-label{font-size:0.8rem;color:#666;text-transform:uppercase;letter-spacing:0.05em}
.card{background:#fff;border-radius:8px;padding:1.25rem;margin-bottom:1rem;box-shadow:0 1px 3px rgba(0,0,0,0.08)}
.card-title{font-weight:600;margin-bottom:0.35rem}
.card-title a{color:#1a56db;text-decoration:none}
.card-meta{font-size:0.82rem;color:#888;margin-bottom:0.75rem}
.card p{font-size:0.92rem;color:#444;text-align:justify}
.card-url{margin-top:0.5rem;font-size:0.82rem;word-break:break-all}
.search-box{margin-bottom:1.5rem}
.search-box input{width:100%;padding:0.65rem 1rem;border:1px solid #d0d0d0;border-radius:8px;font-size:1rem}
.search-box input:focus{outline:none;border-color:#1a56db;box-shadow:0 0 0 3px rgba(26,86,219,0.15)}
.footer{text-align:center;color:#999;font-size:0.8rem;margin-top:2rem;padding-top:1rem;border-top:1px solid #e0e0e0}
</style></head><body><div class="container">
<h1>Jurisprudencias &mdash; Documentacao Offline</h1>
<p class="subtitle">Gerado em $(Get-Date -Format "dd/MM/yyyy HH:mm") &middot; Cache local</p>
<div class="stats">
<div class="stat"><div class="stat-num">$count</div><div class="stat-label">Decisoes</div></div>
<div class="stat"><div class="stat-num">$($(($allDecisions | ForEach-Object { $_.court } | Where-Object { $_ } | Select-Object -Unique).Count))</div><div class="stat-label">Tribunais</div></div>
</div>
<div class="search-box"><input type="text" id="filter" placeholder="Filtrar..." oninput="filterCards()"></div>
<div id="cards">$rows</div>
<div class="footer">Cache TTL: $($Script:CacheTTLHours)h</div>
</div>
<script>function filterCards(){var q=document.getElementById('filter').value.toLowerCase();document.querySelectorAll('.card').forEach(function(c){c.style.display=q===''||c.textContent.toLowerCase().includes(q)?'':'none'})}</script>
</body></html>
"@

    $html | Set-Content -LiteralPath $OutputPath -Encoding UTF8
    Write-Host "Documentacao gerada: $OutputPath ($count decisoes)" -ForegroundColor Green
    if ($Open) { Start-Process $OutputPath }
}

function Invoke-JurPreFetch {
    param(
        [Parameter(Mandatory)] [string] $Court,
        [string[]] $Terms = @("desapropriacao","precatorio","imissao na posse","indenizacao","utilidade publica","justa indenizacao","tombamento","direito de propriedade","posse","reintegracao de posse","usucapiao","bem publico","servidao administrativa","limitação administrativa"),
        [int] $MaxPages = 0
    )
    Write-Host "=== PRE-FETCH: $Court ===" -ForegroundColor Yellow
    $total = 0
    foreach ($term in $Terms) {
        for ($p = 0; $p -le $MaxPages; $p++) {
            Write-Host "[$($Court)] '$term' pag.$p ... " -NoNewline
            try {
                $r = Search-JurDecisions -Court $Court -Query $term -Page $p -Force
                if ($r -and @($r).Count -gt 0) { Write-Host "$(@($r).Count) resultados" -ForegroundColor Green; $total += @($r).Count }
                else { Write-Host "0 resultados" -ForegroundColor DarkGray; break }
            } catch { Write-Host "ERRO: $_" -ForegroundColor Red; break }
        }
    }
    Write-Host "=== CONCLUIDO: $total decisoes cacheadas ===" -ForegroundColor Yellow
}
