# Relaciones y cardinalidades del grafo

En cada fila, “destinos por origen” expresa el mínimo y máximo de destinos de un nodo origen; “orígenes por destino” expresa la relación inversa. N es un máximo no acotado por el modelo. Son reglas del dominio, no límites físicos impuestos automáticamente por Neo4j.

| Origen | Relación dirigida | Destino | Destinos por origen | Orígenes por destino | Significado |
| --- | --- | --- | --- | --- | --- |
| Persona | PERTENECE_A | Departamento | 1..1 | 0..N | Departamento base |
| Persona | TIENE_ROL | Rol | 1..N | 0..N | Rol vigente |
| Persona | DIRIGE | Departamento | 0..1 | 1..1 | Responsable |
| Persona | LIDERA | Proyecto | 0..N | 1..1 | Líder único por proyecto |
| Persona | PARTICIPA_EN | Proyecto | 0..N | 0..N | Equipo |
| Proyecto | PROPIEDAD_DE | Departamento | 1..1 | 0..N | Departamento propietario |
| VersionDocumento | VERSION_DE | Documento | 1..1 | 1..N | Historial |
| Documento | DOCUMENTA | Proyecto | 1..1 | 0..N | Cobertura |
| Conocimiento | RESPALDADO_POR | Documento | 1..N | 0..N | Evidencia |
| Persona | PROPIETARIO_DE | Documento | 0..N | 1..1 | Responsable documental |
| Repositorio | PERTENECE_A_PROYECTO | Proyecto | 1..1 | 0..N | Contexto |
| Repositorio | CONTIENE | Componente | 0..N | 1..1 | Código |
| Componente | IMPLEMENTA | Microservicio | 1..1 | 0..N | Implementación |
| Microservicio | EXPONE | API | 0..N | 1..1 | Contrato |
| Microservicio | DEPENDE_DE | API | 0..N | 0..N | Recorrido rápido |
| RegistroDependencia | DESDE | Microservicio o Documento | 1..1 unión | 0..N | Origen normalizado |
| RegistroDependencia | HACIA | API | 1..1 | 0..N | Destino normalizado |
| Decision | AFECTA | Proyecto | 1..N | 0..N | Decisión |
| Persona | SOLICITA | SolicitudCambio | 0..N | 1..1 | Solicitante |
| SolicitudCambio | SOBRE | VersionDocumento | 1..1 | 0..N | Objeto |
| Aprobacion | APRUEBA_SOLICITUD | SolicitudCambio | 1..1 | 0..N | Decisión |
| Aprobacion | EMITIDA_POR | Persona | 1..1 | 0..N | Revisor |
| ExcepcionEmergencia | AUTORIZA_TEMPORALMENTE | SolicitudCambio | 1..1 | 0..N | Excepción |
| ExcepcionEmergencia | AUTORIZADA_POR | Persona | 1..1 | 0..N | Autoridad |
| Delegacion | DE | Persona | 1..1 | 0..N | Delegante |
| Delegacion | A | Persona | 1..1 | 0..N | Delegado |
| Conflicto | DETECTADO_EN | SolicitudCambio | 1..1 | 0..N | Contexto |
| Escalamiento | GENERADO_POR | ExcepcionEmergencia | 1..1 | 0..N | Causa |
| Escalamiento | DIRIGIDO_A | Persona | 1..1 | 0..N | Responsable |
| Rol | HABILITA | PoliticaAcceso | 0..N | 1..N | Autorización representada |
| Sincronizacion | DESDE_ORIGEN | SistemaOrigen | 1..1 | 0..N | Fuente |
| Sincronizacion | ACTUALIZA | Repositorio o Documento | 1..N | 0..N | Objeto afectado |
| EventoAuditoria | EJECUTADO_POR | Persona | 0..1 | 0..N | Actor humano |

## Reglas complementarias

DESDE tiene exactamente un destino en la unión Microservicio o Documento: cada tipo individual admite 0..1, pero su suma debe ser 1. HACIA admite exactamente una API. No se permite usar los dos tipos de origen simultáneamente.

DOCUMENTA se restringe a un proyecto por documento en la aplicación integrada, alineado con la FK SQL; el diseño histórico permitía varios. TIENE_ROL admite varios en el modelo conceptual legado, mientras el catálogo operativo SQL asigna un rol por usuario de demostración. La autorización actual consulta SQL, sin inferir permisos adicionales de nodos legados.

Una solicitud puede acumular aprobaciones; APROBADA o PUBLICADA requiere al menos dos técnicas de revisores diferentes y las aprobaciones de propietario y seguridad aplicables. El máximo de una solicitud abierta por versión se hace cumplir en SQL, mientras el historial admite varias solicitudes.

Documento conserva al menos una versión, con máximo una vigente; la baja conserva las versiones retiradas. EJECUTADO_POR es opcional para procesos del sistema en el historial legado. La auditoría actual registra actor_id nulo solo para sistema y un ID humano para acciones autenticadas.

El diagrama lógico resumido representa el núcleo. Este catálogo incluye las 33 relaciones, sus extensiones y las restricciones que el diagrama por sí solo no puede expresar.
