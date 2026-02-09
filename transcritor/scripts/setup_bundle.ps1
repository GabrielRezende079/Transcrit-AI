# Bundle completo (Python embutido + FFmpeg)

$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$bundleDir = Join-Path $root "bundle"
$pythonDir = Join-Path $bundleDir "python"
$ffmpegDir = Join-Path $bundleDir "ffmpeg"
$tempDir = Join-Path $bundleDir "_tmp"

New-Item -ItemType Directory -Force -Path $bundleDir, $pythonDir, $ffmpegDir, $tempDir | Out-Null

Write-Host "\n=== Passo 1: Baixar o Python Embeddable ===" -ForegroundColor Cyan
Write-Host "Baixe o Python embeddable (Windows x64) e coloque o .zip em: $tempDir" -ForegroundColor Yellow
Write-Host "Exemplo de nome: python-3.13.2-embed-amd64.zip" -ForegroundColor Yellow
Write-Host "Depois pressione ENTER para continuar." -ForegroundColor Yellow
Read-Host

$pyZip = Get-ChildItem -Path $tempDir -Filter "python-*-embed-amd64.zip" | Select-Object -First 1
if (-not $pyZip) {
  Write-Error "Nao encontrei um .zip do Python embeddable em $tempDir"
}

Write-Host "Extraindo Python..." -ForegroundColor Cyan
Expand-Archive -Force -Path $pyZip.FullName -DestinationPath $pythonDir

Write-Host "\n=== Passo 2: Instalar dependencias Python no bundle ===" -ForegroundColor Cyan
Write-Host "Vamos usar o pip do sistema para instalar dependencias dentro do bundle." -ForegroundColor Yellow
$pythonExe = Join-Path $pythonDir "python.exe"
$sitePackages = Join-Path $pythonDir "Lib\site-packages"
New-Item -ItemType Directory -Force -Path $sitePackages | Out-Null

# Ativa import do site-packages no embeddable
$pth = Get-ChildItem -Path $pythonDir -Filter "python*.pth" | Select-Object -First 1
if ($pth) {
  $pthPath = $pth.FullName
  $content = Get-Content $pthPath
  if (-not ($content -contains "Lib\\site-packages")) {
    Add-Content $pthPath "Lib\\site-packages"
  }
}

$systemPython = "python"
& $systemPython -m pip install -r (Join-Path $root "requirements.txt") -t $sitePackages

Write-Host "\n=== Passo 3: Baixar FFmpeg ===" -ForegroundColor Cyan
Write-Host "Baixe o FFmpeg (Windows x64) e coloque o .zip em: $tempDir" -ForegroundColor Yellow
Write-Host "Exemplo de nome: ffmpeg-*.zip" -ForegroundColor Yellow
Write-Host "Depois pressione ENTER para continuar." -ForegroundColor Yellow
Read-Host

$ffZip = Get-ChildItem -Path $tempDir -Filter "ffmpeg-*.zip" | Select-Object -First 1
if (-not $ffZip) {
  Write-Error "Nao encontrei um .zip do FFmpeg em $tempDir"
}

Write-Host "Extraindo FFmpeg..." -ForegroundColor Cyan
Expand-Archive -Force -Path $ffZip.FullName -DestinationPath $tempDir
$ffmpegRoot = Get-ChildItem -Path $tempDir -Directory | Where-Object { $_.Name -like "ffmpeg-*" } | Select-Object -First 1
if (-not $ffmpegRoot) {
  Write-Error "Nao achei a pasta do ffmpeg extraida."
}

$ffmpegBin = Join-Path $ffmpegRoot.FullName "bin"
if (-not (Test-Path $ffmpegBin)) {
  Write-Error "Nao achei a pasta bin do ffmpeg."
}

Copy-Item -Recurse -Force -Path $ffmpegRoot.FullName\* -Destination $ffmpegDir

Write-Host "\nBundle completo criado em: $bundleDir" -ForegroundColor Green
Write-Host "Agora rode: npm run dist" -ForegroundColor Green
