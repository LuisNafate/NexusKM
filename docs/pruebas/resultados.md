# Resultados de verificación actual

Corte académico 21 de noviembre de 2026. Marca temporal exacta UTC: 2026-11-22T04:49:10.496838+00:00.

## Pruebas

39 aprobadas, 0 fallos, 0 errores, 0 omitidas. Tiempo JUnit 4.018 segundos. El aviso de deprecación de Starlette/AnyIO no impidió la ejecución.

## Estado de las bases

| Modelo | Estado actual | Carga inicial |
| --- | --- | --- |
| PostgreSQL | 4 documentos, 4 versiones, 3 documentos activos; 6 eventos de auditoría | 3 documentos y 3 versiones |
| MongoDB | 4 agregados de versión; retiene el borrador dado de baja | 3 agregados |
| Neo4j | 65 nodos, 90 relaciones, 23 etiquetas, 24 constraints y 32 índices | 63 nodos y 87 relaciones |

## Rendimiento HTTP

| Operación | Muestras | Mediana ms | p95 ms | Máximo ms |
| --- | --- | --- | --- | --- |
| /api/impact/API-002 | 30 | 38.44 | 42.94 | 70.53 |
| /api/documents/DOC-001 | 30 | 32.19 | 34.31 | 37.48 |
| /api/requests | 30 | 24.02 | 25.65 | 26.33 |

Cliente secuencial autenticado sobre localhost, datos pequeños, motores en Docker Desktop. p95 usa rango más cercano ceil(0.95×30). No hay benchmark entre motores ni estimación de capacidad para producción.

## Versiones

PostgreSQL 16.16, MongoDB 7.0.48, Neo4j 5.26.33 Community. Python del recolector 3.12.14. Las imágenes y dependencias del servidor están fijadas en Compose y requirements-lock.txt.

## Procedencia

verificacion-carga.json conserva la instantánea inicial y su medición anterior; verificacion-integrada.json refleja el estado posterior a los flujos de navegador. Los resultados del 12 de noviembre en NexusKM/evidencias son antecedentes. Los datos reales actuales, comandos de reconstrucción y capturas están en esta carpeta.
