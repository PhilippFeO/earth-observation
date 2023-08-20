"""Evaluate a given index (like NDVI, NDWI) of Munich quantitatively by calculating it's average index value and the percentage where it is > :threshold: (arbitrarily chosen)."""

import numpy as np


def evaluate_index(index_name, index_array, index_threshold, mask):
    """ Evaluates the provided :index_array: resembling an index like NDVI by calulating it's average and percentage where it exceeds :index_threshold:.  

    :index_name: Name of the index, f.i. NDVI
    :index_array: 2d numpy array containing the calculated index
    :index_threshold: Threshold for calculating the percentage exceeding :index_threshold:
    :mask: Mask of the geometry used when calculating :index_array:
    """

    # Calculate area of Munich based on it's mask
    area_munich = np.sum(mask)

    # Calculate average index
    avg = np.sum(index_array) / area_munich
    print(f"The average {index_name} of Munich is {avg:.2f} ...")

    # Calculate percentage of index_array > index_threshold
    # Filter/count all entries with an index_array >= index_threshold
    tmp = index_array[index_array >= index_threshold]
    percentage = tmp.shape[0] / area_munich
    print(f"{percentage:.2f}% of Munich have an {index_name} >= {index_threshold:.2f} ...")
    print("\t...when image was taken.")
