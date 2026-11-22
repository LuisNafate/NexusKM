$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $projectRoot
try {
    if (-not (Test-Path -LiteralPath '.env')) {
        $configuration = [ordered]@{
            POSTGRES_DB = 'nexuskm'
            POSTGRES_USER = 'nexuskm'
            POSTGRES_PASSWORD = ''
            POSTGRES_PORT = '55432'
            MONGO_USER = 'nexuskm'
            MONGO_PASSWORD = ''
            MONGO_PORT = '57017'
            NEO4J_USER = 'neo4j'
            NEO4J_PASSWORD = ''
            NEO4J_BOLT_PORT = '57687'
            NEO4J_HTTP_PORT = '57474'
            APP_PORT = '58000'
            TOKEN_SECRET = ''
            DEMO_PASSWORD = ''
        }
        $generator = [System.Security.Cryptography.RandomNumberGenerator]::Create()
        try {
            foreach ($key in @('POSTGRES_PASSWORD', 'MONGO_PASSWORD', 'NEO4J_PASSWORD', 'TOKEN_SECRET', 'DEMO_PASSWORD')) {
                $buffer = New-Object byte[] 32
                $generator.GetBytes($buffer)
                $configuration[$key] = [Convert]::ToBase64String($buffer).TrimEnd('=').Replace('+', '-').Replace('/', '_')
            }
        } finally {
            $generator.Dispose()
        }
        $lines = foreach ($entry in $configuration.GetEnumerator()) { "$($entry.Key)=$($entry.Value)" }
        [IO.File]::WriteAllLines((Join-Path $projectRoot '.env'), $lines, (New-Object Text.UTF8Encoding $false))
    }
    docker compose up -d --build --wait --wait-timeout 240
    if ($LASTEXITCODE -ne 0) { throw 'Revisa Docker Desktop y los servicios con docker compose ps.' }
    $portLine = Get-Content -LiteralPath '.env' | Where-Object { $_ -match '^APP_PORT=' } | Select-Object -First 1
    $applicationPort = ($portLine -split '=', 2)[1]
    Write-Host "NexusKM disponible en http://localhost:$applicationPort"
    Write-Host 'Acceso de demostración con PER-002. Consulta DEMO_PASSWORD en tu archivo .env.'
} finally {
    Pop-Location
}
