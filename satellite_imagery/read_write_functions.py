import numpy as np
import rasterio
import os
import matplotlib.image
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
from apply_colormap import apply_colormap
from embed_geometry import embed_geometry

""" Function regarding saving images """


def bands_to_array(bands_dir: str,
                   band_order: tuple[str, ...]):
    """Reads the bands specified in :band_order: into an array (keeping the order).

    :bands_dir: Directory of the bands to put in a np.ndarray.
    :band_order: The order of bands to fill the output array. Since the function iterates over all files in :bands_dir: and the order is not arbitrary, it is necessary to define the order in which the bands are red into the output array. 
    :returns: Tuple containing an array containing all bands as they were defined in :band_order: and the corresponding meta data

    """
    out_meta = None
    nmb_bands = len(band_order)
    bands = None  # image dimensions have to be red from metadata
    files = (os.path.join(bands_dir, file)
             for file in os.listdir(bands_dir))
    for file in files:
        # Skip <out>-directory, ie. only iterate over TIFF-files
        if file.endswith(('.tif', '.TIF')):
            band = rasterio.open(file)
            # Initialize band array (especially with image dimensions)
            if bands is None:
                out_meta = band.meta.copy()
                bands = np.empty((nmb_bands,
                                  out_meta['height'],
                                  out_meta['width']))
            # Fill band array with band values
            for i, b in enumerate(band_order):
                if b in file:
                    bands[i] = band.read(1)
                    break
            band.close()
    # Update meta data
    out_meta.update(count=nmb_bands,
                    dtype=rasterio.uint8,
                    nodata=0)
    return bands, out_meta


""" Function regarding saving images """


def create_out_dir(bands_dir: str) -> str:
    """Create the output directory':bands_dir:/out' for the produced image.

    :bands_dir: The directory to create an 'out' dir in. Usually, the image for processing are suited in :bands_dir:.

    :returns: Path of the created directory"""
    out_dir = f'{bands_dir}/out'
    try:
        os.mkdir(out_dir)
        print(f'Created:\n\t{out_dir}')
    except FileExistsError:  # Error occurs when <out_dir> exists; this is nothing to worry about
        pass
    return out_dir


def save_cmap_legend(index_array, cmap, path_to_image):
    ''' Save gradient NDWI using a matplotlib plot and display a color gradient legend based on <cmap> '''
    width_pixels = 1000
    height_pixels = 1000
    # Convert to inches
    plt.figure(figsize=(width_pixels / 100, height_pixels / 100))

    plt.imshow(index_array, cmap=cmap)
    plt.colorbar()  # Show color gradient, s. doc for setting ticks
    # plt.show()
    plt.axis('off')
    plt.savefig(path_to_image)


def save_sc_geotiff(sc_index, meta, path_to_image):
    ''' Save single channel index image as geotiff. <sc_index> contains values in [0, 1] (of type <float32>) '''
    meta.update(count=1)
    with rasterio.open(path_to_image, 'w', **meta) as img:
        sc_index = (sc_index * 255).astype('uint8')
        img.write(sc_index, 1)


def generate_plots(out_dir: str,
                   index_name: str,
                   index,
                   out_meta: dict,
                   colors: list[str, ...],
                   boundary: bool,
                   shape_mask_dir: str,
                   shape_mask_name: str) -> None:
    """Superlevel function to create all plots.

    :out_dir: Directory where plots are saved.
    :index_name: Name of the index to generate plots for.
    :index: Array containing the index values.
    :out_meta: Meta data for the single channel GeoTIFF.
    :colors: List of colors defining a Colormap.
    :boundary: Embed the boundary of the area of interest into the plot.
    :shape_mask_dir: Directory containing the shape (.shp) and and mask ('.npy') of the area of interest.
    :shape_mask_name: Name of the shapefile and mask without their extension (because they differ, .shp & .npy respectively).
    :returns: None

    """
    # cmap_index is a RGBA array
    cmap_index, color_map = apply_colormap(index, colors)

    # Replace alpha channel by mask
    mask_name = f"{shape_mask_name}.npy"
    mask = np.load(os.path.join(shape_mask_dir, mask_name))
    cmap_index[:, :, 3] = mask

    """Save images."""
    # Create output directory for produced images
    out_dir = create_out_dir(out_dir)

    """Save different configurations and formats"""
    # Embed boundary if wished
    shape_name = f"{shape_mask_name}.shp"
    ax = embed_geometry(os.path.join(shape_mask_dir, shape_name),
                        cmap_index,
                        out_meta,
                        boundary)
    path_to_image = os.path.join(out_dir, f"{index_name}")
    # print(path_to_image)
    plt.savefig(path_to_image)
    # Add colorbar
    cbar = plt.colorbar(ScalarMappable(cmap=color_map), ax=ax)
    cbar.ax.tick_params(labelsize=30)
    # Save with boundary and legend
    path_to_image = os.path.join(out_dir, f"legend_{index_name}.png")
    plt.savefig(path_to_image)


    # Saving np-array as PNG for valid transparency (not embedded in a plot)
    path_to_image = os.path.join(out_dir, f"cmap_{index_name}.png")
    matplotlib.image.imsave(path_to_image, cmap_index)

    # Matplotlib plot with color gradient legend
    # path_to_image = os.path.join(out_dir, 'legend_cmap_index.png')
    # save_cmap_legend(cmap_index, color_map, path_to_image,
    # x_boundary=x, y_boundary=y)

    # One channel index image as geotiff
    path_to_image = os.path.join(out_dir, f"sc_{index_name}.geotiff")
    save_sc_geotiff(index, out_meta.copy(), path_to_image)
    #
    # """ Evaluate index """
    # evaluate_index(index_name, index, .75, mask)
