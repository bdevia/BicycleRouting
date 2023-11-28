#!/bin/bash
source .env
echo "inicializando base de datos..."

#python3 scripts/python/process_data_bicicletas.py
ogr2ogr -f PostgreSQL PG:"host=$HOST user=$POSTGRES_USER password=$POSTGRES_PASSWORD dbname=$POSTGRES_DB port=$PORT" ./data/ciclovias/Ciclovías_2Semestre_2022_snc.shp -lco PRECISION=NO -nlt MULTILINESTRING -nln ciclovias_all -lco GEOMETRY_NAME=geom -lco FID=ciclovia_id -dim 3
ogr2ogr -f PostgreSQL PG:"host=$HOST user=$POSTGRES_USER password=$POSTGRES_PASSWORD dbname=$POSTGRES_DB port=$PORT" ./metadata/accidentes/accidentes.geojson -lco PRECISION=NO -nlt POLYGON -nln accidentes -lco GEOMETRY_NAME=geom -lco FID=accidente_id
ogr2ogr -f PostgreSQL PG:"host=$HOST user=$POSTGRES_USER password=$POSTGRES_PASSWORD dbname=$POSTGRES_DB port=$PORT" ./metadata/robos/robos_rm_40m.geojson -lco PRECISION=NO -nlt MULTIPOLYGON -nln robos -lco GEOMETRY_NAME=geom -lco FID=robo_id -dim 2 
PGPASSWORD=$POSTGRES_PASSWORD psql -h $HOST -U $POSTGRES_USER -d $POSTGRES_DB -p $PORT -f ./scripts/db/clear_data.sql

echo "Iniciando procesamiento de ciclovias..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h $HOST -U $POSTGRES_USER -d $POSTGRES_DB -p $PORT -f ./scripts/db/get_intersecciones.sql
ogr2ogr -f GeoJSON -t_srs EPSG:4326 ./data/ciclovias/ciclovias.geojson PG:"host=$HOST user=$POSTGRES_USER password=$POSTGRES_PASSWORD dbname=$POSTGRES_DB port=$PORT" -sql "SELECT * FROM ciclovias"
ogr2ogr -f GeoJSON -t_srs EPSG:4326 ./data/ciclovias/puntos_intersecciones.geojson PG:"host=$HOST user=$POSTGRES_USER password=$POSTGRES_PASSWORD dbname=$POSTGRES_DB port=$PORT" -sql "SELECT * FROM puntos_intersecciones"
python3 scripts/python/get_tramos.py 
ogr2ogr -f PostgreSQL PG:"host=$HOST user=$POSTGRES_USER password=$POSTGRES_PASSWORD dbname=$POSTGRES_DB port=$PORT" ./metadata/ciclovias/ciclovia_tramos.geojson -lco PRECISION=NO -nlt MULTILINESTRING -nln ciclovia_tramos -lco GEOMETRY_NAME=geom -lco FID=tramo_id -dim 3

echo "Asignacion de pesos..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h $HOST -U $POSTGRES_USER -d $POSTGRES_DB -p $PORT -f ./scripts/db/get_pesos.sql
ogr2ogr -f GeoJSON -t_srs EPSG:4326 ./metadata/ciclovias/ciclovia_tramos_pesos.geojson PG:"host=$HOST user=$POSTGRES_USER password=$POSTGRES_PASSWORD dbname=$POSTGRES_DB port=$PORT" -sql "SELECT * FROM ciclovia_tramos"


#ogr2ogr -f PostgreSQL PG:"host=localhost user=postgres password=postgres dbname=gis port=25432" ./metadata/accidentes/accidentes.geojson -lco PRECISION=NO -nlt POLYGON -nln accidentes -lco GEOMETRY_NAME=geom -lco FID=accidente_id
#ogr2ogr -f PostgreSQL PG:"host=localhost user=postgres password=postgres dbname=gis port=25432" ./metadata/robos/robos_rm_40m.geojson -lco PRECISION=NO -nlt MULTIPOLYGON -nln robos -lco GEOMETRY_NAME=geom -lco FID=robo_id -dim 2 
#
echo "Finalizado exitosamente"

#PGPASSWORD=postgres psql -h localhost -U postgres -d gis -p 25432 -f ./scripts/db/clear_data.sql
#ogr2ogr -f GeoJSON -t_srs EPSG:4326 ./data/ciclovias/ciclovias.geojson PG:"host=localhost user=postgres password=postgres dbname=gis port=25432" -sql "SELECT * FROM ciclovias"
#ogr2ogr -f GeoJSON -t_srs EPSG:4326 ./data/ciclovias/puntos_intersecciones.geojson PG:"host=localhost user=postgres password=postgres dbname=gis port=25432" -sql "SELECT * FROM puntos_intersecciones"
#ogr2ogr -f PostgreSQL PG:"host=localhost user=postgres password=postgres dbname=gis port=25432" ./metadata/ciclovias/ciclovia_tramos.geojson -lco PRECISION=NO -nlt MULTILINESTRING -nln ciclovia_tramos -lco GEOMETRY_NAME=geom -lco FID=tramo_id -dim 3
