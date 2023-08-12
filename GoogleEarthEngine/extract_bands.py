import rasterio
import numpy as np
import argparse


def adjust_values(data):
    ''' Linear Mapping
    In a nutshell: Map values from 0-65536 to 0-255 '''
    # All bands containing geotiff image contains values in 0-65536 (to be precise, [u]int16).
    # But the range is just partially exploited, ie. only values from f.e. 5000-20000.
    # To avoid dark images, the effective range is mapped onto 0-255.
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
    return np.where(data == 0, 0, data * 255/9000 - 198)


def extract_band(geotiff, band, name):
    data = geotiff.read(band)
    # Leave <nodata>-values untouched
    data = adjust_values(data)
    # Convert values to uint8 according to metadata
    data = data.astype('uint8')

    output_meta = geotiff.meta.copy()
    output_meta.update(count=1,  # number of channels
                       dtype=rasterio.uint8,  # interpret values within 0-255
                       nodata=0)  # placeholder if no data is avialable, fi. at the edges

    with rasterio.open(f'./geotiffs/B{band}-{name}.geotiff', 'w', **output_meta) as sc:
        sc.write(data, 1)


def compose_bands_to_rgb(geotiff):
    output_meta = geotiff.meta.copy()
    output_meta.update(count=3,
                       dtype=rasterio.uint8,  # interpret values within 0-255
                       nodata=0)  # placeholder if no data is avialable, fi. at the edges
    data = geotiff.read([4, 3, 2])

    data = adjust_values(data)

    # Save RGB image
    with rasterio.open('./geotiffs/rgb.tif', 'w', **output_meta) as m:
        m.write(data)


if __name__ == "__main__":
    geotiff = rasterio.open('./geotiffs/all_bands_800.geotiff')

    # compose_bands_to_rgb()

    parser = argparse.ArgumentParser("extract_bands")
    parser.add_argument(
        "band", help="The band to extract from a geotiff image", type=int)
    parser.add_argument(
        "band_name", help="Name of band, f.i. <red> or <near-IR>", type=str)
    args = parser.parse_args()

    extract_band(geotiff, args.band, args.band_name)

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
