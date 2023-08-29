# Some explainatory comments regarding rasterio can be found in extract_bands.py

import numpy as np
import argparse
from read_write_functions import generate_plots, bands_to_array


p = argparse.ArgumentParser("ndvi")
p.add_argument("image_dir",
               help="Directory containing the bands for calculating the NDVI.",
               nargs='?',
               default='./USGS/image_working_dir/ndvi_2022-05-15',
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

"""Generate plots of the index"""
generate_plots(args.image_dir,
               "ndvi",
               ndvi,
               out_meta,
               colors=["orange", "yellow", "green"],
               boundary=False,
               shape_mask_dir="./shapes_and_masks/munich/",
               shape_mask_name="munich-ds")
