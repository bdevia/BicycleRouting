CREATE EXTENSION postgis;
CREATE EXTENSION pgrouting;

-- ogr2ogr -f PostgreSQL PG:"host=localhost user=postgres password=postgres dbname=gis port=25432" ./accidentes.geojson -nln accidentes -lco GEOMETRY_NAME=geom -lco FID=FID