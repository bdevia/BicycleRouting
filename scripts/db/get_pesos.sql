--INTERSECCIONES ENTRE CICLOVIA Y ACCIDENTES
CREATE TABLE IF NOT EXISTS interseccion_accidentes AS
SELECT 
    c.tramo_id as tramo_id,
    a.accidente_id,
    ST_PointOnSurface((ST_Dump(ST_Intersection(c.geom, a.geom))).geom) AS interseccion_geom_accidente,
    ROUND((5.0*a.fallecidos + 3.0*a.graves + 2.0*a.menos_grav + a.leves) / a.siniestros, 2) AS peso
FROM 
    ciclovia_tramos AS c
JOIN 
    accidentes AS a ON ST_Intersects(c.geom, a.geom);

CREATE INDEX idx_intersecciones_accidente_geom ON interseccion_accidentes USING GIST (interseccion_geom_accidente);

--INTERSECCIONES ENTRE CICLOVIA Y ROBOS
CREATE TABLE IF NOT EXISTS interseccion_robos AS
SELECT 
    c.tramo_id as tramo_id,
    r.robo_id,
    ST_PointOnSurface((ST_Dump(ST_Intersection(c.geom, r.geom))).geom) AS interseccion_geom_robo,
    ROUND((3.0*CAST(r.robos_V AS INTEGER) + 2.0*CAST(r.robos_f AS INTEGER)) / CAST(r.robos AS INTEGER),2) AS peso
FROM 
    ciclovia_tramos AS c
JOIN 
    robos AS r ON ST_Intersects(c.geom, r.geom);

CREATE INDEX idx_intersecciones_robo_geom ON interseccion_robos USING GIST (interseccion_geom_robo);

--ASIGNAMOS LOS PESOS EN FUNCION DE LAS INTERSECCIONES
ALTER TABLE ciclovia_tramos
ADD COLUMN peso NUMERIC;

-- Actualizar la columna de peso basándote en las intersecciones
UPDATE ciclovia_tramos c
SET peso = (
    COALESCE((
        SELECT SUM(peso)
        FROM interseccion_accidentes
        WHERE c.tramo_id = interseccion_accidentes.tramo_id
    ), 0)
    +
    COALESCE((
        SELECT SUM(peso)
        FROM interseccion_robos
        WHERE c.tramo_id = interseccion_robos.tramo_id
    ), 0)
);

-- Agregar una nueva columna llamada 'distancia' como double precision
ALTER TABLE ciclovia_tramos
ADD COLUMN distancia double precision;

-- Actualizar la columna 'distancia' con la longitud en kilómetros de cada 'MultiLineString'
UPDATE ciclovia_tramos
SET distancia = ROUND(CAST(ST_Length(geom::geography) / 1000.0 AS numeric), 4);

--COMANDOS PARA TENERLOS A MANO
--psql -U postgres -h localhost -d gis
--sudo chown -R benja:sudo ./db/13/main