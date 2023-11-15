--BUSQUEDA DE INTERSECCIONES ENTRE LAS CICLOVIAS
CREATE TABLE IF NOT EXISTS intersecciones_ciclovias AS
SELECT
    a.ciclovia_id AS ciclovia_a,
    b.ciclovia_id AS ciclovia_b,
    ST_PointOnSurface(ST_Intersection(a.geom, b.geom)) AS interseccion
FROM
    ciclovias a
JOIN
    ciclovias b ON a.ciclovia_id < b.ciclovia_id AND ST_Intersects(a.geom, b.geom);

--BUSQUEDA DE PUNTOS EXTREMOS
DROP TABLE IF EXISTS extremo_ini;
CREATE TABLE extremo_ini AS
SELECT
  ciclovia_id,
  ST_StartPoint((ST_Dump(geom)).geom)::geometry(PointZ) AS inicio_punto
FROM
  ciclovias
WHERE
  ST_NumGeometries(geom) > 0;

DROP TABLE IF EXISTS extremo_fin;
CREATE TABLE extremo_fin AS
SELECT
  ciclovia_id,
  ST_EndPoint((ST_Dump(geom)).geom)::geometry(PointZ) AS fin_punto
FROM
  ciclovias
WHERE
  ST_NumGeometries(geom) > 0;
