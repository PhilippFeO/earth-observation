import json
from pyproj import Transformer

# Load geojson of munich's districts
geojson = ""
with open('Munich_Districts.json', 'r') as f:
    contents = f.readline()
    geojson = json.loads(contents)

# Extract coordinates of first district in "features"
# (nevertheless it's "sb_number" is "02", "sb" may come from "StadtBezirk" (german for "district"))
sb1 = geojson["features"][0]["geometry"]["coordinates"][0]

# Convert coordinates
# (Some type of Gauß-Krüger to Longitude & Latitude)
# (GK type written in geoJSON under crs>properties>name)
transformer = Transformer.from_crs("EPSG:25832", "EPSG:4326")
# GEE needs forstly Longitude, secondly Latitude
sb1_long_lat = [(transformer.transform(*coords)[1],
                 transformer.transform(*coords)[0]) for coords in sb1]

print(*sb1_long_lat)
