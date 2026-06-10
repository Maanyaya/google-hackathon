# Upload MoDeX demo videos (PowerShell)
# Usage:
#   .\scripts\upload_mcp_demo_video.ps1 -VideoPath "C:\path\to\your-recording.mp4"
#   .\scripts\upload_mcp_demo_video.ps1 -VideoPath ".\recording.mp4" -Target handoff

param(
    [Parameter(Mandatory = $true)]
    [string]$VideoPath,
    [ValidateSet("mcp-setup", "handoff")]
    [string]$Target = "mcp-setup",
    [string]$Bucket = "gen-lang-client-0795401430-agentic-data-platform-logs"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $VideoPath)) {
    Write-Error "Video not found: $VideoPath"
}

$destName = if ($Target -eq "handoff") { "handoff-demo.mp4" } else { "mcp-setup.mp4" }
$localPublic = Join-Path $PSScriptRoot "..\frontend\public\videos\$destName"
$localPublic = [System.IO.Path]::GetFullPath($localPublic)

New-Item -ItemType Directory -Force -Path (Split-Path $localPublic) | Out-Null
Copy-Item -Force $VideoPath $localPublic
Write-Host "Copied to $localPublic (bundled with frontend on next build)"

$gcsUri = "gs://$Bucket/demo-videos/$destName"
Write-Host "Uploading to $gcsUri ..."
gsutil cp $VideoPath $gcsUri
gsutil acl ch -u AllUsers:R $gcsUri

$publicUrl = "https://storage.googleapis.com/$Bucket/demo-videos/$destName"
Write-Host ""
Write-Host "Public GCS URL:"
Write-Host $publicUrl
Write-Host ""
Write-Host "Option A — bundle with app (recommended):"
Write-Host "  cd frontend; npm run build"
Write-Host "  gcloud run deploy agentic-data-platform --source . --region asia-south1"
Write-Host ""
Write-Host "Option B — external URL on Cloud Run (no rebuild):"
$envKey = if ($Target -eq "handoff") { "MODEX_DEMO_VIDEO_URL" } else { "MODEX_MCP_SETUP_VIDEO_URL" }
Write-Host "  gcloud run services update agentic-data-platform --region asia-south1 --update-env-vars ${envKey}=$publicUrl"
