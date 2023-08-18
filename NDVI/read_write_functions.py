import numpy as np
import rasterio
import os


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
