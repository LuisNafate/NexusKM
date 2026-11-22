$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $projectRoot
$testExitCode = 1
try {
    $evidencePath = Join-Path $projectRoot 'docs/pruebas/evidencias'
    New-Item -ItemType Directory -Force -Path $evidencePath | Out-Null
    docker compose stop app
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo preparar la ejecución de pruebas.' }
    docker compose run --rm --no-deps --volume "${evidencePath}:/app/docs/pruebas/evidencias" app python -m pytest -q --junitxml=docs/pruebas/evidencias/pytest.xml
    $testExitCode = $LASTEXITCODE
} finally {
    docker compose up -d app
    Pop-Location
}
if ($testExitCode -ne 0) { throw 'Las pruebas detectaron un problema. Revisa el resultado.' }
