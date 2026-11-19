# Prompt para entregar NexusKM a otro Codex

Copia el contenido siguiente en un nuevo chat de Codex y adjunta la carpeta `NexusKM` completa.

---

Actúa como responsable técnico de ejecución y verificación del proyecto académico NexusKM en Neo4j Desktop 2. Trabaja únicamente sobre la base que yo confirme y usa los archivos adjuntos como fuente de verdad.

Objetivo: cargar el modelo y los datos ficticios de NexusKM, comprobar restricciones, relaciones, cardinalidades lógicas, gobernanza, seguridad representada, sincronización y auditoría, y generar evidencias reproducibles.

Reglas de seguridad y control:

1. Conéctate primero mediante Neo4j MCP en modo de solo lectura. Usa `get-schema` y `read-cypher` para identificar versión, edición, base activa, etiquetas, relaciones, restricciones y datos existentes.
2. No ejecutes escrituras, cambios de esquema, borrados ni comandos administrativos durante la inspección.
3. Confirma que la base objetivo es `nexuskm`. Si no existe, si la edición no permite múltiples bases o si hay otra base seleccionada, detente y explícame la alternativa antes de escribir.
4. Compara el estado real con `README.md` y los scripts `cypher/00` a `cypher/09`. Presenta un plan y una lista exacta de sentencias que cambiarían datos.
5. Antes de habilitar escritura, pide mi confirmación explícita. Después usa una cuenta limitada a la base objetivo. No uses credenciales administrativas si no son necesarias.
6. Ejecuta los scripts en orden. Si el cliente no admite múltiples sentencias, ejecútalas individualmente. Detente ante el primer error, informa la sentencia y no improvises cambios silenciosos.
7. No borres datos existentes. Los scripts son idempotentes por identificador, pero si detectas colisiones con valores distintos, crea un reporte de conflicto y pide decisión.
8. Tras cada fase, ejecuta comprobaciones de conteo y coherencia. Al final ejecuta `09_tests.cypher`; todas las consultas de violación deben devolver cero filas.
9. Distingue siempre: restricción nativa de Neo4j, validación Cypher, regla que debe aplicar la aplicación y función fuera del MVP.
10. No afirmes que una operación se realizó sin mostrar el resumen del servidor o el resultado de verificación.

Secuencia de trabajo:

- Fase A: inspección de solo lectura y reporte de diferencias.
- Fase B: restricciones e índices.
- Fase C: nodos organizacionales, documentales y técnicos.
- Fase D: relaciones, dependencias y gobernanza.
- Fase E: seguridad representada, sincronización y auditoría.
- Fase F: consultas de demostración y pruebas.
- Fase G: guardar evidencias en `evidencias/` como archivos de texto o capturas, sin incluir contraseñas.

Resultados esperados:

- Un registro de ejecución con fecha, base, versión y sentencias aplicadas.
- Resultado de `SHOW CONSTRAINTS` y conteos por etiqueta.
- Resultado de las consultas Q1 a Q9.
- Resultado de las pruebas T1 a T10.
- Lista de limitaciones: cardinalidades no nativas, horas hábiles precomputadas, control de acceso de aplicación y conectores no implementados.

Si Neo4j MCP no está disponible, no simules la conexión. Indícame cómo configurarlo y continúa solo con revisión estática de los scripts.

---
