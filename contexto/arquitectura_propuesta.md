# Arquitectura integrada propuesta

**Estado** Borrador elaborado el 18 de noviembre de 2026 a partir del dominio de NexusKM y de la guía del proyecto. La elección de motores, lenguaje y plataforma sigue pendiente.

## Operaciones que justifican los tres modelos

| Modelo | Responsabilidad propuesta | Operación demostrable | Capacidad que aporta |
| --- | --- | --- | --- |
| Relacional | Personas, organización, roles, identidad de documentos y versiones, solicitudes, decisiones de aprobación y estado de publicación. | Registrar una aprobación válida y actualizar el estado de la solicitud dentro de una transacción. | Restricciones entre registros y control de transiciones coherentes ante reintentos o cambios simultáneos. |
| Documental | Contenido de versiones de runbooks, contratos de API y modelos de amenazas. | Guardar y recuperar un documento con secciones, pasos, parámetros o amenazas anidadas según su tipo. | Manejo de documentos completos cuya estructura cambia entre categorías. |
| Grafo | Activos técnicos, dependencias, cobertura documental y conexiones con proyectos y responsables. | Consultar qué servicios, componentes y proyectos dependen de Inventory API. | Recorridos y patrones de impacto técnico. |

La base documental necesita contenido de ejemplo con estructura propia. El paquete recibido contiene metadatos de documentos en el grafo. Crear ejemplos de un runbook con pasos y un contrato de API con operaciones y parámetros permitiría justificar la necesidad documental.

## Matriz de propiedad de datos

| Datos | Fuente de verdad propuesta | Copias y referencias |
| --- | --- | --- |
| Identidad y estado de personas, departamentos y proyectos | Relacional | Neo4j conserva identificadores y los atributos necesarios para mostrar recorridos. |
| Asignaciones de líder, departamento y roles | Relacional | Neo4j conserva relaciones proyectadas para consultas de contexto. |
| Documento y versión identificables, propietario, clasificación y estado de publicación | Relacional | La base documental referencia documentoId y versionId. Neo4j conserva enlaces y metadatos mínimos de consulta. |
| Contenido anidado de cada versión | Documental | Referencia mediante versionId desde el catálogo relacional y el contexto del grafo. |
| Solicitudes y aprobaciones | Relacional | El grafo puede conservar su conexión con la versión como proyección para trazabilidad. |
| Repositorios, componentes, microservicios, APIs y dependencias | Grafo | Las otras bases referencian sus identificadores cuando una operación los necesita. |
| Eventos de negocio y operaciones de sincronización | Relacional | Registrar operación, estado de sincronización y entidades afectadas. Proyectar en Neo4j únicamente lo necesario para recorrer la trazabilidad. |

Los identificadores PER-001, PRY-001, DOC-001, VER-001 y API-002, entre otros, sirven como enlaces comunes durante el diseño. El backend valida que la entidad referenciada exista y define el comportamiento ante una baja o una réplica atrasada.

## Lectura integrada de impacto y conocimiento

1. La interfaz solicita el impacto de API-002 al backend.
2. El servicio consulta en Neo4j los consumidores, componentes y proyectos afectados.
3. Recupera del catálogo relacional los responsables y los documentos autorizados asociados con esos proyectos.
4. Solicita a la base documental el contenido de las versiones seleccionadas por versionId.
5. Devuelve una respuesta única con impacto, responsables, documentación y estado de los datos consultados.

La autorización precede a la entrega del contenido. Las pruebas deben verificar también la ausencia de versiones autorizadas y el caso en que una base requerida esté temporalmente disponible con retraso o falle.

## Publicación y fallos parciales

Como estrategia inicial se propone registrar primero el contenido como borrador documental. Una transacción relacional verifica revisores y estado, confirma la publicación y registra una operación pendiente para proyectar el cambio al grafo. El procesamiento de esa operación debe poder repetirse usando un identificador único.

El flujo debe comprobar que la versión de contenido existe y está lista antes de confirmar la publicación. Al fallar la transacción relacional, el borrador documental sigue identificado para su recuperación. Al fallar la actualización del grafo, la operación pendiente permite reintentar y comunicar el estado de sincronización. La revisión y limpieza de borradores sin referencia forma parte de la política por definir.

Para solicitudes concurrentes, definir una transición condicional sobre la versión o el estado del registro que impida confirmar dos transiciones incompatibles. El detalle de bloqueo, aislamiento o control de versión se elige con la tecnología.

Esta estrategia incorpora persistencia del trabajo pendiente, reintentos y reconciliación al alcance de integración. Su implementación y sus pruebas siguen pendientes.

## Decisiones que deben cerrarse antes de implementar

- Estados permitidos y transición entre solicitud aprobada y versión publicada.
- Fuente de verdad definitiva por entidad y campos exactos que se replican.
- Autoridad de aprobación documental y reglas de delegación. El caso recibido presenta una diferencia de propietario que debe resolverse.
- Alcance de eliminación o baja por entidad y conservación de referencias e historial.
- Tipo de documento y ejemplos de contenido anidado para la base documental.
- Impacto directo que resuelve Q3 y recorridos adicionales que requiera el dominio.
- Motores, API, lenguaje y condiciones de ejecución reproducible.

Las preguntas y casos de fallo para validar estas decisiones están en la [revisión adversaria](revision_adversaria.md).
