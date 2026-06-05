# PowerShell Script para Configurar Exclusões do Windows Defender e Regras de Firewall para MSYS2/OpenCode
# Este script precisa de privilégios de Administrador. Se não estiver elevado, ele solicitará permissão automaticamente.

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "==========================================================" -ForegroundColor Yellow
    Write-Host "Solicitando permissão de Administrador (UAC)..." -ForegroundColor Cyan
    Write-Host "==========================================================" -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    Exit
}

Write-Host "==========================================================" -ForegroundColor Green
Write-Host "   Configuração de Segurança para MSYS, OpenCode e LaTeX (Biber)" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host ""

# 1. Procurar diretórios que contêm DLLs do MSYS ou executáveis do LaTeX (como biber.exe)
$commonPaths = @(
    "C:\msys64",
    "C:\msys",
    "C:\Program Files\Git",
    "C:\Program Files (x86)\Git",
    "C:\Program Files\MiKTeX",
    "C:\texlive",
    "$env:LOCALAPPDATA\Programs",
    "$env:USERPROFILE\AppData\Local\Programs"
)

$detectedFolders = @()
$targetFiles = @("msys-z.dll", "msys-2.0.dll", "biber.exe")

Write-Host "Buscando diretórios com arquivos MSYS e Biber..." -ForegroundColor Cyan

foreach ($path in $commonPaths) {
    if (Test-Path $path) {
        foreach ($target in $targetFiles) {
            $files = Get-ChildItem -Path $path -Filter $target -Recurse -ErrorAction SilentlyContinue
            foreach ($file in $files) {
                $dir = $file.DirectoryName
                if ($detectedFolders -notcontains $dir) {
                    $detectedFolders += $dir
                    Write-Host "[Achado] $target em: $dir" -ForegroundColor Green
                }
            }
        }
    }
}

# Se não encontrou em locais óbvios, adiciona o padrão C:\msys64
if ($detectedFolders.Count -eq 0) {
    if (Test-Path "C:\msys64") {
        $detectedFolders += "C:\msys64"
        Write-Host "Usando diretório padrão: C:\msys64" -ForegroundColor Cyan
    }
}

# 2. Aplicar exclusões no Windows Defender (Antivírus)
if ($detectedFolders.Count -gt 0) {
    Write-Host ""
    Write-Host "--> Adicionando exclusões no Windows Defender..." -ForegroundColor Cyan
    foreach ($folder in $detectedFolders) {
        try {
            Add-MpPreference -ExclusionPath $folder -ErrorAction Stop
            Write-Host "SUCESSO: Pasta '$folder' excluída do Windows Defender." -ForegroundColor Green
        } catch {
            Write-Warning "Falha ao adicionar exclusão para '$folder': $_"
        }
    }
} else {
    Write-Host "Nenhum diretório MSYS foi detectado automaticamente." -ForegroundColor Yellow
    Write-Host "Você pode instalar o MSYS2 no caminho padrão (C:\msys64) ou adicioná-lo manualmente." -ForegroundColor Yellow
}

# 3. Adicionar regra de Firewall para a porta 44398 (OpenCode)
Write-Host ""
Write-Host "--> Configurando Regra de Firewall para o OpenCode na porta 44398..." -ForegroundColor Cyan
try {
    # Remover regra antiga se existir para evitar duplicação
    Remove-NetFirewallRule -DisplayName "OpenCode Port 44398" -ErrorAction SilentlyContinue
    
    # Criar nova regra
    New-NetFirewallRule -DisplayName "OpenCode Port 44398" `
                        -Direction Inbound `
                        -Action Allow `
                        -Protocol TCP `
                        -LocalPort 44398 `
                        -Description "Permite conexões de entrada para o ecossistema OpenCode" `
                        -ErrorAction Stop | Out-Null
                        
    Write-Host "SUCESSO: Regra de Firewall criada para permitir TCP de entrada na porta 44398." -ForegroundColor Green
} catch {
    Write-Warning "Falha ao criar regra de firewall: $_"
}

# 4. Informar sobre como restaurar a DLL caso o antivírus já a tenha excluído
Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "Configurações concluídas com sucesso!" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host ""
Write-Host "DICA ADICIONAL:" -ForegroundColor Yellow
Write-Host "Se o arquivo 'msys-z.dll' já tiver sido excluído/quarentenado antes deste script:" -ForegroundColor White
Write-Host "1. Abra 'Segurança do Windows' no menu iniciar." -ForegroundColor White
Write-Host "2. Vá em 'Proteção contra vírus e ameaças' > 'Histórico de proteção'." -ForegroundColor White
Write-Host "3. Encontre o bloqueio do arquivo e clique em 'Ações' > 'Restaurar'." -ForegroundColor White
Write-Host ""
Write-Host "Pressione qualquer tecla para fechar..." -ForegroundColor Gray
$null = [Console]::ReadKey()
