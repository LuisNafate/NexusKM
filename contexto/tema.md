# NexusKM

## Origen y estado de la información

El usuario eligió NexusKM el 18 de noviembre de 2026 al proporcionar la carpeta, el ZIP y el chat del trabajo previo. El dominio procede de un levantamiento simulado para una empresa de software. Los nombres, proyectos y registros de muestra son ficticios.

La ficha sintetiza el [documento académico](../NexusKM/documentacion/NexusKM_documento_academico_actualizado.pdf), el [README previo](../NexusKM/README.md) y el [chat compartido](fuentes/antecedentes/chat_compartido.md). La ampliación a las tres bases se desarrolla en la [arquitectura propuesta](arquitectura_propuesta.md).

## Ficha de aplicación

| Campo | Definición |
| --- | --- |
| Nombre | NexusKM. |
| Descripción | Aplicación de gestión de conocimiento técnico, responsables, documentación versionada y dependencias de software. |
| Problema | Los equipos conservan contratos de API, runbooks, decisiones y responsables en herramientas dispersas. Un cambio puede afectar servicios y documentos cuya dependencia resulta difícil de identificar. |
| Usuarios | Líderes de proyecto, arquitectos y revisores técnicos, responsables documentales, revisores de seguridad y administradores de conocimiento. |
| Objetivo general | Permitir que el equipo identifique el impacto de un cambio técnico, consulte el conocimiento relacionado y tramite decisiones con evidencia trazable. |
| Ejemplo central | Consultar qué servicio, componente y proyecto dependen de Inventory API y acceder a los documentos y responsables relacionados. |
| Integrantes | Pendientes de registrar. |
| Datos disponibles | Dos proyectos, seis personas, cuatro departamentos y ejemplos de documentos, versiones, APIs, dependencias, aprobaciones y auditoría. |

## Operaciones recuperadas

El documento anterior contiene doce requisitos funcionales. Se agrupan aquí para ubicar las capacidades del dominio.

| Grupo | Operaciones |
| --- | --- |
| Organización | Registrar personas, departamentos, roles y proyectos. Asignar departamento base, líder y departamento propietario. |
| Conocimiento | Registrar documentos, versiones, clasificación, propietario y vencimiento. Consultar su contexto por proyecto. |
| Activos técnicos | Asociar repositorios, componentes, microservicios y APIs. Registrar dependencias y consultar el impacto de cambios. |
| Gobernanza | Tramitar solicitudes y revisiones, comprobar revisores distintos y segregación del solicitante. |
| Riesgos y trazabilidad | Registrar excepciones, escalamiento, políticas representadas, sincronizaciones, conflictos y eventos de auditoría. |

## Alcance inicial para la entrega integrada

Se propone priorizar la consulta de impacto de una API, la consulta de documentos versionados y la gestión de una solicitud con aprobaciones. Esos flujos permiten demostrar las tres bases y la coordinación desde el backend. Las operaciones de modificación y eliminación o baja deberán definirse por entidad, con sus reglas de integridad y evidencia.

La interfaz, la API y las bases relacional y documental están pendientes de desarrollo dentro del material recibido. La integración con proveedores externos, SSO, correo, respaldos automáticos y calendario laboral necesita una decisión de alcance posterior. El ejemplo de sincronización con Confluence y GitHub representa registros ficticios.

## Reglas del dominio recuperadas

- Una persona tiene un departamento base. Un proyecto tiene un líder y un departamento propietario.
- Una versión pertenece a un documento. Los documentos publicados requieren una versión vigente.
- Una solicitud aprobada requiere al menos dos revisores técnicos distintos. La segregación de funciones excluye al solicitante de la aprobación técnica.
- Una dependencia tiene un origen y un destino identificados.
- Las excepciones tienen autoridad responsable y fecha límite. Los plazos de 48 horas hábiles para criticidad crítica y 72 para alta proceden de propuestas del diseño previo.
- Las políticas por rol y clasificación necesitan aplicación efectiva en las operaciones del backend.

La revisión detectó diferencias entre los datos de aprobación, el propietario documental y la representación de ciertos tipos de dependencia. Su resolución se registra en la [revisión adversaria](revision_adversaria.md).
