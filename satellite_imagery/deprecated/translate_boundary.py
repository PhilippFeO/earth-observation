import geopandas as gpd
import numpy as np


def translate_boundary(geojson: str,
                       shape_image: tuple[int, int],
                       shape_geometry: tuple[int, int]):
    """Translates the boundary to its geographical correct position by adding half of the dimensional difference to it's vertices.
    Example: Buffered version of munich occupies more space, fi. (1000, 900). But Munich itself only needs (750, 600). To fit the boundary onto the buffered image, we add (900-600)/2 to X and (1000-750)/2 to Y (images are saved as height x width).

    Disclaimer: The boundary probably doesn't fit geographically correct with the underlying image.

    :geojson: geojson file to calculate the boundary (via geopandas)
    :returns: 2D Tuple containing x and y coordinates respectively

    """
    mgdf = gpd.read_file(geojson)
    mgdf['boundary'] = mgdf.boundary
    boundary_linestring = mgdf['boundary'].iloc[0]
    x, y = boundary_linestring.xy
    x = np.array(x)
    y = np.array(y)
    # Align with coordinate axes
    x = x - x.min()
    y = y - y.min()
    # Because cmap_ndvi resembles an image
    #   shape[0] is number of rows/height/y
    #   shape[1] is number of columns/width/x
    x = x / x.max() * shape_geometry[1]
    y = y / y.max() * shape_geometry[0]  # mask.shape[0]
    # Because image is plotted, and origin lies in upper left not lower left
    # mirroring is necessary
    y = y * -1
    y = y - y.min()
    # Translate by half of dimension difference to "center" it
    y = y + (shape_image[1] - shape_geometry[1]) / 2
    x = x + (shape_image[0] - shape_geometry[0]) / 2

    return x, y
