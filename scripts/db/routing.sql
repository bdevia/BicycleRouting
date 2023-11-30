DO $$ 
DECLARE
    source_id INT := 889;
    target_id INT := 293;
    distancia_restriccion DOUBLE PRECISION := 0;
BEGIN

    SELECT sum(distancia) INTO distancia_restriccion FROM ruta_mas_corta;

    DROP TABLE IF EXISTS ruta_optima_1;
    CREATE TABLE ruta_optima_1 AS
    SELECT t.*
    FROM pgr_dijkstra(
        'SELECT id, source, target, peso_accidentes + peso_robos + peso_fallas + distancia as cost FROM ciclovia_tramos',
        889,  -- Nodo de origen para la ruta
        293,  -- Nodo de destino para la ruta
        directed := true
    ) AS di
    JOIN ciclovia_tramos t ON di.edge = t.id
    WHERE (
        SELECT sum(optima.distancia)
        FROM (
            SELECT t.*, distancia as distancia_optima
            FROM pgr_dijkstra(
                'SELECT id, source, target, peso_accidentes + peso_robos + peso_fallas + distancia as cost FROM ciclovia_tramos',
                889,  -- Nodo de origen para la segunda ruta
                293,  -- Nodo de destino para la segunda ruta
                directed := true
            ) AS di
            JOIN ciclovia_tramos t ON di.edge = t.id
        ) as optima
    ) < distancia_restriccion * 1.3;

    DROP TABLE IF EXISTS ruta_optima_2;
    CREATE TABLE ruta_optima_2 AS
    SELECT t.*
    FROM pgr_dijkstra(
        'SELECT id, source, target, peso_accidentes + peso_robos + peso_fallas + distancia as cost FROM ciclovia_tramos WHERE id <> 463',
        889,  -- Nodo de origen para la ruta
        293,  -- Nodo de destino para la ruta
        directed := true
    ) AS di
    JOIN ciclovia_tramos t ON di.edge = t.id
    WHERE (
        SELECT sum(optima.distancia)
        FROM (
            SELECT t.*, distancia as distancia_optima
            FROM pgr_dijkstra(
                'SELECT id, source, target, peso_accidentes + peso_robos + peso_fallas + distancia as cost FROM ciclovia_tramos',
                889,  -- Nodo de origen para la segunda ruta
                293,  -- Nodo de destino para la segunda ruta
                directed := true
            ) AS di
            JOIN ciclovia_tramos t ON di.edge = t.id
        ) as optima
    ) < distancia_restriccion * 1.3;

END $$;
