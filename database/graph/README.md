# Persistencia de grafos

La fuente de los scripts es [NexusKM/cypher](../../NexusKM/cypher). El bootstrap ejecuta 01 a 07 sobre el motor de grafos del entorno integrado. Las consultas están en 08 y las validaciones en 09.

PostgreSQL mantiene el catálogo y la gobernanza oficial. La clase GraphRepository actualiza las proyecciones de documentos, versiones, solicitudes y aprobaciones mediante transacciones de Neo4j. Los activos técnicos y las dependencias mantienen su fuente de verdad en el grafo.

La base del contenedor Community se llama neo4j y se expone en el puerto local 57687. La instancia histórica nexuskm de Neo4j Desktop conserva su evidencia en el paquete original.
