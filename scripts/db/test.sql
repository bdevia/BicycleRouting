DO $$ 
DECLARE
    source_id INT := 889;
    target_id INT := 293;
    distancia_restriccion DOUBLE PRECISION := 100;
    total_distance DOUBLE PRECISION;
    ruta_id INT;
BEGIN
    DROP TABLE IF EXISTS ruta_optima_2;
    CREATE TABLE ruta_optima_2 AS
    SELECT t.*
    FROM pgr_dijkstra(
        'SELECT id, source, target, peso_accidentes + peso_robos + distancia as cost FROM ciclovia_tramos',
        889,  -- Nodo de origen para la ruta
        293,  -- Nodo de destino para la ruta
        directed := true
    ) AS di
    JOIN ciclovia_tramos t ON di.edge = t.id
    WHERE (
        SELECT sum(optima.distancia)
        FROM (
            SELECT t.*
            FROM pgr_dijkstra(
                'SELECT id, source, target, peso_accidentes + peso_robos + distancia as cost FROM ciclovia_tramos',
                889,  -- Nodo de origen para la segunda ruta
                293,  -- Nodo de destino para la segunda ruta
                directed := true
            ) AS di
            JOIN ciclovia_tramos t ON di.edge = t.id
        ) as optima
    ) < 6.835699999999999;
END $$;