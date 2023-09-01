"""
Corps a geometry saved as a shapefile from a GeoTIFF.

Usage:
    python isolate_shape.py <GeoTIFF> <Shapefile>

"""

import os
from rasterio.mask import mask
import rasterio
import fiona
import argparse
import numpy as np

p = argparse.ArgumentParser("isolate_shape")
p.add_argument("geotiff",
               help="The GeoTIFF to crop a geometry from.",
               type=str)
p.add_argument("shapefile",
               help="Shapefile containing the geometry to crop from a GeoTIFF.",
               type=str)
p.add_argument("mask_path",
               help="Path to save the mask resembling the geometry",
               type=str)
p.add_argument("file_prefix",
               help="Prefix for the cropped image_name image_name name, f.i. 'buffered'.",
               nargs='?',
               default='Masked',
               type=str)
args = p.parse_args()

# Load geometry (of Munich)
with fiona.open(args.shapefile) as shapefile:
    geometry = [feature["geometry"] for feature in shapefile]

# load the raster, mask it by the polygon and crop it
src_img_dir, image_name = os.path.split(args.geotiff)  # split path to GeoTIFF
out_dir = os.path.join(src_img_dir, 'geometries')
try:
    os.mkdir(out_dir)
    print(f'Created:\n\t{out_dir}')
except FileExistsError:  # Error occurs when <out_dir> exists; this is nothing to worry about
    pass

# Retrieve mask of <geometry>, ie. a boolean array resembling the geometry
#   Without "filled=False", outside the shape filled with <nodata>/0 (and
#   displayed as black).
#   This is not desirable because this value might occure within the shape
#   and decreases accuracy.
with rasterio.open(args.geotiff, 'r') as src:
    # out_image, out_transform = mask(src, geometry, crop=True)
    out_image, out_transform = mask(src, geometry, crop=True, filled=False)


# save the resulting raster
out_meta = src.meta.copy()
out_meta.update({"driver": "GTiff",
                 "height": out_image.shape[1],
                 "width": out_image.shape[2],
                 "transform": out_transform})
# print(out_meta)

# <image_name> ends in .TIF, no extension needed
out_image_name = os.path.join(out_dir, f"{args.file_prefix}_{image_name}")
with rasterio.open(out_image_name, "w", **out_meta) as dest:
    dest.write(out_image)

# Save the mask (for further calculations as in './ndvi.py')
out_mask = out_image.mask[0]
# <~out_mask> inverts masks (I need it vice versa than provided by rasterio)
np.save(args.mask_path, ~out_mask)
# show(source=out_image.data, alpha=a)
