# NDVI #
This directory documents my calculation of the NDVI of central bavaria (near the lower center lies Munich). Via Google Earth Engine I retrieve the proper satellite imagery form [Landsat 8 – Wikipedia](https://en.wikipedia.org/wiki/Landsat_8) as `GeoTIFF` containing all 19 bands. The following steps include:
  - Reading necessary bands from image
  - Preprocessing values for higher quality results (f.i. not whole 16bit color range is exploited)
  - Calculating NDVI
  - Saving image/generating plot

Long term goal: Use a Geopolygon to filter the city of Munich and calculate it's NDVI.

- [extract_bands.py](./extract_bands.py): Isolates band and saves it under [./geotiffs/](./geotiffs/); Usage: `python3 extract_bands.py BAND BAND_NAME`.
- [ndvi.py](./ndvi.py): Calculates the NDVI; currently it produces a bunch of images `GeoTIFF`s and `PNG`s, because I don't know which format works best for upcoming tasks (probably `GeoTIFF` due to additional embedded geo-metadata).

## Produced images
The NDVI:
![](./geotiffs/ndvi-whylgn-legend.png)
(`matplotlib`'s scaling of the image is lower than the original file. I don't know why and how to fit to it's original dimensions.)

There is also a RGB image of the scene but GitHub doesn't embed the file and I don't know why. Anyway, you can find it in [./geotiffs/](./geotiffs/) (as `rgb.png`).
![](./geotiffs/rgb.tiff)
