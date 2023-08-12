import rasterio
import numpy as np


geotiff = rasterio.open('./geotiffs/all_bands_800.geotiff')

# Set geotiff specific meta data
output_meta = geotiff.meta.copy()
output_meta.update(count=1,  # number of channels
                   dtype=rasterio.uint8,  # interpret values within 0-255
                   nodata=0)  # placeholder if no data is avialable, fi. at the edges
# print(output_meta)

'''Save single RGB channels '''
# image contains values in the range 0-65536
# mapping them onto 0-255

'''Remap image values'''
# for band, name in zip((2, 3, 4), ("blue", "green", "red")):
#     data = geotiff.read(band)
#     d[band-2] = data
#     # Linear mapping
#     # all bands containing geotiff image contains values in 0-65536 (to be precise, [u]int16)
#     # Due to technical reasons (s. link below) the range should be truncated to
#     # achive higher quality images
#     #   https://gis.stackexchange.com/questions/304180/what-are-the-min-and-max-values-of-map-addlayer-on-google-earth-engine
#     # The original template (s. NDVI-Munich.ipynb) removes values <7000 and >16000, ie.
#     # maps the range 7000-16000 onto 0-255 (by specifying a <min> and <max> argument in a
#     # <parameters>-dictionary). This has to be replicated and it's done by solving
#     #   7000m + t = 0,
#     #   16000m + t = 255
#     #       => m = 255/9000, t = -198
#
#     # Leave <nodata>-values untouched
#     data = np.where(data == 0, 0, data * 255/9000 - 198)
#     # Convert values to uint8 according to metadata
#     data = data.astype('uint8')
#
#     with rasterio.open(f'./geotiffs/B{band}-{name}-extracted.geotiff', 'w', **output_meta) as sc:
#         sc.write(data, 1)


output_meta.update(count=3)
data = geotiff.read([4, 3, 2])

''' Linear Mapping
# In a nutshell: Map values from 0-65536 to 0-255 '''
# All bands containing geotiff image contains values in 0-65536 (to be precise, [u]int16)
# Due to technical reasons (s. link below) the range should be truncated to
# achive higher quality images
#   https://gis.stackexchange.com/questions/304180/what-are-the-min-and-max-values-of-map-addlayer-on-google-earth-engine
# The original template (s. NDVI-Munich.ipynb) removes values <7000 and >16000, ie.
# maps the range 7000-16000 onto 0-255 (by specifying a <min> and <max> argument in a
# <parameters>-dictionary). This has to be replicated and it's done by solving
#   7000m + t = 0,
#   16000m + t = 255
#       => m = 255/9000, t = -198

# Leave <nodata>-values untouched
data = np.where(data == 0, 0, data * 255/9000 - 198)

# Save RGB image
with rasterio.open('./geotiffs/rgb.tif', 'w', **output_meta) as m:
    m.write(data)

geotiff.close()


# Some reference:
# https://rasterio.readthedocs.io/en/stable/topics/writing.html
# # Register GDAL format drivers and configuration options with a
# # context manager.
# with rasterio.Env():
#
#     # Write an array as a raster band to a new 8-bit file. For
#     # the new file's profile, we start with the profile of the source
#     profile = geotiff.profile
#
#     # And then change the band count to 1, set the
#     # dtype to uint8, and specify LZW compression.
#     profile.update(
#         dtype=rasterio.uint16,
#         count=1,
#         nodata=0,)
#     # compress='lzw')
#
#     with rasterio.open('example.tif', 'w', **profile) as dst:
#         data = geotiff.read(2) // 255
