"""Evaluate the NDVI of Munich quantitatively by calculating it's average NDVI and the percentage where NDVI > .75 (arbitrarily chosen)."""


import rasterio
import numpy as np

with rasterio.open('./USGS/image_working_dir/NDVI/out/sc-ndvi.geotiff', 'r') as gt:
    ndvi = gt.read(1)

mask = np.load('./shapes_and_masks/munich/munich_mask.npy')

# Calculate area of Munich based on it's mask
area_munich = np.sum(mask)

# Calculate average NDVI
# GeoTIFFs are saved as uint8 => transform into [0, 1] by dividing by 255
avg = np.sum(ndvi) / (area_munich * 255)
print(f"The average NDVI of Munich is {avg:.2f} ...")

# Calculate percentage of NDVI > .75
# Filter/count all entries with an NDVI >= .75
# ndvi.dtype = np.uint8, hence int(_ * 255)
tmp = ndvi[ndvi >= int(.75 * 255)]
percentage_green = tmp.shape[0] / area_munich
print(f"{percentage_green:.2f}% of Munich have an NDVI >= .75 ...")

print("\t...when image was taken.")
