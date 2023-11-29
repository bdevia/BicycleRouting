import json
import geojson
import bisect
import math
from collections import OrderedDict

# FUNCION PARA GENERAR LOS TRAMOS DE CICLOVIAS
def split_list(lst, indices):
    result = []
    start = 0
    end = 0
    for indice in indices:
        if indice != 0 and indice != len(lst) - 1:
            end = indice
            result.append(lst[start:end+1])
            #print(f'start {start} fin {end}')
            start = indice
    result.append(lst[start:])
    #print(f'start {start} end {len(lst)-1}')
    return result
    
def distancia_entre_puntos(punto1, punto2):
    return math.sqrt((punto1[0] - punto2[0]) ** 2 + (punto1[1] - punto2[1]) ** 2)

def agregar_punto_interseccion(coordinates, punto_interseccion):
    new_coordinates = coordinates
    distances = [distancia_entre_puntos(punto_interseccion, punto) for punto in new_coordinates]
    indice_minima_distancia = distances.index(min(distances))
    
    if indice_minima_distancia - 1 >= 0 and indice_minima_distancia + 1 <= len(new_coordinates) -1:
        distance_a_punto = distancia_entre_puntos(new_coordinates[indice_minima_distancia - 1], punto_interseccion)
        distance_b_punto = distancia_entre_puntos(new_coordinates[indice_minima_distancia + 1], punto_interseccion)
        
        if distance_a_punto < distance_b_punto:
            distancia_a_indice =  distancia_entre_puntos(new_coordinates[indice_minima_distancia - 1], new_coordinates[indice_minima_distancia])
            if distance_a_punto < distancia_a_indice:
                new_coordinates.insert(indice_minima_distancia, punto_interseccion)
            else:
                new_coordinates.insert(indice_minima_distancia + 1, punto_interseccion)
        else:
            distancia_b_indice =  distancia_entre_puntos(new_coordinates[indice_minima_distancia + 1], new_coordinates[indice_minima_distancia])
            if distance_b_punto < distancia_b_indice:
                new_coordinates.insert(indice_minima_distancia + 1, punto_interseccion)
            else:
                new_coordinates.insert(indice_minima_distancia, punto_interseccion)
            
    elif indice_minima_distancia == 0:
        distance_a = distancia_entre_puntos(punto_interseccion, new_coordinates[indice_minima_distancia + 1])
        distance_b = distancia_entre_puntos(new_coordinates[indice_minima_distancia], new_coordinates[indice_minima_distancia + 1])
        if distance_a < distance_b:
            new_coordinates.insert(indice_minima_distancia + 1, punto_interseccion)
        else:
            new_coordinates.insert(indice_minima_distancia, punto_interseccion)
        
    elif indice_minima_distancia == len(new_coordinates) -1:
        distance_a = distancia_entre_puntos(punto_interseccion, new_coordinates[indice_minima_distancia - 1])
        distance_b = distancia_entre_puntos(new_coordinates[indice_minima_distancia], new_coordinates[indice_minima_distancia - 1])
        if distance_a < distance_b:
            new_coordinates.insert(indice_minima_distancia, punto_interseccion)
        else:
            new_coordinates.insert(indice_minima_distancia + 1, punto_interseccion)

    return new_coordinates       

def concatenar(coordinates):
    lista_concatenada = coordinates[0]
    if len(coordinates) > 1:
        puntos_inicio = []
        for i, lista in enumerate(coordinates):
            puntos_inicio.append(coordinates[i][0])
        
        #print("puntos_inicio:", puntos_inicio)
        #print(f'coordinates {len(coordinates)}", {coordinates}')
        punto_extremo = min(puntos_inicio, key=lambda punto: punto[0])
        distancias_al_extremo = [distancia_entre_puntos(punto_extremo, punto) for punto in puntos_inicio]

        indices_ordenados = sorted(range(len(coordinates)), key=lambda i: distancias_al_extremo[i])
        #print(indices_ordenados)

        if coordinates[indices_ordenados[0]][0] < coordinates[indices_ordenados[0]][len(coordinates[indices_ordenados[0]])-1]:
            lista_concatenada = coordinates[indices_ordenados[0]]
        else:
            lista_concatenada = coordinates[indices_ordenados[0]][::-1]
        
        for i, lista in enumerate(coordinates):
            if i <= len(coordinates) - 2:
                distancia_inicio = distancia_entre_puntos(lista_concatenada[len(lista_concatenada)-1], coordinates[indices_ordenados[i+1]][0])
                distancia_fin = distancia_entre_puntos(lista_concatenada[len(lista_concatenada)-1], coordinates[indices_ordenados[i+1]][len(coordinates[indices_ordenados[i+1]])-1])
                if distancia_inicio < distancia_fin:
                    lista_concatenada += coordinates[indices_ordenados[i+1]]
                else:
                    lista_concatenada += coordinates[indices_ordenados[i+1]][::-1]
                    
    return lista_concatenada

def haversine_distance(coord1, coord2):
    # Radio de la Tierra en metros
    R = 6371000.0

    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance

# LEEMOS LOS DATOS QUE NECESITAMOS
input_file_path = './data/ciclovias/ciclovias.geojson'
intersecciones_file_path = "./data/ciclovias/puntos_intersecciones.geojson"
output_file_path = "./metadata/ciclovias/ciclovia_tramos.geojson"

