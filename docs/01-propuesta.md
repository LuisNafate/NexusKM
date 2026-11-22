# 1 Propuesta de aplicación

NexusKM conecta conocimiento técnico, responsables y dependencias de software. El nombre combina **Nexus**, vínculo o conexión, con **KM**, Knowledge Management o gestión del conocimiento. El sistema permite identificar el impacto de una API y consultar documentos vigentes antes de modificar un servicio.

## Problema y objetivo

Una empresa de software conserva contratos de API, procedimientos operativos y modelos de amenazas en fuentes dispersas. Ante un cambio, el equipo necesita saber qué servicio depende de la API, qué proyecto resulta afectado, quién responde por ese proyecto y qué documentación está aprobada. Una lista de archivos no expresa estas relaciones ni garantiza que el contenido consultado sea vigente.

El objetivo es consultar ese contexto en una aplicación y controlar la creación, revisión y publicación del conocimiento con evidencia trazable. Los dos proyectos, seis usuarios y demás registros son ficticios; representan un levantamiento de necesidades simulado.

## Usuarios y necesidades

| Usuario | Necesidad | Acción disponible |
| --- | --- | --- |
| Líder de proyecto | Identificar consumidores y responsables de un cambio | Consulta de impacto y documentos internos |
| Propietario documental | Mantener y publicar contenido confiable | Alta, versión, edición de borrador, solicitud, publicación y baja |
| Revisor técnico | Comprobar consistencia técnica | Aprobación técnica, lectura de contenido restringido |
| Seguridad | Revisar riesgos y trazabilidad | Aprobación de seguridad y auditoría global |
| Administrador | Recuperar sincronizaciones y mantener el catálogo documental | Reintento de outbox, asignación de propietario y auditoría |

## Requisitos del alcance final

Los identificadores **RFI** distinguen estos requisitos de los RF históricos del grafo. La prioridad de todos es necesaria para la demostración integrada.

| ID | Requisito | Criterio comprobable |
| --- | --- | --- |
| RFI01 | Autenticar usuarios activos y aplicar permisos en el servidor | Token inválido o vencido devuelve 401; rol no habilitado, 403 |
| RFI02 | Consultar proyectos, personas y APIs con IDs comunes | Catálogo une PostgreSQL y Neo4j sin cambiar PER, PRY o API |
| RFI03 | Crear un documento y su primera versión | Metadatos en SQL, contenido válido en Mongo y proyección en Neo4j |
| RFI04 | Consultar documentos y versiones con clasificación | Lista y detalle omiten o rechazan contenido no permitido |
| RFI05 | Modificar título y contenido de borrador con revisión | Una revisión obsoleta devuelve 409; contenido publicado es inmutable |
| RFI06 | Crear versiones numeradas sin duplicarlas por documento | Número repetido devuelve 409; conserva historial |
| RFI07 | Dar de baja un documento sin publicación ni solicitud abierta | Desaparece del catálogo activo y conserva auditoría e historial |
| RFI08 | Solicitar revisión y congelar el contenido | Versión BORRADOR pasa a EN_REVISION; una solicitud abierta por versión |
| RFI09 | Exigir dos técnicos distintos y aprobación real del propietario | Rechaza autoaprobación técnica, rol ajeno y propietario incorrecto |
| RFI10 | Exigir seguridad para contenido restringido y publicar | Verifica requisitos, contenido sincronizado y vencimiento futuro |
| RFI11 | Consultar impacto técnico con documentos vigentes | API → dependencia → servicio → componente → proyecto; SQL y Mongo completan el resultado |
| RFI12 | Auditar comandos y recuperar escrituras parciales sin duplicar efectos | Outbox persistente, estado pendiente, reintento e idempotencia |

## Función de cada modelo

| Modelo | Información oficial | Operación representativa | Razón |
| --- | --- | --- | --- |
| Relacional PostgreSQL | Personas, proyectos, metadatos, versiones, solicitudes, aprobaciones y auditoría | Publicar una versión y retirar la anterior en una transacción | Claves, unicidad, integridad referencial y coordinación de cambios |
| Documental MongoDB | Contenido por versión: secciones, pasos, endpoints o amenazas | Recuperar o reemplazar el contenido completo de un borrador | Agregado de lectura y escritura con estructura variable según tipo |
| Grafo Neo4j | Activos técnicos y dependencias; copias de contexto documental | Recorrer consumidores de Inventory API y llegar a los proyectos | Las conexiones y los recorridos son el objeto de la consulta |

Se utilizan los tres motores: **un grafo también pertenece a la familia NoSQL**. SQL podría guardar todo mediante tablas y uniones; MongoDB podría representar referencias; Neo4j podría almacenar metadatos. La selección distribuye responsabilidades según las operaciones y cumple la integración solicitada. No se afirma una superioridad universal ni un rendimiento comparativo no medido.

## Límites de la entrega

La aplicación web local incluye interfaz, API REST, tres bases reales, autenticación de demostración, permisos, CRUD documental con baja lógica, gobernanza, impacto, auditoría y recuperación. El inventario técnico y los catálogos organizacionales se cargan por scripts; su administración completa por interfaz queda fuera de esta versión.

Las excepciones, delegaciones, escalamiento y conectores Confluence/GitHub del grafo anterior se conservan como **datos y consultas de extensión**. No ejecutan conectores externos ni calendarios laborales. SSO, correo, registro de usuarios, gestión de contraseñas, alta disponibilidad, respaldos automáticos y despliegue público del servicio requieren trabajo adicional. La publicación del repositorio permite compartir el código y las evidencias.
