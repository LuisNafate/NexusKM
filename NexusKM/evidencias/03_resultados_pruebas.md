# Resultados de pruebas de coherencia

Las pruebas T1 a T9 son consultas de violación. Todas devolvieron cero filas.

| Prueba | Regla comprobada | Resultado |
|---|---|---|
| T1 | Una persona pertenece exactamente a un departamento | 0 violaciones |
| T2 | Un proyecto tiene exactamente un departamento propietario | 0 violaciones |
| T3 | Un proyecto tiene exactamente un líder | 0 violaciones |
| T4 | Una versión pertenece exactamente a un documento | 0 violaciones |
| T5 | Una solicitud aprobada tiene dos revisores técnicos distintos | 0 violaciones |
| T6 | El solicitante no se aprueba técnicamente a sí mismo | 0 violaciones |
| T7 | Una dependencia registrada tiene un origen y un destino | 0 violaciones |
| T8 | Una excepción crítica respeta el máximo declarado de 48 horas | 0 violaciones |
| T9 | Un documento publicado tiene una versión vigente | 0 violaciones |

T10 devolvió los conteos finales: 63 nodos y 87 relaciones.

Estas pruebas validan el conjunto cargado. No convierten todas las cardinalidades en restricciones nativas del motor; la aplicación debe seguir protegiendo las escrituras dentro de una transacción.
