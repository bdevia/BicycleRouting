--INTERSECCIONES ENTRE CICLOVIA Y ACCIDENTES
CREATE TABLE IF NOT EXISTS interseccion_accidentes AS
SELECT 
    c.ciclovia_id,
    a.accidente_id,
    ST_PointOnSurface((ST_Dump(ST_Intersection(c.geom, a.geom))).geom) AS interseccion_geom_accidente,
    ROUND((5.0*a.fallecidos + 3.0*a.graves + 2.0*a.menos_grav + a.leves) / a.siniestros, 2) AS peso
FROM 
    ciclovias AS c
JOIN 
    accidentes AS a ON ST_Intersects(c.geom, a.geom);

CREATE INDEX idx_intersecciones_accidente_geom ON interseccion_accidentes USING GIST (interseccion_geom_accidente);

--INTERSECCIONES ENTRE CICLOVIA Y ROBOS
CREATE TABLE IF NOT EXISTS interseccion_robos AS
SELECT 
    c.ciclovia_id,
    r.robos_id,
    ST_PointOnSurface((ST_Dump(ST_Intersection(c.geom, r.geom))).geom) AS interseccion_geom_robo,
    ROUND((3.0*CAST(r.robos_V AS INTEGER) + 1.0*CAST(r.robos_f AS INTEGER)) / CAST(r.robos AS INTEGER),2) AS peso
FROM 
    ciclovias AS c
JOIN 
    robos AS r ON ST_Intersects(c.geom, r.geom);

CREATE INDEX idx_intersecciones_robo_geom ON interseccion_robos USING GIST (interseccion_geom_robo);

--ASIGNAMOS LOS PESOS EN FUNCION DE LAS INTERSECCIONES
ALTER TABLE ciclovias
ADD COLUMN peso NUMERIC;

-- Actualizar la columna de peso basándote en las intersecciones
UPDATE ciclovias c
SET peso = (
    COALESCE((
        SELECT SUM(peso)
        FROM interseccion_accidentes
        WHERE c.ciclovia_id = interseccion_accidentes.ciclovia_id
    ), 0)
    +
    COALESCE((
        SELECT SUM(peso)
        FROM interseccion_robos
        WHERE c.ciclovia_id = interseccion_robos.ciclovia_id
    ), 0)
);

--psql -U postgres -h localhost -d gis