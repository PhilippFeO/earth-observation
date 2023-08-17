"""
Reads image of band {red, green, blue} in <args.band_dir> (i.e., all images have to be transfered there beforehand) and combines them to an RGB image. This saved under '<args.band_dir>/out/combined_bands.tif'.
"""
import os
import rasterio
from extract_bands import adjust_values
import argparse
import numpy as np

# TODO: adjust band values individually to control the influence of a band <17-08-2023>

p = argparse.ArgumentParser("compose_bands")
p.add_argument("band_dir",
               help="Directory containing the images for composing.",
               type=str)
args = p.parse_args()


directory = os.fsencode(args.band_dir)
files = os.listdir(directory)
out_meta = None
bands = None
for i, f in enumerate(files):
    # decode b-string to normal string
    f = f.decode('utf-8')
    band_file = os.fsdecode(f'{args.band_dir}/{f}')
    if band_file.endswith(('.tif', '.TIF')):
        band = rasterio.open(band_file)
        if bands is None:
            out_meta = band.meta.copy()
            bands = np.empty((3,
                              out_meta['height'],
                              out_meta['width']))
        # Place band at right position for RGB image
        if 'B2' in f:  # 'B2' is blue
            bands[2] = band.read(1)
        elif 'B3' in f:  # 'B3' is green
            bands[1] = band.read(1)
        else:  # Remaining is 'B4', which is red
            bands[0] = band.read(1)
        band.close()

bands = adjust_values(bands, 7000, 16000)

# Create directory for output image
out_dir = f'{args.band_dir}/out'
try:
    os.mkdir(out_dir)
except FileExistsError:
    print('out-directory exists')

out_meta.update(count=3,
                dtype=rasterio.uint8,
                nodata=0)
print(f'{out_meta = }')

# save combined bands
with rasterio.open(f'{out_dir}/combined_bands.tif', 'w', **out_meta) as m:
    m.write(bands)
