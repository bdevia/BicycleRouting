import json
import geojson
import bisect
import math

# FUNCION PARA GENERAR LOS TRAMOS DE CICLOVIAS
def split_list(lst, indices):
    result = []
    start = 0
    end = 0
    for indice in indices:
        if indice != 0 and indice != len(lst) - 1:
            end = indice
            result.append(lst[start:end+1])
            print(f'start {start} fin {end}')
            start = indice
    result.append(lst[start:])
    print(f'start {start} end {len(lst) -1}')
    return result

# FUNCION PARA DETERMINAR EL SENTIDO DE LA CADA CICLOVIA
def sentido_multilinestring(coordenadas):
    pendiente_promedio_x = sum(
    (coord2[0] - coord1[0]) / (coord2[1] - coord1[1]) if (coord2[1] - coord1[1]) != 0 else 0
    for coord1, coord2, _ in zip(coordenadas, coordenadas[1:], coordenadas[2:])
    ) / len(coordenadas)

    pendiente_promedio_y = sum(
        (coord2[1] - coord1[1]) / (coord2[0] - coord1[0]) if (coord2[0] - coord1[0]) != 0 else 0
        for coord1, coord2, _ in zip(coordenadas, coordenadas[1:], coordenadas[2:])
    ) / len(coordenadas)
    
    if abs(pendiente_promedio_x) > abs(pendiente_promedio_y):
        return "Horizontal"
    elif abs(pendiente_promedio_y) > abs(pendiente_promedio_x):
        return "Vertical"
    else:
        return "Indeterminado"
    
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
            
        punto_extremo = min(puntos_inicio, key=lambda punto: punto[0])
        distancias_al_extremo = [distancia_entre_puntos(punto_extremo, punto) for punto in puntos_inicio]

        indices_ordenados = sorted(range(len(coordinates)), key=lambda i: distancias_al_extremo[i])
        print(indices_ordenados)

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
                
# LEEMOS LOS DATOS QUE NECESITAMOS
input_file_path = "../data/ciclovias/ciclovias.geojson"
intersecciones_file_path = "../data/ciclovias/puntos_intersecciones.geojson"
output_file_path = "../data/ciclovias/correccion.geojson"

# Leer el archivo GeoJSON de entrada
with open(input_file_path, "r") as infile:
    ciclovias = json.load(infile)

with open(intersecciones_file_path, "r") as infile:
    intersecciones = json.load(infile)

# Ciclovia_id deseado
#target_ciclovia_id = [1112, 1137, 1334, 1335]
target_ciclovia_id = 1204
features = []

#for target_ciclovia_id in target_ciclovia:

# Buscar la geometría correspondiente al ciclovia_id
for feature in ciclovias['features']:
    if feature['properties']['ciclovia_id'] == target_ciclovia_id:
        sentido = feature['properties']['sentido']
        geometry = feature['geometry']
        coordinates = geometry['coordinates']
        break

#new_coordinates = [sublista for lista in coordinates for sublista in lista]
print(f'cantidad de dimensiones {len(coordinates)}')
#print(f'new_coordenadoas {len(new_coordinates)} \n {new_coordinates}')

puntos_interseccion = []
id_intersecciones = []

for feature in intersecciones['features']:
    if feature['properties']['ciclovia_a'] == target_ciclovia_id:
        geometry_intersecciones = feature['geometry']
        puntos_interseccion.append(geometry_intersecciones['coordinates'])
        id_intersecciones.append(feature['properties']['ciclovia_b']) 

print(f'coordinates[0] \n {len(coordinates[0])}') 
new_coordinates = concatenar(coordinates)
print(f'new_coordenadoas {len(new_coordinates)}')

existing_coordinates_set = set(map(tuple, new_coordinates))

# Agregar solo los puntos de intersección que no están en las coordenadas
for punto_interseccion in puntos_interseccion:
    if tuple(punto_interseccion) not in existing_coordinates_set:
       new_coordinates = agregar_punto_interseccion(new_coordinates, punto_interseccion)

print(f'new_coordinates {len(new_coordinates)}')
indices_puntos_interseccion = [new_coordinates.index(p) for p in puntos_interseccion]
indices_puntos_interseccion.sort()
print(f'indices {indices_puntos_interseccion}')

# Dividir la lista new_coordinates_sort en tramos
tramos = split_list(new_coordinates, indices_puntos_interseccion)

for i, tramo in enumerate(tramos):
    # Crear la geometría para el MultiLineString
    print(f'tramo {i} tamaño{len(tramo)}')
    multilinestring = {
        "type": "Feature",
        "properties": {"ciclovia_id": target_ciclovia_id, "sentido": sentido,"tramo": i+1},
        "geometry": {
            "type": "MultiLineString",
            "coordinates": [tramo]
        }
    }
    features.append(multilinestring)

# Crear el GeoJSON final
output_geojson = {
    "type": "FeatureCollection",
    "name": "Tramos_ciclovias",
    "features": features
}

#print(f'puntos interseccion {len(puntos_interseccion)} \n {puntos_interseccion}')
#print(f'indices {len(indices_puntos_interseccion)} \n {indices_puntos_interseccion}') 
#print(f'tamaño coordenadas {len(coordinates[0])} \n{coordinates[0]}')
print(f'tamaño coordenadas {len(new_coordinates)} \n{new_coordinates}')
print(f'tramos {len(tramos)}\n{tramos}')


# Escribir el nuevo GeoJSON al archivo de salida
with open(output_file_path, "w") as outfile:
    geojson.dump(output_geojson, outfile, indent=2)

print(f"Archivo GeoJSON generado con éxito en: {output_file_path}")
