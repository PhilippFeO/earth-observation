import numpy as np
import geopandas as gpd
from rasterio.plot import show
import matplotlib.pyplot as plt


def embed_geometry(geometry_file: str, index: np._typing.NDArray, meta: dict):
    """Embed a geometry geographically correct on a cropped satellite image using rasterio and geopandas.

    :geometry_file: Path to the file holding the geometry, fi. the boundary of a city
    :index: Image to embend the geometry onto, fi. an array containing NDVI values
    :meta: meta data of any band used for the index calculation. The value of the "transform" key is necessary to generate plots using rasterio.
    :returns: The axis of the plot (used for additional configurations like adding a colorbar)

    """
    # Read/Calculate geometry
    mgdf = gpd.read_file(geometry_file)
    mgdf['geometry'] = mgdf.boundary

    fig, ax = plt.subplots()
    x, y = index.shape[0], index.shape[1]
    x, y = y / 100 * 2, x / 100 * 2
    # Set the desired figure size in inches
    fig.set_size_inches(x, y)
    fig.set_dpi(600)  # Set the desired DPI value
    # Plot raster
    # rasterio needs (height, width, bands) order
    show(index.transpose(2, 0, 1),
         transform=meta['transform'],
         ax=ax)
    # Add geometry, fi. boundary via GeoPandas
    mgdf.plot(ax=ax, color='black', linewidth=6)
    # Some settings
    plt.axis('off')
    return ax
