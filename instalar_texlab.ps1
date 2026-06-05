# Script para baixar e instalar o TexLab (Language Server para LaTeX) no Windows
# O TexLab será colocado na pasta C:\Users\marce\.cargo\bin, que já está no seu PATH de sistema.

$version = "v5.25.1"
$url = "https://github.com/latex-lsp/texlab/releases/download/$version/texlab-x86_64-windows.zip"
$tempZip = "$env:TEMP\texlab-$version.zip"
$tempExtracted = "$env:TEMP\texlab-$version-extracted"
$targetDir = "C:\Users\marce\.cargo\bin"
$targetPath = "$targetDir\texlab.exe"

Write-Host "==========================================================" -ForegroundColor Green
Write-Host "Instalando TexLab $version no seu ambiente Windows" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host ""

# 1. Verificar se a pasta de destino existe
if (-not (Test-Path $targetDir)) {
    Write-Host "Criando pasta de destino: $targetDir..." -ForegroundColor Cyan
    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
}

# 2. Baixar o arquivo ZIP
Write-Host "Baixando o TexLab de $url..." -ForegroundColor Cyan
try {
    # Usando curl.exe que é nativo no Windows 10/11 e muito mais rápido/robusto
    curl.exe -L -o $tempZip $url
    if (-not (Test-Path $tempZip) -or (Get-Item $tempZip).Length -lt 1000) {
        throw "O download falhou ou o arquivo está corrompido."
    }
} catch {
    Write-Warning "Falha ao baixar com curl. Tentando Invoke-WebRequest..."
    try {
        Invoke-WebRequest -Uri $url -OutFile $tempZip -UseBasicParsing
    } catch {
        Write-Error "Erro ao baixar o TexLab: $_"
        Exit 1
    }
}

# 3. Extrair o arquivo
Write-Host "Extraindo arquivos temporários..." -ForegroundColor Cyan
if (Test-Path $tempExtracted) {
    Remove-Item $tempExtracted -Recurse -Force
}
try {
    Expand-Archive -Path $tempZip -DestinationPath $tempExtracted -Force
} catch {
    Write-Error "Falha ao extrair o arquivo ZIP: $_"
    Exit 1
}

# 4. Mover para a pasta final
Write-Host "Instalando texlab.exe em $targetPath..." -ForegroundColor Cyan
try {
    # Parar processo se já estiver rodando para permitir sobrescrever
    $process = Get-Process -Name "texlab" -ErrorAction SilentlyContinue
    if ($process) {
        Write-Host "Finalizando processo texlab.exe ativo para atualizar..." -ForegroundColor Yellow
        Stop-Process -Name "texlab" -Force
        Start-Sleep -Seconds 1
    }

    if (Test-Path $targetPath) {
        Remove-Item $targetPath -Force
    }
    
    Move-Item -Path "$tempExtracted\texlab.exe" -Destination $targetPath -Force
    Write-Host "SUCESSO: TexLab instalado com sucesso!" -ForegroundColor Green
} catch {
    Write-Error "Falha ao mover texlab.exe para a pasta de destino: $_"
    Exit 1
}

# 5. Limpeza
Write-Host "Limpando arquivos temporários..." -ForegroundColor Cyan
Remove-Item $tempZip -Force -ErrorAction SilentlyContinue
Remove-Item $tempExtracted -Recurse -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "Instalação concluída!" -ForegroundColor Green
Write-Host "Caminho: $targetPath" -ForegroundColor White
Write-Host "==========================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Pressione qualquer tecla para fechar..." -ForegroundColor Gray
$null = [Console]::ReadKey()
