import rasterio
import numpy as np
import argparse


def adjust_values(data, min, max):
    ''' Linear Mapping
    In a nutshell: Map values from [min, max] (subset of [0, 65536]) to [0, 255]

    All bands containing geotiff image contains values in [0, 65536]
        (to be precise, [u]int16).
    But the range is just partially exploited (technical reasons, s. link below),
    f.i. only values from 5000-20000.
    To avoid dark images, this effective range is mapped onto 0-255.
        > https://gis.stackexchange.com/questions/304180/what-are-the-min-and-max-values-of-map-addlayer-on-google-earth-engine

    The original template (s. NDVI-Munich.ipynb) removes values <7000 and >16000, ie.
    maps the range [7000, 16000] onto [0, 255] (by specifying a <min> and <max> argument in a
    <parameters>-dictionary). This has to be replicated and it's done by solving
      7000m + t = 0,
      16000m + t = 255
          => m = 255/(16000-7000), t = 7000*m
    '''

    # Leave <nodata>-values untouched
    # Map range min-max onto 0-255.
    #   =>  make <min> the smallest value in the image
    #       make <max> the highest value in the image
    #   By doing so <tmp * m - t> won't produce values outside 0-255.
    #       (Before, I didn't truncate and had artifacts in the rgb-image)
    tmp = np.clip(data, min, max)
    m = 255 / (max - min)
    t = min * 255 / (max - min)
    tmp = tmp * m - t  # The actual mapping
    return tmp.astype('uint8')  # Convert values to uint8 according to metadata


def extract_band(geotiff, band, name):
    """ Save one single band as an image """
    output_meta = geotiff.meta.copy()
    output_meta.update(count=1,  # number of channels
                       dtype=rasterio.uint8,  # interpret values within 0-255
                       nodata=0)  # placeholder if no data is avialable, fi. at the edges

    data = geotiff.read(band)  # data is a pure np.ndarray
    data = adjust_values(data, 7000, 16000)

    with rasterio.open(f'./geotiffs/B{band}-{name}.geotiff', 'w', **output_meta) as sc:
        sc.write(data, 1)


def compose_bands_to_rgb(geotiff):
    """ Merge bands 4 (red), 3 (green), 2 (blue) into one rgb image """
    output_meta = geotiff.meta.copy()
    output_meta.update(count=3,
                       dtype=rasterio.uint8,  # interpret values within 0-255
                       nodata=0)  # placeholder if no data is avialable, fi. at the edges

    data = geotiff.read([4, 3, 2])
    data = adjust_values(data, 7000, 16000)

    # Save RGB image
    with rasterio.open('./geotiffs/rgb.tiff', 'w', **output_meta) as m:
        m.write(data)


if __name__ == "__main__":
    geotiff = rasterio.open('./geotiffs/all_bands_800.geotiff')

    parser = argparse.ArgumentParser("extract_bands")
    parser.add_argument("band",
                        help="The band to extract from a geotiff image",
                        type=int)
    parser.add_argument("band_name",
                        help="Name of band, f.i. <red> or <near-IR>",
                        type=str)
    args = parser.parse_args()

    assert 1 <= args.band <= 19, '<BAND> has to be in [1, 19].'
    extract_band(geotiff, args.band, args.band_name)

    # compose_bands_to_rgb(geotiff)

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
