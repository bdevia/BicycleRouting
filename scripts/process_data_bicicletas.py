import json
from shapely.geometry import Point
from shapely.geometry import Polygon
import math

input_geojson_file = "./data/accidentes_bicicleta_2022.geojson"
output_geojson_file = "./metadata/metadata_bicicletas_2022.geojson"

campos_a_eliminar = ["Región", "Calle_Uno", "Calle_Dos", "Número", "Cód_Regi", "Cód_Zona", "Zona", "Ubicación", "Intersecci", "Ruta", "Claseaccid", "Ubicaci_1"]

# Cargar el archivo GeoJSON
with open(input_geojson_file, "r", encoding='utf-8') as archivo_entrada:
    datos_geojson = json.load(archivo_entrada)

# Crear una lista para almacenar las características con hexágonos
features_with_hexagons = []

for caracteristica in datos_geojson["features"]:
    for campo in campos_a_eliminar:
        if campo in caracteristica["properties"]:
            del caracteristica["properties"][campo]

    # Obtener las coordenadas del punto
    coords = caracteristica["geometry"]["coordinates"][0]
    x, y = coords

    # Crear un objeto Point
    punto_referencia = Point(x, y)

    # Definir la distancia deseada (5 metros)
    distancia_en_metros = 10

    # Convertir la distancia a grados de latitud (aproximadamente)
    distancia_en_grados = distancia_en_metros / (40008000 / 360)

    # Calcular los vértices del hexágono
    vertices = []
    for i in range(6):
        angulo = 2 * math.pi / 6 * i
        nuevo_x = x + (distancia_en_grados * math.cos(angulo))
        nuevo_y = y + (distancia_en_grados * math.sin(angulo))
        vertices.append([nuevo_x, nuevo_y])

    # Cerrar el hexágono
    vertices.append(vertices[0])

    # Crear un objeto Polygon que representa el hexágono
    hexagon = Polygon(vertices)

    # Crear una nueva característica con el hexágono
    nueva_caracteristica = {
        "type": "Feature",
        "properties": caracteristica["properties"],
        "geometry": hexagon.__geo_interface__
    }

    features_with_hexagons.append(nueva_caracteristica)

# Crear el nuevo GeoJSON con las características con hexágonos y campos no deseados eliminados
nuevo_geojson = {
    "type": "FeatureCollection",
    "name": "Metadata_bicicletas_2022.geojson",
    "features": features_with_hexagons
}

# Guardar el nuevo archivo GeoJSON
with open(output_geojson_file, "w", encoding='utf-8') as archivo_salida:
    json.dump(nuevo_geojson, archivo_salida, indent=2, ensure_ascii=False)

print(f"Se ha creado un nuevo archivo GeoJSON con los campos no deseados eliminados y hexágonos alrededor de los puntos: {output_geojson_file}")
