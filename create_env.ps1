# create_env.ps1 — Windows helper to make a .env file and optionally run auth
# Run this from the project folder in PowerShell (Right-click -> "Open in Terminal")

Param()

$clientId = Read-Host "Enter your Spotify CLIENT_ID"
$clientSecret = Read-Host "Enter your Spotify CLIENT_SECRET"
$redirect = "http://127.0.0.1:8888/callback"

$envPath = Join-Path -Path (Get-Location) -ChildPath ".env"
if (Test-Path $envPath) {
    $ok = Read-Host ".env already exists. Overwrite? (y/N)"
    if ($ok -ne 'y' -and $ok -ne 'Y') {
        Write-Output ".env left unchanged. If you want to update it later, re-run this script or edit .env manually."
        exit 0
    }
}

$envContent = @"
CLIENT_ID=$clientId
CLIENT_SECRET=$clientSecret
REDIRECT_URI=$redirect
REFRESH_TOKEN=
"@

Set-Content -Path $envPath -Value $envContent -Encoding UTF8
Write-Output ".env created at $envPath"

$runGet = Read-Host "Run python get_refresh_token.py now to authenticate with Spotify and create a .cache file? (Y/n)"
if ($runGet -eq '' -or $runGet -match '^[Yy]') {
    Write-Output "Running: python get_refresh_token.py — this will open your browser to authorize."
    python get_refresh_token.py
    Write-Output "Attempting to extract REFRESH_TOKEN from .cache and write to .env..."
    python extract_refresh_token.py --update
    Write-Output "If the script found a token, .env REFRESH_TOKEN was updated. Run 'python test_env.py' to verify."
}

Write-Output "Done. Install required packages: python -m pip install -r requirements.txt"
