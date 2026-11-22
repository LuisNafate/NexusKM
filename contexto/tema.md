# Tema y alcance de NexusKM

**Actualizado:** 21 de noviembre de 2026. El usuario eligió NexusKM el 18 de noviembre y pidió completar los entregables el 21 de noviembre. El dominio simula una empresa de software; personas, proyectos y contenidos son ficticios.

NexusKM une Nexus, conexión, y KM, Knowledge Management. El objetivo es conocer el impacto de un cambio técnico, encontrar documentos vigentes y tramitar publicación con responsabilidades y evidencia. Los usuarios son líderes, técnicos, propietarios, seguridad y administración.

La aplicación implementa alta y consulta de documentos, edición de borrador y título, versiones, baja lógica, solicitudes, dos revisores técnicos distintos, aprobación del propietario real y seguridad cuando corresponde, publicación, impacto, auditoría y recuperación de sincronización. [Propuesta completa con 12 RFI](../docs/01-propuesta.md).

Se utiliza PostgreSQL como autoridad de gobierno, MongoDB para contenido anidado y Neo4j para dependencias técnicas. Inventory API → checkout-service → componente → repositorio → CHECKOUT es el recorrido central. Los IDs recibidos se reutilizan.

El inventario técnico y organizacional se carga por scripts. Excepciones, delegaciones, escalamiento y ejemplos Confluence/GitHub son extensiones del modelo anterior, no conectores o calendarios automatizados. SSO y operación productiva quedan fuera de la versión académica local. [Arquitectura y límites](../docs/03-arquitectura.md).

La selección de stack fue una decisión de implementación para completar la tarea autorizada; no se atribuye a una instrucción específica del usuario. Los nombres de integrantes no se han proporcionado.
