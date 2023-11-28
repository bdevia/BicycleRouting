import requests
import geopandas as gpd
import pyproj
from shapely.geometry import shape
import json

# URL del servicio WMS
wms_url = "https://stop.carabineros.cl/geoserver/stop/wms/?service=WMS&request=GetFeatureInfo&version=1.1.1&layers=stop%3ARobos&styles=&format=image%2Fpng&transparent=true&info_format=application%2Fjson&width=1920&height=976&srs=EPSG%3A3857&bbox=-7868212.712533993%2C-3956586.0085542393%2C-7859040.269139772%2C-3951923.349828845&query_layers=stop%3ARobos&X=738&Y=588"

# Realizar la solicitud HTTP al servicio WMS
response = requests.get(wms_url, verify=False)

# Comprobar si la solicitud fue exitosa
if response.status_code == 200:
    # Cargar los datos como un diccionario
    data_dict = response.json()

    # Definir el CRS de los datos de entrada
    crs = pyproj.CRS("EPSG:3857")

    # Crear una función de transformación
    transformer = pyproj.Transformer.from_crs(crs, "EPSG:4326", always_xy=True)

    # Crear un nuevo diccionario para almacenar los datos reformateados
    reformatted_data = {
        "type": "FeatureCollection",
        "features": []
    }

    # Recorrer las geometrías y reformatear los datos
    for feature in data_dict["features"]:
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

    # Guardar los datos reformateados en un archivo .geojson
    output_geojson_file = "datos_geograficos11.geojson"
    with open(output_geojson_file, "w") as geojson_file:
        json.dump(reformatted_data, geojson_file, indent=2)

    print("Los datos reformateados se han guardado en:", output_geojson_file)
else:
    print("La solicitud al servicio WMS falló. Código de estado:", response.status_code)
