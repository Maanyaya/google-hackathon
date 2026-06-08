# MoDeX UI — LOCAL PREVIEW ONLY (no deploy, no git push)
#
# Usage:
#   .\scripts\preview_ui.ps1              # hot-reload dev (Vite + API)
#   .\scripts\preview_ui.ps1 -Production  # production build served like Cloud Run
#
# After you approve the UI, publish separately:
#   cd frontend; npm run build
#   gcloud run deploy agentic-data-platform --project ... --region asia-south1 --source . ...

param(
    [switch]$Production,
    [int]$Port = 8090
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Frontend = Join-Path $ProjectRoot "frontend"
$EnvFile = Join-Path (Split-Path -Parent $ProjectRoot) ".env"
$Port = if ($env:MODEX_PREVIEW_PORT) { [int]$env:MODEX_PREVIEW_PORT } else { $Port }

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

Import-DotEnv -Path $EnvFile
Remove-Item Env:GOOGLE_APPLICATION_CREDENTIALS -ErrorAction SilentlyContinue
$env:GOOGLE_CLOUD_PROJECT = $(if ($env:GOOGLE_CLOUD_PROJECT) { $env:GOOGLE_CLOUD_PROJECT } else { "gen-lang-client-0795401430" })
$env:GOOGLE_CLOUD_LOCATION = "asia-south1"
$env:GOOGLE_GENAI_USE_VERTEXAI = "True"

Set-Location $ProjectRoot

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MoDeX LOCAL PREVIEW (not published)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($Production) {
    Write-Host "Building frontend (production)..." -ForegroundColor Yellow
    Push-Location $Frontend
    npm run build
    Pop-Location

    Write-Host ""
    Write-Host "Starting API + built dashboard on port $Port ..." -ForegroundColor Green
    Write-Host "  Dashboard:  http://127.0.0.1:$Port/dashboard/" -ForegroundColor White
    Write-Host "  Dev UI:     http://127.0.0.1:$Port/dev-ui/?app=app" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "Press Ctrl+C to stop. Nothing is deployed to Cloud Run." -ForegroundColor DarkGray
    Write-Host ""

    uv run uvicorn app.fast_api_app:app --host 127.0.0.1 --port $Port
} else {
    # Start FastAPI backend in background job
    $backendJob = Start-Job -ScriptBlock {
        param($root, $port)
        Set-Location $root
        $env:GOOGLE_CLOUD_PROJECT = "gen-lang-client-0795401430"
        $env:GOOGLE_CLOUD_LOCATION = "asia-south1"
        $env:GOOGLE_GENAI_USE_VERTEXAI = "True"
        uv run uvicorn app.fast_api_app:app --host 127.0.0.1 --port $port 2>&1
    } -ArgumentList $ProjectRoot, $Port

    Start-Sleep -Seconds 4

    Write-Host "Backend job started (port $Port). Starting Vite dev server..." -ForegroundColor Green
    Write-Host ""
    Write-Host "  PREVIEW URL:  http://localhost:5173/dashboard/" -ForegroundColor Yellow
    Write-Host "  API proxy:    localhost:5173 -> localhost:$Port" -ForegroundColor DarkGray
    Write-Host "  Dev UI:       http://127.0.0.1:$Port/dev-ui/?app=app" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "Edit frontend/src/* — browser hot-reloads." -ForegroundColor DarkGray
    Write-Host "Press Ctrl+C to stop preview (backend job stops too)." -ForegroundColor DarkGray
    Write-Host ""

    $env:MODEX_PREVIEW_PORT = "$Port"

    Push-Location $Frontend
    try {
        npm run dev
    } finally {
        Pop-Location
        Stop-Job $backendJob -ErrorAction SilentlyContinue
        Remove-Job $backendJob -Force -ErrorAction SilentlyContinue
    }
}
