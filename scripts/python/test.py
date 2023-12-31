import sys
import psycopg2
import os
import json

def ejecutar_consulta(source, target, option):
    conn_params = {
        'dbname': 'gis',
        'user': 'postgres',
        'password': 'postgres',
        'host': 'localhost',
        'port': '25432'
    }
    try:
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()

        consulta_1 = f"SELECT t.* FROM pgr_dijkstra('SELECT id, source, target, distancia as cost FROM ciclovia_tramos', {source}, {target}, directed := {True}) AS di JOIN ciclovia_tramos t ON di.edge = t.id;"
        consulta_2 = f"SELECT t.* FROM pgr_dijkstra('SELECT id, source, target, distancia as cost FROM ciclovia_tramos WHERE id <> 463', {source}, {target}, directed := {True}) AS di JOIN ciclovia_tramos t ON di.edge = t.id;"
            
        if option == 'secure':
            consulta_3 = f"SELECT t.* FROM pgr_dijkstra('SELECT id, source, target, peso_accidentes + peso_robos + peso_fallas + distancia as cost FROM ciclovia_tramos', {source}, {target}, directed := {True}) AS di JOIN ciclovia_tramos t ON di.edge = t.id;"
            consulta_4 = f"SELECT t.* FROM pgr_dijkstra('SELECT id, source, target, peso_accidentes + peso_robos + peso_fallas + distancia as cost FROM ciclovia_tramos WHERE id <> 463', {source}, {target}, directed := {True}) AS di JOIN ciclovia_tramos t ON di.edge = t.id;"

        elif option == 'default':
            consulta_3 = f"SELECT t.* FROM pgr_dijkstra('SELECT id, source, target, peso_accidentes + peso_fallas + distancia as cost FROM ciclovia_tramos', {source}, {target}, directed := {True}) AS di JOIN ciclovia_tramos t ON di.edge = t.id;"
            consulta_4 = f"SELECT t.* FROM pgr_dijkstra('SELECT id, source, target, peso_accidentes + peso_fallas + distancia as cost FROM ciclovia_tramos WHERE id <> 463', {source}, {target}, directed := {True}) AS di JOIN ciclovia_tramos t ON di.edge = t.id;"

        else:
            print("Opción no válida. Debes proporcionar el modo de ejecucion ('default' o 'secure' ")
            return None

        
        # Ejecuta las consultas y obtén los resultados
        cursor.execute(consulta_1)
        resultados_1 = cursor.fetchall()
        
        cursor.execute(consulta_2)
        resultados_2 = cursor.fetchall()
        
        cursor.execute(consulta_3)
        resultados_3 = cursor.fetchall()
        
        cursor.execute(consulta_4)
        resultados_4 = cursor.fetchall()

        return resultados_1, resultados_2, resultados_3, resultados_4

    except psycopg2.Error as e:
        print(f"Error de PostgreSQL: {e}")
        return None

    finally:
        # Cierra la conexión
        if conn:
            conn.close()
            
def filtrar_features_por_ids(features, ids):
    return [feature for feature in features if feature['properties']['id'] in ids]


if __name__ == "__main__":
    # Verifica que se proporcionen los argumentos correctos
    if len(sys.argv) != 4:
        print("Uso: python consulta_postgres.py source target option")
        sys.exit(1)

    # Obtiene los argumentos de la línea de comandos
    source = sys.argv[1]
    target = sys.argv[2]
    option = sys.argv[3]

    input_file_path = '../../metadata/ciclovias/ciclovia_tramos_pesos.geojson'
    directorio_salida = '../../data/rutas'
    
    # Leer el archivo GeoJSON de entrada
    with open(input_file_path, "r") as infile:
        ciclovias_tramos = json.load(infile)
        
    resultados_1, resultados_2, resultados_3, resultados_4 = ejecutar_consulta(source, target, option)

    for i, resultados in enumerate([resultados_1, resultados_2, resultados_3, resultados_4], start=1):
        if resultados:
            # Convertir los IDs a una lista de enteros
            ids_enteros = [id_[0] for id_ in resultados]

            # Filtrar las características por los IDs obtenidos
            features_resultantes = filtrar_features_por_ids(ciclovias_tramos['features'], ids_enteros)

            # Crear un nuevo GeoJSON con las características resultantes
            resultado_geojson = {
                "type": "FeatureCollection",
                "features": features_resultantes
            }

            # Escribir el resultado a un nuevo archivo GeoJSON
            nombre_archivo = os.path.join(directorio_salida, f"ruta_{i}.geojson")
            with open(nombre_archivo, "w") as outfile:
                json.dump(resultado_geojson, outfile, indent=2)

            print(f"Se ha creado el archivo {nombre_archivo} con la ruta {i} .")
        else:
            print(f"No se obtuvieron IDs de la consulta {i}.")