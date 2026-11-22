# Entregables de NexusKM

![Modelos](https://img.shields.io/badge/modelos-3-1d5fbf) ![Pruebas](https://img.shields.io/badge/pruebas-39%20aprobadas-23734a) ![Corte](https://img.shields.io/badge/evidencia-21%20nov%202026-555555)

Los ocho documentos describen la aplicación integrada implementada. El informe y la presentación de [entrega](../entrega/) reúnen el contenido para revisión académica. La guía del profesor es la fuente de requisitos; los antecedentes de `NexusKM/` conservan el trabajo del grafo recibido.

| Entregable | Documento | Evidencia principal |
| --- | --- | --- |
| 1 | [Propuesta](01-propuesta.md) | Problema, usuarios, alcance y 12 requisitos |
| 2 | [Modelos](02-modelado.md) | Conceptual, SQL, documental, grafo y diccionarios |
| 3 | [Arquitectura](03-arquitectura.md) | Decisiones, comparación y consistencia |
| 4 | [Bases implementadas](04-implementacion.md) | Esquemas, cargas e índices ejecutables |
| 5 | [Operaciones y consultas](05-operaciones.md) | Catálogo y resultados de los tres modelos |
| 6 | [Backend y API](06-api.md) | Contrato REST, validaciones y seguridad |
| 7 | [Aplicación integrada](07-aplicacion.md) | Capturas reales y recorrido de usuario |
| 8 | [Pruebas y manual](08-pruebas-y-manual.md) | 39 pruebas, fallos parciales y ejecución |

[Diccionario SQL](modelos/diccionario-relacional.md) · [Diccionario del grafo](modelos/diccionario-grafo.md) · [Relaciones y cardinalidades](modelos/relaciones-grafo.md) · [Matriz de pruebas](pruebas/matriz.md) · [Guion de demostración](demo.md) · [Referencias](referencias.md)

## Evidencia verificable

- [Verificación actual](pruebas/evidencias/verificacion-integrada.json): versiones de motores, resultados Q1–Q9, T1–T13, S1–S5 y D1–D4, respuesta integrada y mediciones.
- [JUnit](pruebas/evidencias/pytest.xml): 39 pruebas, cero fallos, errores y omisiones.
- [Carga inicial](pruebas/evidencias/verificacion-carga.json): instantánea anterior a la demostración en navegador.
- [Interfaz](pruebas/evidencias/ui-verificacion.json): flujos y resoluciones comprobados.
- [Contrato OpenAPI](api/openapi.json): contrato exportado del código ejecutado.

Los resultados del 12 de noviembre bajo `NexusKM/evidencias/` son históricos. Los archivos de esta carpeta corresponden a una ejecución actual sobre Docker con datos ficticios. No contienen contraseñas ni tokens de sesión.
