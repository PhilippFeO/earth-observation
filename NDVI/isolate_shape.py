"""
Corps a geometry saved as a shapefile from a GeoTIFF.

Usage:
    python isolate_shape.py <GeoTIFF> <Shapefile>

"""

from os.path import split
from rasterio.mask import mask
import rasterio
import fiona
import argparse

p = argparse.ArgumentParser("isolate_shape")
p.add_argument("GeoTIFF",
               help="The GeoTIFF to crop a geometry from.",
               type=str)
p.add_argument("shapefile",
               help="Shapefile containing the geometry to crop from a GeoTIFF.",
               type=str)
args = p.parse_args()

# Load geometry (of Munich)
with fiona.open(args.shapefile) as shapefile:
    geometry = [feature["geometry"] for feature in shapefile]

# load the raster, mask it by the polygon and crop it
geotiff = args.GeoTIFF
folder, file = split(geotiff)  # split path to GeoTIFF

with rasterio.open(f'{folder}/{file}', 'r') as src:
    out_image, out_transform = mask(src, geometry, crop=True)

out_meta = src.meta.copy()

# save the resulting raster
out_meta.update({"driver": "GTiff",
                 "height": out_image.shape[1],
                 "width": out_image.shape[2],
                 "transform": out_transform})

# <file> ends in .TIF, no extension needed
with rasterio.open(f"{folder}/Masked_{file}", "w", **out_meta) as dest:
    dest.write(out_image)
