import numpy as np
import rasterio
import os
import matplotlib.pyplot as plt

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
