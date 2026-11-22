# Diccionario completo del grafo

Las 23 etiquetas tienen al menos tres propiedades definidas. La obligatoriedad es un contrato de modelo; Neo4j Community aplica unicidad nativa y el servicio controla las escrituras del alcance. La existencia de todas las propiedades del catálogo legado no se presenta como constraint nativa. Los campos de extensión histórica solo corresponden a la carga del grafo anterior; solicitudes nuevas usan el subconjunto operativo indicado.

## Departamento

| Propiedad | Tipo | Obligatoria | Única | Semántica |
| --- | --- | --- | --- | --- |
| departamentoId | String | Sí | Sí | Identificador único DEP-### |
| nombre | String | Sí | No | Nombre visible |
| descripcion | String | No | No | Responsabilidad |
| estado | Enum | Sí | No | ACTIVO o INACTIVO |

## Persona

| Propiedad | Tipo | Obligatoria | Única | Semántica |
| --- | --- | --- | --- | --- |
| personaId | String | Sí | Sí | Identificador único PER-### |
| nombre | String | Sí | No | Nombre ficticio |
| correo | String | Sí | Sí | Correo único |
| estado | Enum | Sí | No | ACTIVO o INACTIVO |

## Rol

| Propiedad | Tipo | Obligatoria | Única | Semántica |
| --- | --- | --- | --- | --- |
| rolId | String | Sí | Sí | Identificador único |
| nombre | String | Sí | No | Función de gobernanza |
| descripcion | String | Sí | No | Responsabilidad representada por el rol |

## Proyecto

| Propiedad | Tipo | Obligatoria | Única | Semántica |
| --- | --- | --- | --- | --- |
| proyectoId | String | Sí | Sí | Identificador único |
| codigo | String | Sí | No | Código corto |
| nombre | String | Sí | No | Nombre del proyecto |
| descripcion | String | No | No | Objetivo |
| estado | Enum | Sí | No | ACTIVO o CERRADO |

## Conocimiento

| Propiedad | Tipo | Obligatoria | Única | Semántica |
| --- | --- | --- | --- | --- |
| conocimientoId | String | Sí | Sí | Identificador |
| nombre | String | Sí | No | Tema |
| tipo | Enum | Sí | No | OPERATIVO, TECNICO o SEGURIDAD |
| estado | Enum | Sí | No | VIGENTE u OBSOLETO |

## Documento

| Propiedad | Tipo | Obligatoria | Única | Semántica |
| --- | --- | --- | --- | --- |
| documentoId | String | Sí | Sí | Identificador |
| titulo | String | Sí | No | Título |
| tipo | Enum | Sí | No | RUNBOOK, API o SEGURIDAD |
| clasificacion | Enum | Sí | No | INTERNO o RESTRINGIDO |
| estado | Enum | Sí | No | EN_REVISION, PUBLICADO o RETIRADO; derivado de SQL |
| activo | Boolean | Sí en proyección integrada | No | Baja lógica SQL |
| revision | Integer | Sí en proyección integrada | No | Revisión de metadatos positiva |

## VersionDocumento

| Propiedad | Tipo | Obligatoria | Única | Semántica |
| --- | --- | --- | --- | --- |
| versionId | String | Sí | Sí | Identificador |
| numero | String | Sí | No | Versión semántica |
| estado | Enum | Sí | No | BORRADOR, EN_REVISION, VIGENTE o RETIRADA |
| fechaPublicacion | DateTime | Condicional | No | Nula en borrador |
| fechaVencimiento | DateTime | Sí | No | Revisión obligatoria |

## Repositorio

| Propiedad | Tipo | Obligatoria | Única | Semántica |
| --- | --- | --- | --- | --- |
| repositorioId | String | Sí | Sí | Identificador |
| nombre | String | Sí | No | Nombre |
| url | String | Sí | No | URL ficticia |
| estado | Enum | Sí | No | ACTIVO |

## Componente

| Propiedad | Tipo | Obligatoria | Única | Semántica |
| --- | --- | --- | --- | --- |
| componenteId | String | Sí | Sí | Identificador |
| nombre | String | Sí | No | Nombre |
| tipo | Enum | Sí | No | MODULO o LIBRERIA |
| estado | Enum | Sí | No | ACTIVO |

## Microservicio

| Propiedad | Tipo | Obligatoria | Única | Semántica |
| --- | --- | --- | --- | --- |
| servicioId | String | Sí | Sí | Identificador |
| nombre | String | Sí | No | Nombre |
| criticidad | Enum | Sí | No | ALTA o CRITICA |
| estado | Enum | Sí | No | ACTIVO |

## API

| Propiedad | Tipo | Obligatoria | Única | Semántica |
| --- | --- | --- | --- | --- |
| apiId | String | Sí | Sí | Identificador |
| nombre | String | Sí | No | Nombre |
| version | String | Sí | No | Versión |
| protocolo | Enum | Sí | No | REST |
| estado | Enum | Sí | No | ACTIVA |

## Decision

| Propiedad | Tipo | Obligatoria | Única | Semántica |
| --- | --- | --- | --- | --- |
| decisionId | String | Sí | Sí | Identificador |
| titulo | String | Sí | No | Decisión de arquitectura |
| fecha | Date | Sí | No | Fecha |
| estado | Enum | Sí | No | ACEPTADA |

## RegistroDependencia

