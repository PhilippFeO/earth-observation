# Some explainatory comments regarding rasterio can be found in extract_bands.py

import numpy as np
import matplotlib.image
import argparse
import os
from read_write_functions import bands_to_array, create_out_dir, save_cmap_legend, save_sc_geotiff
from evaluate_index import evaluate_index
from apply_colormap import apply_colormap


p = argparse.ArgumentParser("ndvi")
p.add_argument("image_dir",
               help="Directory containing the bands for calculating the NDVI.",
               nargs='?',
               default='./USGS/image_working_dir/NDVI/',
               type=str)
args = p.parse_args()

"""Read bands"""
# B4 = red
# B5 = NIR
band_order = ('B4', 'B5')
bands, out_meta = bands_to_array(args.image_dir, band_order)

"""Calculate NDVI = (NIR - Red) / (NIR + Red)"""
# Avoid dividing by 0 by adding smallest possible float to the divisor
b4red, b5nearIR = bands[0], bands[1]
ndvi = np.divide(b5nearIR - b4red,
                 b5nearIR + b4red + np.finfo(float).eps)  # has type 'float32'

"""Postprocess index values"""
# truncate values
# especially to remove negative values
# print(f"{ndvi.min() = }\n{ndvi.max() = }")
min, max = 0., 1.
ndvi = np.clip(ndvi, min, max)

"""Apply colormap and insert mask."""
colors = ["red", "yellow", "green"]
# cmap_ndvi is a RGBA array
cmap_ndvi, color_map = apply_colormap(ndvi, colors)

# Replace alpha channel by mask
mask = np.load('./shapes_and_masks/munich/munich_mask.npy')
cmap_ndvi[:, :, 3] = mask

"""Save images."""
# Create output directory for produced images
out_dir = create_out_dir(args.image_dir)

# Saving np-array as PNG for valid transparency (not embedded in a plot)
path_to_image = os.path.join(out_dir, 'cmap_ndvi.png')
matplotlib.image.imsave(path_to_image, cmap_ndvi)

# Matplotlib plot with color gradient legend
path_to_image = os.path.join(out_dir, 'legend_cmap_ndvi.png')
save_cmap_legend(cmap_ndvi, color_map, path_to_image)

# One channel NDVI image as geotiff
path_to_image = os.path.join(out_dir, 'sc_ndvi.geotiff')
save_sc_geotiff(ndvi, out_meta.copy(), path_to_image)

""" Evaluate NDVI """
evaluate_index('NDVI', ndvi, .75, mask)
