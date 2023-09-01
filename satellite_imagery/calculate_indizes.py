from Index import NDVI, NDWI

ndvi = True
ndwi = False

"""NDVI"""
if ndvi:
    Ndvi = NDVI(('B4', 'B5'),
                './USGS/image_working_dir/ndvi_2022-07-18_bbox')
    Ndvi.calculate()
    Ndvi.generate_plots(('red', 'yellow', 'green'),
                        './shapes_and_masks/munich/',
                        'munich-bbox',
                        True,
                        'munich-ds')

"""NDWI"""
if ndwi:
    Ndwi = NDWI(('B3', 'B5'),
                './USGS/image_working_dir/ndwi_2022-05-15/')
    Ndwi.calculate()
    Ndwi.generate_plots(('yellow', 'blue'),
                        False,
                        './shapes_and_masks/munich/',
                        'munich-ds')
