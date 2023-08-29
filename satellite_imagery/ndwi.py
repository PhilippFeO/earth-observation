import argparse
import numpy as np
from read_write_functions import bands_to_array, generate_plots


p = argparse.ArgumentParser("ndwi")
p.add_argument("image_dir",
               help="Directory containing the bands for calculating the NDWI.",
               nargs='?',
               default='./USGS/image_working_dir/ndwi_2022-05-15',
               type=str)
args = p.parse_args()

""" Read bands """
# B3 = green
# B5 = near-IR
band_order = ('B3', 'B5')
bands, out_meta = bands_to_array(args.image_dir, band_order)

""" Calculate ndwi = (Green - NIR) / (Green + NIR) """
# Avoid dividing by 0 by adding smallest possible float to the divisor
b4green, b5nearIR = bands[0], bands[1]
ndwi = np.divide(b4green - b5nearIR,
                 b4green + b5nearIR + np.finfo(float).eps)  # has type 'float32'

""" Postprocess index values """
# Clip values
# especially to remove negative values
# print(f"{ndwi.min() = }\n{ndwi.max() = }")
min, max = 0., ndwi.max()
ndwi = np.clip(ndwi, min, max)


# Scale for better visual results
ndwi = ndwi / max * 10
print("\nImage values (not calculated ones) were manipulated such that visual results are more appealing.\n")

"""Generate plots of the index"""
generate_plots(args.image_dir,
               "ndwi",
               ndwi,
               out_meta,
               colors=["yellow", "blue"],
               boundary=False,
               shape_mask_dir="./shapes_and_masks/munich/",
               shape_mask_name="munich-ds")
