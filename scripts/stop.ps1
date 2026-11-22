$ErrorActionPreference = 'Stop'
Push-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
try {
    docker compose stop
    if ($LASTEXITCODE -ne 0) { throw 'No se pudieron detener los servicios.' }
} finally {
    Pop-Location
}
