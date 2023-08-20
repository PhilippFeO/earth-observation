import argparse
import numpy as np
import matplotlib.image
from read_write_functions import bands_to_array, create_out_dir, save_cmap_legend, save_sc_geotiff
from evaluate_index import evaluate_index


if __name__ == "__main__":
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

    """ Calculate ndwi = (NIR - Red) / (NIR + Red) """
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

    """ Apply colormap """
    # Create a colormap using LinearSegmentedColormap
    #   Own colormap because built-in <YlGn> maps white, i.e. 'nodata' onto bright yellow which doesn't look appealing 'outside' the image. I prefere plain white.
    colors = ["yellow", "blue"]
    color_map = matplotlib.colors.LinearSegmentedColormap.from_list(
        "WhYlGn", colors)

    # Apply colormap; Result is a RGBA array
    cmap_ndwi = color_map(ndwi)

    # Replace alpha channel by mask
    mask = np.load('./shapes_and_masks/munich/munich_mask.npy')
    cmap_ndwi[:, :, 3] = mask

    """ Save images """
    # Create output directory for produced images
    out_dir = create_out_dir(args.image_dir)

    # Saving np-array as PNG (not embedded in a plot)
    matplotlib.image.imsave(f'{out_dir}/cmap_ndwi.png', cmap_ndwi)

    # Save image as matplotlib plot with color gradient legend
    save_cmap_legend(cmap_ndwi, color_map, f"{out_dir}/legend_cmap_ndwi.png")

    # Save yellow-green ndwi image as geotiff
    # Remove alphy channel, GeoTIFF can't handle alpha values (as far as I know)
    # no_alph_ndwi = color_map(ndwi)[:, :, :3]
    # save_whylgn_geotiff(no_alph_ndwi, out_meta.copy())

    # Save one channel ndwi image as geotiff
    save_sc_geotiff(ndwi, out_meta.copy(), f"{out_dir}/sc_ndwi.geotiff")

    """ Evaluate NDWI """
    evaluate_index('NDWI', ndwi * max, .33, mask)
