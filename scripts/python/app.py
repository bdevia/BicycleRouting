import sys
import psycopg2
import json

def ejecutar_consulta(source, target, option):
    # Configura los detalles de la conexión a PostgreSQL
    conn_params = {
        'dbname': 'gis',
        'user': 'postgres',
        'password': 'postgres',
        'host': 'localhost',
        'port': '25432'
    }

    # Intenta conectarse a la base de datos
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

        features = []
        # Ejecuta las consultas y obtén los resultados
        cursor.execute(consulta_1)
        resultados_1 = cursor.fetchall()
        #print(resultados_1)
        features.append(guardar_resultados_geojson(resultados_1))
        
        cursor.execute(consulta_2)
        resultados_2 = cursor.fetchall()
        #print(resultados_2)
        features.append(guardar_resultados_geojson(resultados_2))
        
        cursor.execute(consulta_3)
        resultados_3 = cursor.fetchall()
        #print(resultados_3)
        features.append(guardar_resultados_geojson(resultados_3))
        
        cursor.execute(consulta_4)
        resultados_4 = cursor.fetchall()
        #print(resultados_4)
        features.append(guardar_resultados_geojson(resultados_4))

        return features

    except psycopg2.Error as e:
        print(f"Error de PostgreSQL: {e}")
        return None

    finally:
        # Cierra la conexión
        if conn:
            conn.close()

def guardar_resultados_geojson(resultados):
    features = []

    
    return features


if __name__ == "__main__":
    # Verifica que se proporcionen los argumentos correctos
    if len(sys.argv) != 4:
        print("Uso: python consulta_postgres.py source target option")
        sys.exit(1)

    # Obtiene los argumentos de la línea de comandos
    features = []
    source = sys.argv[1]
    target = sys.argv[2]
    option = sys.argv[3]


