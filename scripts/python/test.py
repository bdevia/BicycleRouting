import geopandas as gpd

# Especifica la ruta al archivo shapefile
ruta_shapefile = '../metadata/ciclovias/Ciclovías_2Semestre_2022_snc.shp'

# Lee el shapefile usando geopandas
datos_shapefile = gpd.read_file(ruta_shapefile)

# Muestra la información del GeoDataFrame
print(datos_shapefile.head())
