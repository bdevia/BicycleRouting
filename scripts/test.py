from shapely.geometry import Point, LineString

# Definir un punto y una LineString de ejemplo
point = Point(-70.688, -33.432)
linestring = LineString([(-70.687, -33.433), (-70.686, -33.430), (-70.686, -33.425)])

# Proyectar el punto sobre la LineString
projected_point = linestring.interpolate(linestring.project(point))

print(projected_point)
