# 8 Pruebas y manual de ejecución

La validación actual utiliza tres motores reales en Docker, API HTTP, pruebas de servicio y revisión de interfaz. **39 pruebas automatizadas aprobaron, sin fallos, errores ni omisiones**. Los resultados históricos del grafo se conservan aparte y no se usan como sustituto de esta ejecución.

## Instalación y arranque

Se necesita Docker Desktop con motor Linux y Docker Compose v2, PowerShell y un navegador. La primera construcción requiere acceso a los registros de imágenes y paquetes. Como referencia operativa se aconsejan 4 GB de memoria disponibles para Docker y varios GB de disco; no se ha medido un mínimo garantizado. Los puertos predeterminados deben estar libres.

```powershell
git clone https://github.com/LuisNafate/NexusKM.git
Set-Location NexusKM
powershell -ExecutionPolicy Bypass -File scripts/start.ps1
```

El script genera `.env` con secretos aleatorios si no existe, construye la imagen, inicia cuatro servicios y espera salud. No requiere Python instalado en el host. Abre `http://localhost:58000`; contrato interactivo `http://localhost:58000/docs`; salud `http://localhost:58000/api/health`.

Acceso: `PER-002` para Carlos. Consulta **DEMO_PASSWORD en tu `.env` local**. No compartas ese archivo. Los usuarios ficticios son PER-001 Ana/LIDER, PER-002 Carlos/SEGURIDAD, PER-003 Laura/TECNICO, PER-004 Miguel/ADMIN, PER-005 Sofía/PROPIETARIO y PER-006 Diego/TECNICO. Todos reciben esa contraseña de demostración en la primera carga.

| Variable | Contrato y valor de ejemplo |
| --- | --- |
| POSTGRES_DB / POSTGRES_USER | nexuskm / nexuskm |
| POSTGRES_PASSWORD | Secreto local generado |
| POSTGRES_PORT | 55432 en host; 5432 en la red Compose |
| MONGO_USER / MONGO_PASSWORD | nexuskm / secreto generado |
| MONGO_PORT | 57017 en host; 27017 interno |
| NEO4J_USER / NEO4J_PASSWORD | neo4j / secreto generado |
| NEO4J_BOLT_PORT / NEO4J_HTTP_PORT | 57687 / 57474 en host |
| APP_PORT | 58000 en host; 8000 interno |
| TOKEN_SECRET | Secreto aleatorio para firma |
| DEMO_PASSWORD | Contraseña inicial de los seis usuarios ficticios |

`.env.example` documenta estos nombres con valores de reemplazo. La aplicación admite variables de host para desarrollo y Compose las dirige a los servicios internos. Los datos quedan en volúmenes; reiniciar no reescribe la carga. No ejecutar los seeds Cypher manualmente sobre una base con cambios.

## Operación y diagnóstico

```powershell
docker compose ps
docker compose logs --tail 60 app
powershell -ExecutionPolicy Bypass -File scripts/test.ps1
powershell -ExecutionPolicy Bypass -File scripts/stop.ps1
```

`test.ps1` detiene temporalmente la app, ejecuta pytest en un contenedor aislado del servidor pero conectado a las tres bases y reinicia la app en finally. Esto evita que el worker normal consuma el evento de fallo parcial durante el test. No ejecutar durante una edición de usuario. Las pruebas crean IDs propios y limpian solo esos registros; conservan el seed y la demostración UI.

Si Docker no responde, abre Docker Desktop y espera el motor. Si un puerto está ocupado, cambia su variable antes de arrancar. Ante 202 o aviso pendiente, usa PER-004 en el panel de sincronización o espera el worker; no recrees el documento. Si hay 409 por revisión, recarga. Si expiró el token, inicia sesión otra vez. Los logs no deben copiarse con secretos de configuración.

Para detener conservando información usa `stop.ps1`. Eliminar volúmenes es una acción distinta y destruye esa instalación; no forma parte del apagado normal. Para probar una instalación limpia se usa otro nombre de proyecto y puertos, conservando el entorno principal.

## Cobertura y evidencia

| Nivel | Casos representativos | Evidencia |
| --- | --- | --- |
| Componentes | Token inválido/vencido, validación de contenido, idempotencia | tests/test_integration.py |
| PostgreSQL | FK, unicidad de vigente, rollback, concurrencia | JUnit y esquema consultado |
| MongoDB | Documento inválido y objeto anidado con tipo incorrecto | Pruebas contra validador real |
| Neo4j | Unicidad, T1–T13, conteos positivos y Q2 | JSON con consulta y salida completa |
| Integración | Crear/editar/baja en tres motores, aprobación/publicación, impacto | 39 pruebas con drivers reales |
| Recuperación | Fallo inyectado Neo4j después de Mongo, outbox pendiente, reintento | Caso de sincronización e idempotencia |
| Interfaz | Login, impacto, CRUD, publicación, auditoría y móvil | Capturas reales y ui-verificacion.json |
| Reconstrucción | Volúmenes nuevos, carga completa y reinicio sin sobrescritura | reconstruccion.json |

El fallo parcial utiliza una excepción controlada del repositorio; no se afirma haber medido toda clase de fallo de red. Las pruebas de concurrencia comprueban un ganador y un conflicto de revisión. La matriz completa se genera desde los nombres de las 39 pruebas en [matriz.md](pruebas/matriz.md).

## Rendimiento básico

Se midieron 30 solicitudes secuenciales por operación con un cliente HTTP local autenticado, sin carga concurrente y con datos de demostración. Se usa mediana y percentil 95 por rango más cercano. La tabla de resultados actual se encuentra en [resultados.md](pruebas/resultados.md); cada duración completa de resumen y las versiones exactas de motor están en `verificacion-integrada.json`. Estas medidas describen este equipo y conjunto pequeño; no prueban capacidad productiva ni superioridad entre motores.

## Entrega y mantenimiento

El [guion de demostración](demo.md) describe un recorrido repetible. El [índice](README.md) enlaza los ocho entregables y la carpeta `entrega/` reúne informe editable, PDF, presentación y paquete. Se conserva el historial del paquete recibido en `contexto/migracion.json`; sus hashes describen la versión de origen, mientras Git registra las correcciones posteriores.

La guía proporcionada el 21 de noviembre coincide por SHA-256 con la guía ya organizada y conserva los mismos criterios. La aplicación está preparada localmente y el repositorio comparte código. El registro de integrantes y el envío a Classroom corresponden al equipo.
