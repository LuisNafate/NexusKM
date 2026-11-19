# Configuración de Neo4j MCP para Codex

## Recomendación

Usa el servidor oficial Neo4j MCP. Para Neo4j Desktop 2 local, la ruta más simple es transporte `stdio` con `uvx`. Neo4j indica como prerrequisitos una base activa y APOC para inspeccionar el esquema. GDS es opcional.

## 1. Preparar Neo4j Desktop 2

1. Inicia la instancia que contiene `nexuskm`.
2. Confirma el puerto Bolt, normalmente `bolt://localhost:7687`.
3. Instala y habilita APOC desde la instancia de Desktop.
4. Crea, si tu edición lo permite, un usuario dedicado. Para la primera inspección concédele solo lectura sobre `nexuskm`.
5. No pegues contraseñas en el prompt ni las guardes dentro de esta carpeta.

## 2. Instalar `uv`

Instala `uv` siguiendo https://docs.astral.sh/uv/ para disponer de `uvx`.

## 3. Registrar el servidor en Codex

Codex comparte la configuración MCP entre CLI y extensión. La documentación oficial permite registrar servidores con la CLI o en `~/.codex/config.toml`.

Ejemplo conceptual para un servidor local `stdio` en `config.toml`:

```toml
[mcp_servers.neo4j_nexuskm]
command = "uvx"
args = ["neo4j-mcp-server"]
env_vars = ["NEO4J_MCP_PASSWORD"]

[mcp_servers.neo4j_nexuskm.env]
NEO4J_MCP_URI = "bolt://localhost:7687"
NEO4J_MCP_USERNAME = "nexuskm_reader"
NEO4J_MCP_DATABASE = "nexuskm"
NEO4J_MCP_READ_ONLY = "true"
NEO4J_MCP_TELEMETRY = "false"
NEO4J_MCP_SCHEMA_SAMPLE_SIZE = "100"
```

La misma configuración está disponible en `codex_config_neo4j.toml.example` para copiarla a `~/.codex/config.toml` o a `.codex/config.toml` dentro de un proyecto de confianza.

Define `NEO4J_MCP_PASSWORD` como variable de entorno local antes de iniciar Codex. `env_vars` permite que Codex la reenvíe al proceso sin escribir el secreto en este archivo. Verifica la conexión con `codex mcp list`; en la interfaz también puedes usar `/mcp`. Después pide al agente que use `get-schema` y `read-cypher`.

## 4. Habilitar escritura solo para la carga

Después de revisar el plan y respaldar lo necesario:

1. Cambia a un usuario limitado con permisos de escritura únicamente en `nexuskm`.
2. Cambia `NEO4J_MCP_READ_ONLY` a `false`.
3. Reinicia la sesión de Codex para recargar herramientas.
4. Ejecuta únicamente los scripts aprobados.
5. Al terminar, restablece solo lectura.

Neo4j MCP expone `get-schema`, `read-cypher` y `write-cypher`. La documentación advierte que las consultas generadas por un modelo pueden causar daño y recomienda escritura solo en entornos de desarrollo.

## 5. Alternativa sin MCP

Ejecuta manualmente los scripts en Neo4j Query y entrega a Codex los resultados de texto. Esta alternativa conserva control humano total y es suficiente para el proyecto académico.

## Compatibilidad de versión

Esta guía se verificó el 12 de noviembre de 2026. Neo4j MCP 2.0 cambió el modo HTTP a rutas por base de datos (`/db/{databaseName}/mcp`) y exige configuración distinta a `stdio`. Para una base local de Desktop, esta guía utiliza `stdio`, donde `NEO4J_MCP_DATABASE` debe declararse explícitamente.
