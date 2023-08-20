import argparse
import numpy as np
import os
import matplotlib.image
from read_write_functions import bands_to_array, create_out_dir, save_cmap_legend, save_sc_geotiff
from evaluate_index import evaluate_index
from apply_colormap import apply_colormap


p = argparse.ArgumentParser("ndwi")
p.add_argument("image_dir",
               help="Directory containing the bands for calculating the NDWI.",
               nargs='?',
               default='./USGS/image_working_dir/ndwi_2022-03-28/',
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
ndwi = ndwi / max
print("\nImage values (not calculated ones) were manipulated such that visual results are more appealing.\n")

"""Apply colormap and insert mask."""
colors = ["yellow", "blue"]
# cmap_ndwi is a RGBA array
cmap_ndwi, color_map = apply_colormap(ndwi, colors)

# Replace alpha channel by mask
mask = np.load('./shapes_and_masks/munich/munich_mask.npy')
cmap_ndwi[:, :, 3] = mask

""" Save images """
# Create output directory for produced images
out_dir = create_out_dir(args.image_dir)

# Saving np-array as PNG for valid transparency (not embedded in a plot)
path_to_image = os.path.join(out_dir, 'cmap_ndwi.png')
matplotlib.image.imsave(path_to_image, cmap_ndwi)

# matplotlib plot with color gradient legend
path_to_image = os.path.join(out_dir, 'legend_cmap_ndwi.png')
save_cmap_legend(cmap_ndwi, color_map, path_to_image)

# One channel ndwi image as geotiff
path_to_image = os.path.join(out_dir, 'sc_ndwi.geotiff')
save_sc_geotiff(ndwi, out_meta.copy(), path_to_image)

""" Evaluate NDWI """
evaluate_index('NDWI', ndwi * max, .33, mask)
