# MoDeX local UI launcher (Windows-safe)
# Serves ADK dev-ui + Mission Control dashboard via app.fast_api_app
#
# Usage:
#   .\scripts\start_local_ui.ps1
#   .\scripts\start_local_ui.ps1 -Port 8080 -Mode playground

param(
    [int]$Port = 8080,
    [ValidateSet("full", "playground")]
    [string]$Mode = "full"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$SubstDrive = "M:"
$EnvFile = Join-Path (Split-Path -Parent $ProjectRoot) ".env"

function Import-DotEnv {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return }
    Get-Content $Path | ForEach-Object {
        $line = $_.Trim()
        if ($line -eq "" -or $line.StartsWith("#")) { return }
        $idx = $line.IndexOf("=")
        if ($idx -lt 1) { return }
        $key = $line.Substring(0, $idx).Trim()
        $value = $line.Substring($idx + 1).Trim()
        if ($key -eq "GOOGLE_APPLICATION_CREDENTIALS") { return }
        Set-Item -Path "env:$key" -Value $value
    }
}

function Ensure-SubstDrive {
    param([string]$Drive, [string]$Target)
    $existing = subst 2>$null | Where-Object { $_ -match "^$Drive" }
    if ($existing) {
        Write-Host "Using existing drive $Drive -> $Target"
        return
    }
    subst $Drive $Target | Out-Null
    Write-Host "Mapped $Drive -> $Target (avoids PowerShell glob issues with adk web)"
}

Import-DotEnv -Path $EnvFile
Remove-Item Env:GOOGLE_APPLICATION_CREDENTIALS -ErrorAction SilentlyContinue

if (-not $env:GOOGLE_CLOUD_PROJECT) {
    $env:GOOGLE_CLOUD_PROJECT = "gen-lang-client-0795401430"
}
$env:GOOGLE_CLOUD_LOCATION = "global"
$env:GOOGLE_GENAI_USE_VERTEXAI = "True"

Ensure-SubstDrive -Drive $SubstDrive -Target $ProjectRoot
Set-Location $SubstDrive

$devUi = "http://127.0.0.1:$Port/dev-ui/?app=app"
$dashboard = "http://127.0.0.1:$Port/dashboard/"

Write-Host ""
Write-Host "MoDeX local UI ($Mode mode)" -ForegroundColor Cyan
Write-Host "  Dev UI (ADK playground): $devUi"
if ($Mode -eq "full") {
    Write-Host "  Mission Control dashboard: $dashboard"
}
Write-Host ""
Write-Host "Tip: use your user gcloud ADC for Vertex (service account unset)." -ForegroundColor DarkGray
Write-Host "Press Ctrl+C to stop." -ForegroundColor DarkGray
Write-Host ""

if ($Mode -eq "full") {
    $dist = Join-Path $ProjectRoot "frontend\dist\index.html"
    if (-not (Test-Path $dist)) {
        Write-Host "Building frontend (first run)..." -ForegroundColor Yellow
        Push-Location (Join-Path $ProjectRoot "frontend")
        npm run build
        Pop-Location
    }
    uv run uvicorn app.fast_api_app:app --host 127.0.0.1 --port $Port
} else {
    # adk web only — AGENTS_DIR must be last; never pass --allow_origins * (PowerShell expands it)
    uv run adk web --host 127.0.0.1 --port $Port --reload_agents "$SubstDrive\"
}
