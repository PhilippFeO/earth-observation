# Satellite Imagery #
This directory documents my calculation of the NDVI of Munich. Via [USGS Earth Explorer](https://earthexplorer.usgs.gov/) I retrieve the proper satellite imagery form [Landsat 8 – Wikipedia](https://en.wikipedia.org/wiki/Landsat_8). The steps include:
  - Cropping Munich's geopolygon 
  - Preprocessing data for higher quality results (f.i. not whole 16bit color range is exploited)
  - Calculating an index, f.e. [NDVI – Wikipedia](https://en.wikipedia.org/wiki/Normalized_difference_vegetation_index) or [NDWI – Wikipedia](https://en.wikipedia.org/wiki/Normalized_difference_water_index), evaluating vegetation or water respectively
  - Saving image/generating plot
I use `numpy`, `rasterio`, `geopandas`, `shapely` and `matplotlib` to conduct all operations.

## Roadmap
Exploring more indices (maybe related to water)  
~~Evaluate quantitatively the NDVI~~
~~Use a Geopolygon to filter the city of Munich and calculate it's NDVI.~~

## Overview
- [adjust_values.py](./adjust_values.py): Satellite data must be clipped to improve quality. Full explanation given in the file directly.
- [geojson2shapefile_downsampling.py](./geojson2shapefile_downsampling.py): Converts a GeoJSON file of the city of Munich containing it's districts into a Shapefile resembling the border of Munich (without districts) and applies downsampling because the USGS Earth Explorer only permits <500 vertices.
- [isolate_shape.py](./isolate_shape.py): Corps a geometry saved as a shapefile from a GeoTIFF and also it's according mask as boolean array.
- [Index.py](./Index.py): Class resembling the logic needed to calculate and process an Index like the NDVI.
- [index_differences.py](./index_differences.py) Calculate the difference over time of consecutive indices (s. `#### NDVI over time`)
- [WIP] [make_rgb.py](./make_rgb.py): Combines the red, green and blue bands to an RGB file.

## Produced images
### NDVI
The NDVI, data was collected on 2022-05-15, the greener, the more (healthy) vegetation:
![](./USGS/image_working_dir/ndvi_2022-05-15/out/legend_NDVI.png)
(`matplotlib`'s scaling of the image is lower than the original file. I don't know why and how to zoom/scale it.)  
#### NDVI over time
The image below shows the development of the NDVI over two periods in Munich and it's surroundings. Red indicates a decrease in the NDVI, green an increase, ie. reduced/improved vegetation health.
![](./USGS/image_working_dir/ndvi_difference/ndvi_difference_bbox.png)
(The NDVI is in [0, 1], hence it's difference in [-1, 1].)

### NDWI
The [Normalized difference water index – Wikipedia](https://en.wikipedia.org/wiki/Normalized_difference_water_index) is used to monitor changes related to water content in water bodies, using green and NIR wavelengths. Data is from 2022-05-15. Clearly visible is the Isar, some lakes and in the north the olympic regatta area.
![](./USGS/image_working_dir/ndwi_2022-05-15/out/cmap_NDWI.png)  
Disclaimer: The values were multiplied by 10 to increase visibility.
