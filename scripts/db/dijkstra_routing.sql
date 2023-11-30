CREATE TABLE ruta_mas_corta AS
SELECT t.*
FROM pgr_dijkstra(
    'SELECT id, source, target, distancia as cost FROM ciclovia_tramos',
    889,  -- Reemplaza con el valor del source de inicio
    293,  -- Reemplaza con el valor del target de llegada
    directed := true
) AS di
JOIN ciclovia_tramos t ON di.edge = t.id;

CREATE TABLE segunda_ruta_mas_corta AS
SELECT t.*
FROM pgr_dijkstra(
    'SELECT id, source, target, distancia as cost FROM ciclovia_tramos WHERE id <> 463',
    889,  -- Nodo de origen para la segunda ruta
    293,  -- Nodo de destino para la segunda ruta
    directed := true
) AS di
JOIN ciclovia_tramos t ON di.edge = t.id;