# Requisitos y entregables académicos

Las referencias de esta página corresponden a las secciones de la [guía oficial](fuentes/Guia_Proyecto_Final_Bases_Datos.pdf), al [anuncio de Classroom](fuentes/anuncio-classroom.png) y a las [diapositivas de clase](fuentes/Modelado%20de%20grafos%20para%20BD.pptx).

## Alcance y reglas de integración

- **Una aplicación para un problema concreto.** Delimitar usuarios, necesidades y operaciones antes de elegir tecnologías. La aplicación puede ser web, móvil o de escritorio. Cada modelo debe cumplir una función justificada en el mismo dominio. Guía §§ 1–4.
- **Operaciones evaluables.** Identificar qué datos sirve, consulta, modifica y elimina la aplicación, y qué servicios requieren esas operaciones. Anuncio de Classroom.
- **Matriz de responsabilidades.** Asignar a cada base sus datos, estructura, operaciones, reglas y pruebas. Identificar dónde se modifica oficialmente cada dato relevante. Cuando haya copias, documentar campos replicados, motivo, mecanismo de sincronización y tratamiento de inconsistencias. Guía § 5.
- **Acceso por el backend.** La interfaz consume una API. Los servicios aplican las reglas del dominio y coordinan repositorios especializados. Demostrar el uso de las tres bases y al menos un flujo de punta a punta que coordine dos o más. Guía §§ 7.6–9 y 11.
- **Escrituras parciales.** Si una operación escribe en varias bases, detectar los fallos parciales y definir cómo reintentar, compensar o reconciliar los cambios. Reportar el fallo conforme a esa estrategia. Guía §§ 5.2 y 9.

## Ocho entregables de la guía

| Entrega | Contenido y evidencia |
| --- | --- |
| **1. Propuesta de aplicación** · § 7.1 | Nombre, descripción, problema, usuarios y necesidades, objetivo, alcance y operaciones prioritarias. Justificación de los tres modelos con un ejemplo de operación para cada uno. |
| **2. Modelado de datos** · § 7.2 | Modelo conceptual común. Modelo relacional con entidades, atributos, claves y cardinalidades. Modelo documental con colecciones, estructura, anidamiento y validaciones. Modelo de grafos con etiquetas, propiedades, tipos de relación, dirección y cardinalidades. Diccionario de datos y reglas del dominio. |
| **3. Arquitectura y selección tecnológica** · § 7.3 | Diagrama y responsabilidades de interfaz, API, servicios y repositorios. Matriz de comparación, tecnologías elegidas y justificación. Fuente de verdad y estrategia de sincronización. |
| **4. Implementación de las tres bases** · § 7.4 | Relacional con tablas, claves, restricciones, índices justificados, scripts SQL de creación y carga, consultas y pruebas de integridad y transacciones. Documental con colecciones, estructura, validaciones, índices, identificadores, carga reproducible, consultas y pruebas de documentos válidos e inválidos. Grafo en Neo4j con etiquetas, propiedades, relaciones, restricciones e índices, scripts Cypher de creación y carga, consultas y pruebas de humo, integridad, cardinalidad y resultados. Las tres bases se deben poder reconstruir desde cero con datos coherentes. |
| **5. Catálogo de operaciones y consultas** · § 7.5 | Identificador, propósito, bases que intervienen, entradas y validaciones, salida esperada y formato, casos normales, límite y de error, evidencia de ejecución y resultado. Incluir operaciones de los tres modelos y consultas integradas según el caso de uso. |
| **6. Backend y API** · § 7.6 | API REST o GraphQL con decisión justificada y contrato documentado. Controladores o resolvers, servicios y repositorios separados. Drivers oficiales, consultas parametrizadas, configuración externa de credenciales, validación, manejo de errores y autorización acorde al alcance. |
| **7. Aplicación e integración** · § 7.7 | Interfaz funcional para los usuarios definidos, flujos que usen cada modelo, caso integrado entre bases y evidencia de que cambios y consultas se reflejan según la estrategia de consistencia. |
| **8. Pruebas, documentación y despliegue** · § 7.8 | Pruebas unitarias o de componentes, por base, funcionales y de integración. Evidencia de manejo de errores, consistencia y rendimiento básico. Instrucciones de instalación, configuración, carga y ejecución. Variables de entorno de ejemplo sin credenciales reales, repositorio y demostración funcional. |

## Actividad de refuerzo del grafo

La diapositiva 10 pide los siguientes productos para el modelo lógico. Usa el tema de tu aplicación para elaborarlos e incorpora su evidencia al entregable de modelado.

- [ ] Tabla con **al menos 8 requerimientos funcionales y 5 consultas**. Al menos 2 consultas deben involucrar relaciones entre 3 o más entidades.
- [ ] Diccionario con **al menos 3 propiedades por entidad**. Indicar nombre, tipo de dato, obligatoriedad y unicidad.
- [ ] Catálogo con entidad origen, nombre de la relación, entidad destino y significado.
- [ ] Tabla con **al menos 8 restricciones de integridad**.
- [ ] Tabla con mínimo y máximo en ambos extremos de cada relación.
- [ ] Diagrama del modelo lógico.
- [ ] Conclusiones que expliquen por qué enumerar entidades es insuficiente y cómo influyen las consultas, restricciones y cardinalidades.

Para diseñar el grafo, parte de las preguntas de la aplicación, identifica los recorridos y define qué propiedades describen los nodos y cuáles describen las relaciones. Diapositivas 2–9. La guía, § 6.2, también vincula las actividades de refuerzo con la propuesta, la arquitectura, la selección tecnológica, la especificación del servicio, la implementación en Neo4j, el catálogo Cypher y el backend.

## Pruebas de integración

Según la guía § 9, conservar evidencia de conectividad del backend a los tres motores, operaciones funcionales, integridad de cada modelo, un flujo de extremo a extremo entre bases, consistencia de actualizaciones, manejo de errores y mediciones de rendimiento con el entorno y los datos descritos.

La guía § 10 presenta una estructura de repositorio adaptable. La organización definitiva se elige con el stack y se documenta junto con las instrucciones de ejecución.
