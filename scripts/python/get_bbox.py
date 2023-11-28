from shapely.geometry import Polygon
import json

# Valores del bbox
xmin = -7881108.82343097
ymin = -3976794.6868781974
xmax = -7850946.391254325
ymax = -3943698.1659684954

# Convertir a coordenadas geográficas (EPSG:3857 a EPSG:4326)
from pyproj import Proj, transform

in_proj = Proj(init='epsg:3857')
out_proj = Proj(init='epsg:4326')

xmin, ymin = transform(in_proj, out_proj, xmin, ymin)
xmax, ymax = transform(in_proj, out_proj, xmax, ymax)

# Crear un objeto Polygon
bbox_polygon = Polygon([(xmin, ymin), (xmin, ymax), (xmax, ymax), (xmax, ymin), (xmin, ymin)])

# Generar un GeoJSON
geojson = {
    "type": "Feature",
    "properties": {},
    "geometry": bbox_polygon.__geo_interface__
}

# Guardar el GeoJSON en un archivo
with open("bbox_rm.geojson", "w") as outfile:
    json.dump(geojson, outfile)

print("Archivo 'bbox_rm.geojson' generado.")