| Propiedad | Tipo | Obligatoria | Única | Semántica |
| --- | --- | --- | --- | --- |
| dependenciaId | String | Sí | Sí | Identificador |
| tipo | Enum | Sí | No | API o DATOS |
| criticidad | Enum | Sí | No | ALTA o CRITICA |
| descripcion | String | Sí | No | Motivo |
| estado | Enum | Sí | No | ACTIVA |

## SolicitudCambio

| Propiedad | Tipo | Obligatoria | Única | Semántica |
| --- | --- | --- | --- | --- |
| solicitudId | String | Sí | Sí | Identificador |
| titulo | String | Sí | No | Texto de contexto de la solicitud; generado en proyección |
| estado | Enum | Sí | No | PENDIENTE, APROBADA, PUBLICADA o CANCELADA |
| criticidad | Enum | Solo extensión histórica | No | ALTA o CRITICA |
| creadaEn | DateTime | Sí | No | Inicio |
| fechaLimite | DateTime | Solo extensión histórica | No | SLA precomputado |

## Aprobacion

| Propiedad | Tipo | Obligatoria | Única | Semántica |
| --- | --- | --- | --- | --- |
| aprobacionId | String | Sí | Sí | Identificador |
| tipo | Enum | Sí | No | TECNICA, SEGURIDAD o PROPIETARIO |
| decision | Enum | Sí | No | APROBADA o RECHAZADA |
| fecha | DateTime | Sí | No | Momento |

## ExcepcionEmergencia

| Propiedad | Tipo | Obligatoria | Única | Semántica |
| --- | --- | --- | --- | --- |
| excepcionId | String | Sí | Sí | Identificador |
| motivo | String | Sí | No | Justificación |
| criticidad | Enum | Sí | No | ALTA o CRITICA |
| estado | Enum | Sí | No | VIGENTE, CERRADA o VENCIDA |
| inicio | DateTime | Sí | No | Inicio |
| fechaLimite | DateTime | Sí | No | Límite precomputado |
| horasHabilesAprobadas | Integer | Sí | No | 48 o 72 |

## Delegacion

| Propiedad | Tipo | Obligatoria | Única | Semántica |
| --- | --- | --- | --- | --- |
| delegacionId | String | Sí | Sí | Identificador |
| desde | DateTime | Sí | No | Inicio |
| hasta | DateTime | Sí | No | Fin |
| estado | Enum | Sí | No | ACTIVA o VENCIDA |

## Conflicto

| Propiedad | Tipo | Obligatoria | Única | Semántica |
| --- | --- | --- | --- | --- |
| conflictoId | String | Sí | Sí | Identificador |
| tipo | Enum | Sí | No | Tipo de conflicto |
| estado | Enum | Sí | No | ABIERTO o RESUELTO |
| descripcion | String | Sí | No | Detalle |

## Escalamiento

| Propiedad | Tipo | Obligatoria | Única | Semántica |
| --- | --- | --- | --- | --- |
| escalamientoId | String | Sí | Sí | Identificador |
| motivo | String | Sí | No | Causa |
| estado | Enum | Sí | No | PENDIENTE o ATENDIDO |
| creadoEn | DateTime | Sí | No | Momento |

## EventoAuditoria

| Propiedad | Tipo | Obligatoria | Única | Semántica |
| --- | --- | --- | --- | --- |
| eventoId | String | Sí | Sí | Identificador |
| tipo | Enum | Sí | No | Operación |
| entidad | String | Sí | No | Etiqueta lógica |
| entidadId | String | Sí | No | ID afectado |
| fecha | DateTime | Sí | No | Momento |

## SistemaOrigen

| Propiedad | Tipo | Obligatoria | Única | Semántica |
| --- | --- | --- | --- | --- |
| origenId | String | Sí | Sí | Identificador |
| nombre | String | Sí | No | Fuente |
| tipo | Enum | Sí | No | REPOSITORIO o DOCUMENTACION |

## Sincronizacion

| Propiedad | Tipo | Obligatoria | Única | Semántica |
| --- | --- | --- | --- | --- |
| sincronizacionId | String | Sí | Sí | Identificador |
| inicio | DateTime | Sí | No | Inicio |
| fin | DateTime | Sí | No | Fin |
| estado | Enum | Sí | No | EXITOSA o CONFLICTO |

## PoliticaAcceso

| Propiedad | Tipo | Obligatoria | Única | Semántica |
| --- | --- | --- | --- | --- |
| politicaId | String | Sí | Sí | Identificador |
| clasificacion | Enum | Sí | No | INTERNO o RESTRINGIDO |
| accion | Enum | Sí | No | LECTURA o APROBAR |

## Contrato de las proyecciones actuales

SolicitudCambio nueva conserva solicitudId, titulo, estado y creadaEn. criticidad y fechaLimite son atributos de la extensión histórica, sin SLA automatizado. Aprobacion conserva aprobacionId, tipo, decision y fecha. Documento se construye desde SQL con activo y revision; VersionDocumento conserva número, estado y fechas. No se transfieren contraseñas o tokens al grafo.

Propiedades de DEPENDE_DE: dependenciaId (String obligatorio, identidad lógica de la conexión) y criticidad (Enum ALTA o CRITICA). Se hace MERGE por identidad y SET de criticidad. Los demás tipos de relación no requieren propiedades en este modelo. La correspondencia de DEPENDE_DE con RegistroDependencia debe preservarse al mantener el seed; la API de esta entrega no edita dependencias.
