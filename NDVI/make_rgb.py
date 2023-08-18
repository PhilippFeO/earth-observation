"""
Reads image of band {red, green, blue} in <args.band_dir> (i.e., all images have to be transfered there beforehand) and combines them to an RGB image. This saved under '<args.band_dir>/out/combined_bands.tif'.
"""

import rasterio
import argparse
from adjust_values import adjust_values
from read_write_functions import bands_to_array, create_out_dir

# TODO: adjust band values individually to control the influence of a band <17-08-2023>

p = argparse.ArgumentParser("compose_bands")
p.add_argument("band_dir",
               help="Directory containing the images for composing.",
               type=str)
args = p.parse_args()

band_order = ('B4', 'B3', 'B2')
bands, out_meta = bands_to_array(args.band_dir, band_order)

bands = adjust_values(bands, 7000, 16000)

# Create output directory to save the produced image in
out_dir = create_out_dir(args.image_dir)

# save combined bands
with rasterio.open(f'{out_dir}/combined_bands.tif', 'w', **out_meta) as m:
    m.write(bands)
