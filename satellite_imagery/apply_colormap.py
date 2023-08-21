import matplotlib
import numpy as np
import numpy.typing as npt


def apply_colormap(index_array: npt.NDArray[np.float32],
                   colors: list[str, ...]):
    """Color map :index_array: containing values of an index like NDVI to :colors:.

    :index_array: The calculated index as 2d numpy array, should only contain values in [0, 1].
    :colors: Color palette for the colormap

    :returns: A RGBA numpy array in the dimensions of the :index_array:

    """
    # Create a colormap using LinearSegmentedColormap
    color_map = matplotlib.colors.LinearSegmentedColormap.from_list(
        "", colors)

    # Apply colormap; Result is a RGBA array
    cmap_index_array = color_map(index_array)

    return cmap_index_array, color_map
