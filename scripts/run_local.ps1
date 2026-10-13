$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

if (-not $env:DATABASE_URL) {
    $env:DATABASE_URL = "sqlite+pysqlite:///./local_exec.db"
}
if (-not $env:SECRET_KEY) {
    $env:SECRET_KEY = "local-dev-secret-change-me"
}

python -m alembic upgrade head
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
