DROP TABLE IF EXISTS ruta_mas_corta;
CREATE TABLE ruta_mas_corta AS
SELECT t.*
FROM pgr_dijkstra(
    'SELECT id, source, target, cost FROM ciclovia_tramos',
    889,  -- Reemplaza con el valor del source de inicio
    107,  -- Reemplaza con el valor del target de llegada
    directed := true
) AS di
JOIN ciclovia_tramos t ON di.edge = t.id;