# Leer el archivo GeoJSON de entrada
with open(input_file_path, "r") as infile:
    ciclovias = json.load(infile)

with open(intersecciones_file_path, "r") as infile:
    intersecciones = json.load(infile)

# Ciclovia_id deseado
target_ciclovia = [1112, 1137, 1334, 1335]
#target_ciclovia_id_example = 1112
features = []
puntos_id = {}
id_tramos = 1

for index, feature in enumerate(ciclovias['features']):
    ciclovias['features'][index]["geometry"]["coordinates"] = concatenar(feature["geometry"]["coordinates"])

# Buscar la geometría correspondiente al ciclovia_id
for i, feature in enumerate(ciclovias['features']):
    target_ciclovia_id = feature['properties']['ciclovia_id']
    sentido = feature['properties']['sentido']
    geometry = feature['geometry']
    coordinates = geometry['coordinates']

    #print(f'cantidad de dimensiones {len(coordinates)}')

    puntos_interseccion = []
    id_intersecciones = []

    for feature in intersecciones['features']:
        if feature['properties']['ciclovia_a'] == target_ciclovia_id:
            geometry_intersecciones = feature['geometry']
            puntos_interseccion.append(geometry_intersecciones['coordinates'])
            id_intersecciones.append(feature['properties']['ciclovia_b'])
    
    # Convertir listas internas a tuplas y eliminar duplicados manteniendo el orden
    unique_coordinates = list(OrderedDict.fromkeys(map(tuple, coordinates)))
    new_coordinates = [list(coord) for coord in unique_coordinates]
    
    for i, feature_b in enumerate(ciclovias['features']):
        if feature_b['properties']['ciclovia_id'] != target_ciclovia_id and target_ciclovia_id not in id_intersecciones:
            coordinates_b = feature_b['geometry']['coordinates']
            indice_a = 0
            punto_cercano = 0
            distancia_minima = 100000
            for j, coordinates_a in enumerate(new_coordinates):
                distancia_init = haversine_distance(coordinates_a, coordinates_b[0])
                distancia_fin = haversine_distance(coordinates_a, coordinates_b[-1])
                
                if distancia_init < distancia_fin:
                    if distancia_init < distancia_minima:
                        distancia_minima = distancia_init
                        indice_a = j
                        punto_cercano = coordinates_b[0]
                else:
                    if distancia_fin < distancia_minima:
                        distancia_minima = distancia_fin
                        indice_a = j
                        punto_cercano = coordinates_b[-1]
            
            if distancia_minima <= 50:
                ciclovias['features'][i]["geometry"]["coordinates"] = agregar_punto_interseccion(coordinates_b, new_coordinates[indice_a])
                puntos_interseccion.append(new_coordinates[indice_a])
                
    existing_coordinates_set = set(map(tuple, new_coordinates))

    # Agregar solo los puntos de intersección que no están en las coordeid_interseccionesnadas
    for punto_interseccion in puntos_interseccion:
        if tuple(punto_interseccion) not in existing_coordinates_set:
            new_coordinates = agregar_punto_interseccion(new_coordinates, punto_interseccion)

    indices_puntos_interseccion = [new_coordinates.index(p) for p in puntos_interseccion]
    indices_puntos_interseccion.sort()

    # Dividir la lista new_coordinates_sort en tramos
    tramos = split_list(new_coordinates, indices_puntos_interseccion)

    for i, tramo in enumerate(tramos):
        # Crear la geometría para el MultiLineString
        if len(tramo) >= 2:
            # Verificar y asignar identificadores para el punto de inicio
            id_origen = puntos_id.get(tuple(tramo[0]))
            if id_origen is None:
                id_origen = len(puntos_id) + 1
                puntos_id[tuple(tramo[0])] = id_origen

            # Verificar y asignar identificadores para el punto de destino
            id_destino = puntos_id.get(tuple(tramo[-1]))
            if id_destino is None:
                id_destino = len(puntos_id) + 1
                puntos_id[tuple(tramo[-1])] = id_destino
            multilinestring = {
                "type": "Feature",
                "properties": {"tramo_id": id_tramos, "ciclovia_id": target_ciclovia_id, "tramo": i+1, "sentido": sentido, "id_origen": id_origen, "id_destino": id_destino},
                "geometry": {
                    "type": "MultiLineString",
                    "coordinates": [tramo]
                }
            }
            features.append(multilinestring)
            if sentido == "S_I" or sentido == "Bidireccional":
                multilinestring = {
                    "type": "Feature",
                    "properties": {"tramo_id": id_tramos, "ciclovia_id": target_ciclovia_id, "tramo": i+1, "sentido": sentido, "id_origen": id_destino, "id_destino": id_origen},
                    "geometry": {
                        "type": "MultiLineString",
                        "coordinates": [tramo[::-1]]
                    }
                }
                features.append(multilinestring)
            id_tramos = id_tramos + 1

# Crear el GeoJSON final
output_geojson = {
    "type": "FeatureCollection",
    "name": "Tramos_ciclovias",
    "features": features
}

# Escribir el nuevo GeoJSON al archivo de salida
with open(output_file_path, "w") as outfile:
    geojson.dump(output_geojson, outfile, indent=2)

print(f"Archivo GeoJSON generado con éxito en: {output_file_path}")
