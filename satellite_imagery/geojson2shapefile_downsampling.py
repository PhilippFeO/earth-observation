#!/usr/bin/env python

"""
From GeoJSON to Shapefile with addtional downsampling

The notebook will cover the process of calculating a `Shapefile` based on a `GeoJSON` containing all districts of Munich (and not the city as a whole entity). In particular, the inner borders or shared borders between districts are removed.

Since I also need a version of Munich's border with <500 vertives for USGS Earth Explorer (it only accepts Polygons with <500 vertices), I will also calculate a downsampled version of geopolygon resembling Munich.

There is also a Jupyter notebook (./Munich/geojson2shapefile_downsampling.py) with included plots of the steps and shapes. In fact, this script is derived from this notebook and then a bit tweaked.
"""

from shapely.geometry import Polygon
from shapely.ops import unary_union
import geopandas as gpd

# 1. Load the GeoJSON of Munich's districts
# The file is available under https://geoportal.muenchen.de/geoserver/opendata/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=opendata:vablock_stadtbezirk_opendata&outputFormat=application/json
munich_dir = './shapes_and_masks/munich/'
gdf = gpd.read_file(f'{munich_dir}/munich-districts.geojson')


# Munich has two two small enclaves belonging to _Untergiesing-Harlaching_ and _Thalkirchen-Obersendling-Forstenried-Fürstenried-Solln_. Because the Polygon has to be downsampled to <500 Vertices for the USGS Earth Explorer and the algorithm doesn't work with MultiPolygons only with one single Polygon, these will be removed.
# Due to their diminishing small area their contribution can be neglected anyway.
gdf["area"] = gdf.area
city = gdf[["name", "area", "geometry"]]

# Sort the DataFrame based on the 'area' column in ascending order
city_without_exclaves = city.sort_values(by='area')

# Drop the rows with the smallest areas (the first two)
city_without_exclaves = city_without_exclaves.iloc[2:]


# 2. Unify districts to calculate the city boundary
# Merge all district polygons into one single polygon.
# unary_union() unifys all submitted Polygons, ie. removes duplicates/inner borders
polygons = [poly for poly in city_without_exclaves['geometry']]
munich_poly = unary_union(polygons)


# 3. Downsample the Polygon
# USGS Earth Explorer only allows Polygons with < 500 vertices. Since the original one has roughly 4000, we have to downsample it. Luckily, there is `shapely` function: `shapely.simplify()`, the documentation can be found [here](https://shapely.readthedocs.io/en/stable/reference/shapely.simplify.html).
def downsample_polygon(polygon, target_points):
    assert type(polygon) == Polygon
    # with the exclaves, we had a MultiPolygon which doesn't support the exterior property
    exterior_ring = polygon.exterior
    simplified_exterior = exterior_ring.simplify(
        tolerance=exterior_ring.length / target_points)
    downsampled_polygon = Polygon(simplified_exterior)
    return downsampled_polygon


# Downsample to < 500 vertices
target_points = 7000  # Found by trial and error
munich_downsampled = downsample_polygon(munich_poly, target_points)
print("Original number of points:", len(munich_poly.exterior.coords))
print("Downsampled number of points:", len(munich_downsampled.exterior.coords))


# 4. Create files (GeoJSON, Shapefile)
# 4.1 Downsampled Munich (without exclaves)
d = {'name': ['München'], 'geometry': munich_downsampled}
mgdf = gpd.GeoDataFrame(d, crs='EPSG:25832')
mgdf.to_file(f'{munich_dir}/munich-ds.geojson', driver='GeoJSON')
mgdf.to_file(f'{munich_dir}/munich-ds.shp')

# 4.2 High resolution polygon (with exclaves)
# from shapely.geometry import MultiPolygon
# munich_complete_multipoly = MultiPolygon([munich_poly,
#                              city['geometry'][2],
#                              city['geometry'][16]])
# d = {'name': ['München'], 'geometry': munich_complete_multipoly}
# mmgdf = gpd.GeoDataFrame(d, crs='EPSG:25832')
# mmgdf['flache_qm'] = mmgdf.area
# mmgdf.to_file('Munich.geojson', driver='GeoJSON')

# 4.3 Buffered version of Munich
d = {'name': ['München'], 'geometry': mgdf.buffer(5000)}
m_buffered = gpd.GeoDataFrame(d, crs='EPSG:25832')
m_buffered.to_file(f'{munich_dir}/munich-buffered.shp')
