import numpy as np


def read_mask_array_meta(mask_path: str):
    """Read the shape of a saved numpy array (resembling the mask of a geometry).

    :mask_path: Path to a numpy array containing a mask of the geometry
    :returns: Tuple containing the shape of 2D numpy array

    """
    shape_mask_array = None
    with open(mask_path, 'rb') as npy:
        # ESSENTIAL! Without this call, it doesn't work!
        np.lib.format.read_magic(npy)
        # shape is saved as first index
        shape_mask_array = np.lib.format.read_array_header_1_0(npy)[0]
    return shape_mask_array
