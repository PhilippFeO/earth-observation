import rasterio
import argparse


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
