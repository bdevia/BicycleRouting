import json
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import geojson
import math

# Lee el archivo JSON
with open('../../data/waze/waze_data.json', 'r') as file:
    data = json.load(file)

## Filtra las alertas según el tipo
filtered_alerts = [alerta for alerta in data['alerts'] if alerta['type'] not in ['POLICE', 'JAM', 'CHIT_CHAT']]

# Función para crear vértices de un hexágono regular alrededor de un punto
def hexagon_vertices(center, size):
    angle = 2 * math.pi / 6
    vertices = [(center[0] + size * math.cos(i * angle), center[1] + size * math.sin(i * angle)) for i in range(6)]
    return vertices

# Crea hexágonos alrededor de cada alerta
features = []
for alerta in filtered_alerts:
    coordinates = (alerta['longitude'], alerta['latitude'])  # Reversa latitud y longitud
    point = Point(coordinates)
    
    # Tamaño del hexágono (ajustable según tus necesidades)
    hexagon_size = 0.00018  # 0.00018 grados aproximadamente equivale a 20 metros
    
    # Calcula los vértices del hexágono
    hexagon_vertices_list = hexagon_vertices(coordinates, hexagon_size)
    
    # Crea un polígono hexagonal
    hexagon_polygon = Polygon(hexagon_vertices_list)
    
    properties = {'type': alerta['type'], 'description': alerta['description']}
    feature = geojson.Feature(geometry=hexagon_polygon, properties=properties)
    features.append(feature)

feature_collection = geojson.FeatureCollection(features)

# Guarda el resultado en un nuevo archivo GeoJSON
with open('../../metadata/waze/datos_waze_hexagonos.geojson', 'w') as output_file:
    geojson.dump(feature_collection, output_file)