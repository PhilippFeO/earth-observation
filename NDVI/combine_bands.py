import os
import rasterio
from extract_bands import adjust_values
import argparse
import numpy as np

# TODO: adjust band values individually to control the influence of a band <17-08-2023>

p = argparse.ArgumentParser("compose_bands")
p.add_argument("image_dir",
               help="Directory containing the images for composing.",
               type=str)
args = p.parse_args()


directory = os.fsencode(args.image_dir)
files = os.listdir(directory)
out_meta = None
nmb_bands = len(files)
bands = None
for i, file in enumerate(files):
    # decode b-string to normal string
    band_tif = os.fsdecode(f'{args.image_dir}/{file.decode("utf-8")}')
    if band_tif.endswith(('.tif', '.TIF')):
        band_tif = rasterio.open(band_tif)
        if bands is None:
            out_meta = band_tif.meta.copy()
            bands = np.empty(
                (nmb_bands, out_meta['height'], out_meta['width']))
        bands[i] = band_tif.read(1)
        print(f'{np.min(bands[i]) = }')
        print(f'{np.max(bands[i]) = }')

bands = adjust_values(bands, 5000, 10000)

# Create directory for output image
out_dir = f'{args.image_dir}/out'
try:
    os.mkdir(out_dir)
except FileExistsError:
    print('out-directory exists')

out_meta.update(count=nmb_bands,
                dtype=rasterio.uint8,
                nodata=0)
print(f'{out_meta = }')

# save combined bands
with rasterio.open(f'{out_dir}/combined_bands.tif', 'w', **out_meta) as m:
    m.write(bands)
