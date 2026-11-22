# Seguimiento de NexusKM

**Actualización:** 21 de noviembre de 2026. **Entrega anunciada:** 27 de noviembre de 2026.

| Entregable | Estado y evidencia |
| --- | --- |
| 1 Propuesta | Completo: usuarios, problema, alcance y 12 RFI; docs/01-propuesta.md |
| 2 Modelado | Completo: conceptual, SQL, Mongo y grafo; diccionarios y 33 relaciones con min/max |
| 3 Arquitectura | Completo: stack, responsabilidades, consistencia eventual y comparación |
| 4 Bases | Implementadas y ejecutadas: PostgreSQL, MongoDB y Neo4j; reconstrucción verificada |
| 5 Catálogo | Completo: operaciones, validaciones, errores, 5 SQL, 4 Mongo y 9 Cypher |
| 6 Backend | Implementado: API, servicios, repositorios, permisos y OpenAPI |
| 7 Aplicación | Verificada: login, impacto, CRUD documental, publicación, auditoría y móvil |
| 8 Pruebas y manual | 39 pruebas aprobadas, recuperación y concurrencia; manual y evidencias actuales |

[Índice y enlaces de los ocho entregables](../docs/README.md). [Artefactos para entregar](../entrega/). [Guion de demostración](../docs/demo.md).

## Decisiones y procedencia

| Fecha | Hecho o decisión | Procedencia |
| --- | --- | --- |
| 16 nov | Guía, anuncio y clase organizados | Material del profesor |
| 18 nov | Tema NexusKM, migración de 33 archivos y ZIP | Solicitud del usuario; comparación SHA-256 |
| 18 nov | Repositorio público y retirada de referencia al chat | Autorización expresa del usuario |
| 21 nov | Completar entregables y aplicación integrada | Solicitud del usuario |
| 21 nov | PostgreSQL, MongoDB, Neo4j, FastAPI, interfaz local y Compose | Decisión de implementación razonada en docs/03-arquitectura.md |
| 21 nov | Aprobación del propietario por identidad exacta, baja lógica y outbox | Resolución de revisión adversaria y reglas del dominio |
| 21 nov | Nueva copia de guía idéntica por SHA-256 | Archivo aportado por el usuario |

## Evidencia actual

Entorno Docker Desktop en Windows, puertos de host 55432, 57017, 57687/57474 y app 58000. Base Neo4j aislada `neo4j`; no se modificó la instancia histórica nahl-1. Los comandos están en scripts/ y en el manual; versiones, fechas y resultados en docs/pruebas/evidencias.

La carga inicial es 63 nodos y 87 relaciones, 3 agregados y 3 documentos SQL. Después del ensayo UI hay 65 nodos y 90 relaciones, 4 agregados y 4 documentos SQL, 3 activos. La diferencia corresponde a historial de un borrador dado de baja y SOL-001 publicada, no a duplicación accidental. Las 39 pruebas crean y limpian sus propios IDs.

Se verificaron claves, rollback, validación documental, constraints, consultas positivas y negativas, permisos, concurrencia, idempotencia, aprobación, publicación y recuperación de un fallo inyectado. Un proyecto Compose separado con volúmenes vacíos reconstruyó las bases y conservó conteos y fechas después del reinicio.

## Información administrativa por completar

Los nombres de integrantes, hora y canal exactos de envío y cualquier rúbrica adicional dependen del equipo y del profesor. El repositorio y los archivos están preparados; no se ha realizado el envío a Classroom. Las extensiones y necesidades productivas se delimitan en la propuesta y no se cuentan como funciones implementadas.
