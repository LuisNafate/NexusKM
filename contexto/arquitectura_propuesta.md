# Arquitectura de NexusKM

**Evolución:** borrador del 18 de noviembre; implementación y pruebas del 21 de noviembre de 2026. La [especificación vigente](../docs/03-arquitectura.md) contiene diagrama, comparación, contratos y recuperación.

| Componente | Decisión implementada |
| --- | --- |
| Relacional | PostgreSQL 16, psycopg 3; catálogos, versiones, aprobaciones, auditoría y outbox |
| Documental | MongoDB 7 y PyMongo; agregado de contenido por versión con JSON Schema |
| Grafo | Neo4j 5.26 Community y driver oficial; dependencias y proyecciones |
| Backend | Python 3.12 y FastAPI REST con OpenAPI |
| Interfaz | HTML, CSS y JavaScript; vistas de impacto, documentos, aprobación y auditoría |
| Ejecución | Cuatro servicios Docker Compose, dependencias e imágenes fijadas |

El diseño final confirma primero SQL con el payload transitorio de contenido en outbox. Después entrega a Mongo y Neo4j; limpia el payload al completar. Sustituye la idea inicial de escribir primero un borrador Mongo, porque la cola SQL permite conservar la intención y evitar un agregado huérfano ante rollback. El worker cada 10 segundos y el reintento ADMIN recuperan fallos parciales. La prueba controlada cubre Mongo completado y Neo4j fallido, seguida de convergencia sin duplicados.

Los IDs PER, PRY, DOC, VER y API se comparten. SQL es autoridad de metadatos y permisos; Mongo de contenido; Neo4j de activos y dependencias. La consulta de impacto coordina los tres. Los catálogos de personas/proyectos son estáticos en esta versión, de modo que su proyección se carga al inicio y no existe una API de mantenimiento que deba sincronizar cambios posteriores.

La baja es lógica, preserva referencias y se rechaza si hay versión vigente o solicitud abierta. Publicar exige versión no vencida, contenido listo, dos técnicos diferentes, propietario real y seguridad para RESTRINGIDO. Las políticas de delegación y 48/72 horas hábiles siguen como extensión sin automatización.

La elección tecnológica está razonada en el entregable 3. Fue realizada al implementar la solicitud de completar el proyecto y no se registra como una preferencia previamente confirmada por el usuario.
