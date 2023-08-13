# Some explainatory comments regarding rasterio can be found in extract_bands.py

import rasterio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image


def save_sc_geotiff(sc_ndvi, meta, name='ndvi-sc'):
    ''' Save single channel NDVI image as geotiff. <sc_ndvi> contains values in [0, 1] (of type <float32>) '''
    meta.update(count=1)
    with rasterio.open(f'{geotiff_dir}/{name}.geotiff', 'w', **meta) as img:
        sc_ndvi = (sc_ndvi * 255).astype('uint8')
        img.write(sc_ndvi, 1)


def save_whylgn_geotiff(whylgn_ndvi, meta, name='ndvi-whylgn'):
    ''' Save an image as geotiff representing the NDVI using 3 channels to have a gradient from white/yellow to green instead of pure gray scale. '''
    meta.update(count=3)
    with rasterio.open(f'{geotiff_dir}/{name}.geotiff', 'w', **meta) as img:
        # Convert from [0, 1] to [0, 255]
        whylgn_ndvi = (whylgn_ndvi * 255).astype('uint8')
        # <whylgn_ndvi.shape> = (800, 777, 4) but has to be (3, 800, 777)
        whylgn_ndvi = np.transpose(whylgn_ndvi, (2, 0, 1))
        img.write(whylgn_ndvi)


def save_whylgn_legend(whylgn_ndvi, cmap, name='ndvi-whylgn-legend'):
    ''' Save gradient NDVI using a matplotlib plot and display a color gradient legend based on <cmap> '''
    width_pixels = 1000
    height_pixels = 1000
    # Convert to inches
    plt.figure(figsize=(width_pixels / 100, height_pixels / 100))

    plt.imshow(whylgn_ndvi, cmap=cmap)
    plt.colorbar()  # Show color gradient, s. doc for setting ticks
    # plt.show()
    plt.axis('off')
    plt.savefig(f'{geotiff_dir}/{name}.png')


if __name__ == "__main__":
    geotiff_dir = "./geotiffs"

    # Open geotiff image and set up geotiff specific meta data
    gt = rasterio.open(f'{geotiff_dir}/all_bands_800.geotiff')
    out_meta = gt.meta.copy()
    out_meta.update(dtype=rasterio.uint8,
                    nodata=0)

    # Read bands
    b4red = gt.read(4)
    b5nearIR = gt.read(5)

    # Close image
    gt.close()

    # Calculate NDVI = (NIR - Red) / (NIR + Red)
    # Avoid dividing by 0 by adding smallest possible float to the divisor
    ndvi = np.divide(b5nearIR - b4red, b5nearIR +
                     b4red + np.finfo(float).eps)  # has type 'float32'

    # Adjust values (s. docstring of <adjust_values>)
    min, max = 0.0, 0.4
    # truncate values
    ndvi = np.clip(ndvi, min, max)
    # scale [.0, .4] to [.0, 1.]
    ndvi = ndvi * 2.5

    # Create a colormap using LinearSegmentedColormap
    #   Own colormap because built-in <YlGn> maps white, i.e. 'nodata' onto bright yellow which doesn't look appealing 'outside' the image. I prefere plain white.
    colors = ["white", "yellow", "green"]
    color_map = matplotlib.colors.LinearSegmentedColormap.from_list(
        "WhYlGn", colors)

    # Apply colormap. Result is a RGBA array but I only need RGB values.
    whylgn_ndvi = color_map(ndvi)[:, :, :3]

    # Saving np-array as PNG (not embedded in a plot)
    matplotlib.image.imsave(f'{geotiff_dir}/ndvi-whylgn.png', whylgn_ndvi)

    # Save image as matplotlib plot with color gradient legend
    save_whylgn_legend(whylgn_ndvi, color_map)

    # Save yellow-green NDVI image as geotiff
    save_whylgn_geotiff(whylgn_ndvi, out_meta.copy())

    # Save one channel NDVI image as geotiff
    save_sc_geotiff(ndvi, out_meta.copy())
