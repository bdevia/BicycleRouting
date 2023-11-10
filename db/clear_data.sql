ALTER TABLE IF EXISTS accidentes
DROP COLUMN IF EXISTS fid,
DROP COLUMN IF EXISTS comuna,
DROP COLUMN IF EXISTS año;

ALTER TABLE IF EXISTS robos
DROP COLUMN IF EXISTS fid,
DROP COLUMN IF EXISTS id,
DROP COLUMN IF EXISTS size,
DROP COLUMN IF EXISTS dmcs,
DROP COLUMN IF EXISTS nivel_dmcs,
DROP COLUMN IF EXISTS nivel_robo,
DROP COLUMN IF EXISTS nivel_rf,
DROP COLUMN IF EXISTS nivel_rv;

CREATE TABLE ciclovias AS 
SELECT ciclovia_id, geom, eje, inicio, fin, sentido
FROM "ciclovias_all" WHERE region = 'Metropolitana' AND estado = 'Existentes';
DROP TABLE IF EXISTS "ciclovias_all";




