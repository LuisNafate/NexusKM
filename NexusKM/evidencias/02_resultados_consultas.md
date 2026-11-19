# Resultados principales de las consultas

## Q1. Proyecto, líder y departamento

| Proyecto | Líder | Departamento |
|---|---|---|
| CHECKOUT | Ana López | Desarrollo |
| INVENTARIO | Laura García | Arquitectura |

## Q3. Impacto de Inventory API

| API | Criticidad | Consumidor | Componente | Proyecto |
|---|---|---|---|---|
| Inventory API | CRÍTICA | checkout-service | Adaptador de pagos | Sistema Checkout |

El recorrido completo comprobado fue: `Inventory API` ← `DEPTEC-001` → `checkout-service` ← `Adaptador de pagos` ← `checkout-api` → `Sistema Checkout`.

## Q4. Doble aprobación técnica

| Solicitud | Estado | Revisores técnicos distintos |
|---|---|---|
| SOL-001 | APROBADA | Laura García, Diego Pérez |

## Q5. Excepción temporal

`EXC-001`, criticidad `CRÍTICA`, quedó clasificada como `PRÓXIMA_A_VENCER` al momento de la ejecución.

## Q6. Auditoría

Se reconstruyeron cinco eventos ordenados por fecha: creación de solicitud, dos aprobaciones, una excepción y una sincronización ejecutada por el sistema.

## Q7. Conflicto de sincronización

`SYNC-002` registró un conflicto desde Confluence sobre el documento `Modelo de amenazas checkout`.

## Q8. Política representada

Carlos Ruiz, con el rol Revisor de seguridad, obtuvo la acción representada `LECTURA` para la clasificación `RESTRINGIDO`. Esta relación documenta la política, pero la autorización efectiva corresponde al DBMS y a la aplicación.
