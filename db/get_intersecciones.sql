CREATE TABLE IF NOT EXISTS puntos_intersecciones_2 AS
SELECT
    a.ciclovia_id AS ciclovia_a,
    b.ciclovia_id AS ciclovia_b,
    ST_PointOnSurface(ST_Intersection(a.geom, b.geom)) AS interseccion
FROM
    ciclovias a
JOIN
    ciclovias b ON a.ciclovia_id != b.ciclovia_id AND ST_Intersects(a.geom, b.geom);
