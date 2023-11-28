import json
from pyproj import Proj, transform

# Cargar el GeoJSON desde un archivo
with open("zona_extraccion.geojson", "r") as infile:
    geojson_data = json.load(infile)

# Extraer las coordenadas del GeoJSON
coordinates = geojson_data["features"][0]["geometry"]["coordinates"][0]

# Definir los sistemas de referencia
in_proj = Proj(init='epsg:4326')
out_proj = Proj(init='epsg:3857')

# Convertir las coordenadas de EPSG:4326 a EPSG:3857 y obtener los valores extremos
x_coordinates, y_coordinates = zip(*[transform(in_proj, out_proj, lon, lat) for lon, lat in coordinates])
xmin, ymin, xmax, ymax = min(x_coordinates), min(y_coordinates), max(x_coordinates), max(y_coordinates)

# Imprimir los valores de EPSG:3857
print("xmin:", xmin)
print("ymin:", ymin)
print("xmax:", xmax)
print("ymax:", ymax)
