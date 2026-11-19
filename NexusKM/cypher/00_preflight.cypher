// NexusKM 00 - verificación previa. Solo lectura.
CALL dbms.components()
YIELD name, versions, edition
RETURN name, versions, edition;

CALL db.info()
YIELD name
RETURN name AS baseActiva;

RETURN 'NexusKM' AS proyecto,
       'Conexión disponible' AS estado,
       datetime() AS verificadoEn;
