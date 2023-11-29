from collections import OrderedDict

coordinates = [[1, 2, 3], [3, 4, 5], [1, 2, 3], [5, 6, 7], [3, 4, 5]]

# Convertir listas internas a tuplas y eliminar duplicados manteniendo el orden
unique_coordinates = list(OrderedDict.fromkeys(map(tuple, coordinates)))

# Convertir nuevamente las tuplas a listas
new_coordinates = [list(coord) for coord in unique_coordinates]

print(new_coordinates)
