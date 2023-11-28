import json
import requests
import pyproj
from pyproj import Proj, transform

# Cargar el GeoJSON desde un archivo
with open("./data/zona_extraccion.geojson", "r") as infile:
    geojson_data = json.load(infile)

# Extraer las coordenadas del GeoJSON
coordinates = geojson_data["features"][0]["geometry"]["coordinates"][0]

# Definir los sistemas de referencia
in_proj = Proj(init='epsg:4326')
out_proj = Proj(init='epsg:3857')

# Convertir las coordenadas de EPSG:4326 a EPSG:3857 y obtener los valores extremos
x_coordinates, y_coordinates = zip(*[transform(in_proj, out_proj, lon, lat) for lon, lat in coordinates])
bbox_xmin, bbox_ymin, bbox_xmax, bbox_ymax = min(x_coordinates), min(y_coordinates), max(x_coordinates), max(y_coordinates)

# Tamaño de la imagen
width = 5000
height = 4100

# Número de solicitudes a generar: (x_num_requests) * (y_num_requests)
x_num_requests = 200
y_num_requests = 200    # con esta configuracion se generan 200*200 = 40.000 muestras

# Calcular incrementos en X e Y
x_increment = width / x_num_requests
y_increment = height / y_num_requests

# Coordenadas iniciales
x = 0
y = 0

# URL base de la solicitud WMS (con el bbox constante)
base_url = "https://stop.carabineros.cl/geoserver/stop/wms/?service=WMS&request=GetFeatureInfo&version=1.1.1&layers=stop%3ARobos&styles=&format=image%2Fpng&transparent=true&info_format=application%2Fjson&srs=EPSG%3A3857&query_layers=stop%3ARobos"

# Crear una función de transformación
crs = pyproj.CRS("EPSG:3857")
transformer = pyproj.Transformer.from_crs(crs, "EPSG:4326", always_xy=True)

# Crear un diccionario para almacenar los resultados reformateados
reformatted_data = {
    "type": "FeatureCollection",
    "features": []
}

# Crear un conjunto para rastrear FID únicos
processed_fids = set()

# Generar las solicitudes con coordenadas X e Y incrementales
for i in range(x_num_requests):
    for j in range(y_num_requests):
        # Construir la URL de la solicitud WMS con coordenadas X e Y variables
        url = f"{base_url}&width={width}&height={height}&bbox={bbox_xmin}%2C{bbox_ymin}%2C{bbox_xmax}%2C{bbox_ymax}&X={x}&Y={y}"
        print(url)
        
        try:
            # Realizar la solicitud HTTP con un tiempo de espera máximo (timeout)
            response = requests.get(url, verify=False, timeout=10)  # Establece el tiempo de espera en segundos

            # Verificar si la respuesta es válida y si contiene datos
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(i)
                    if 'features' in data and data['features']:
                        # Reformatear los datos y transformar las coordenadas a EPSG:4326
                        for feature in data["features"]:
                            # Verificar si el FID ya ha sido procesado
                            fid = feature["properties"]["FID"]
                            if fid not in processed_fids:
                                geometry = feature["geometry"]
                                geom_type = geometry["type"]
                                coordinates = geometry["coordinates"]
                                
                                if geom_type == "MultiPolygon":
                                    # Transformar las coordenadas de cada anillo del MultiPolygon
                                    for polygon in coordinates:
                                        for ring in polygon:
                                            for i, coords in enumerate(ring):
                                                lon, lat = transformer.transform(coords[0], coords[1])
                                                ring[i] = [lon, lat]
                                
                                # Reformatear el feature
                                reformatted_feature = {
                                    "type": "Feature",
                                    "geometry": geometry,
                                    "properties": feature["properties"]
                                }
                                
                                reformatted_data["features"].append(reformatted_feature)
                                
                                # Agregar el FID al conjunto de procesados
                                processed_fids.add(fid)
                except json.JSONDecodeError as e:
                    print(f"Error al analizar JSON: {e}")
            else:
                print(f"Error en la solicitud: Código de estado {response.status_code}")
        except requests.exceptions.Timeout:
            print("La solicitud ha excedido el tiempo de espera.")
        
        y += int(y_increment)
        
    # Incrementar las coordenadas en X e Y
    x += int(x_increment)
    y = 0

# Guardar el resultado reformateado en un archivo GeoJSON con formato estructurado
with open("./metadata/robos_rm_40m.geojson", "w") as outfile:
    json.dump(reformatted_data, outfile, indent=4)
