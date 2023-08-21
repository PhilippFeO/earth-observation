'''
Linear Mapping
In a nutshell: Map values from [min, max] (subset of [0, 65536]) to [0, 255]

All bands containing geotiff image contains values in [0, 65536]
    (to be precise, [u]int16).
But the range is just partially exploited (technical reasons, s. link below),
f.i. only values from 5000-20000.
To avoid dark images, this effective range is mapped onto 0-255.
    > https://gis.stackexchange.com/questions/304180/what-are-the-min-and-max-values-of-map-addlayer-on-google-earth-engine

The original template (s. NDVI-Munich.ipynb) removes values <7000 and >16000, ie.
maps the range [7000, 16000] onto [0, 255] (by specifying a <min> and <max> argument in a
<parameters>-dictionary). This has to be replicated and it's done by solving
  7000m + t = 0,
  16000m + t = 255
      => m = 255/(16000-7000), t = 7000*m
    '''

import numpy as np


def adjust_values(data, min, max):
    # Leave <nodata>-values untouched
    # Map range min-max onto 0-255.
    #   =>  make <min> the smallest value in the image
    #       make <max> the highest value in the image
    #   By doing so <tmp * m - t> won't produce values outside 0-255.
    #       (Before, I didn't truncate and had artifacts in the rgb-image)
    tmp = np.clip(data, min, max)
    m = 255 / (max - min)
    t = min * 255 / (max - min)
    tmp = tmp * m - t  # The actual mapping
    return tmp.astype('uint8')  # Convert values to uint8 according to metadata
