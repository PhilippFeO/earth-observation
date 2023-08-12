# Some explainatory comments regarding rasterio can be found in extract_bands.py

import rasterio
import numpy as np
from extract_bands import adjust_values


if __name__ == "__main__":
    geotiff_dir = "./geotiffs"

    # Open geotiff image and set up geotiff specific meta data
    gt = rasterio.open(f'{geotiff_dir}/all_bands_800.geotiff')
    out_meta = gt.meta.copy()
    out_meta.update(count=1,
                    dtype=rasterio.uint8,
                    nodata=0)

    # Read bands
    b4red = gt.read(4)
    b5nearIR = gt.read(5)

    # Close image
    gt.close()

    # Calculate NDVI = (NIR - Red) / (NIR + Red)
    # Avoid dividing by 0 by adding smallest possible float to the divisor
    ndvi = np.divide(b5nearIR - b4red, b5nearIR +
                     b4red + np.finfo(float).eps)

    # Adjust values (s. docstring of <adjust_values>)
    min, max = 0.0, 0.4
    ndvi = adjust_values(ndvi, min, max)

    # Save NDVI image
    with rasterio.open(f'{geotiff_dir}/ndvi.tiff', 'w', **out_meta) as ndvi_img:
        ndvi_img.write(ndvi, 1)
