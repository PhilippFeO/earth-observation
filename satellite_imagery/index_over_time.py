import os
import re
import argparse
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from rasterio.plot import show
from matplotlib.cm import ScalarMappable
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.axes_grid1 import make_axes_locatable
from itertools import pairwise
from embed_geometry import embed_geometry


p = argparse.ArgumentParser(prog='index_over_time')
p.add_argument('paths',
               help='Paths to the directories containing the indices to calculate their differences. Should be submitted chronologically from oldest to newest.',
               nargs='+',
               type=str)
args = p.parse_args()

dates = []
ndvis = []
meta = None

# Reversed order because iterating pairwise and
# substracting "the latter from the former" is done
# first. This guarantees consistency with enumerate().
for geotiff_path in reversed(args.paths):
    geotiff = rasterio.open(geotiff_path)
    # Save meta data, used for embedding the boundary of Munich
    if meta is None:
        meta = geotiff.meta
    data = geotiff.read(1).astype(np.uint16)
    ndvis.append(data)

    # Retrieve date from the geotiff_path
    compounds = geotiff_path.split('_')
    m = re.search(r'\d{4}-\d{2}-\d{2}', geotiff_path)
    date = m.group(0)
    dates.append(date)


"""Configure plot in general"""
# Set the same font size for tick labels and titles
font_size = 20  # Adjust this to your desired font size
plt.rcParams.update({'font.size': font_size})
# Create a figure with gridspec to control subplot sizes
fig = plt.figure(figsize=(25, 14))
fig.suptitle('NDVI over time')

# 2 rows: 1 for matrices, 1 for colorbar
# columns in pairs: matrix, spacing (except for last matrix)
n_images = len(args.paths) - 1
ncol = 2 * n_images - 1
ncol_pairs = n_images - 1
w_ratios = ([6, 1] * ncol_pairs) + [6]
gs = fig.add_gridspec(2, ncol, width_ratios=w_ratios, height_ratios=[4, 1])

# Create subplots for matrices
axs = tuple(fig.add_subplot(gs[0, i])
            for i in range((2 * ncol_pairs), -1, -2))


"""Plot difference"""
# Here becomes reversed iterating over args.paths important
for i, data_pair in enumerate(pairwise(zip(ndvis, dates))):
    """Calculate ndvi difference"""
    # numbering reflects chronologic order of the data
    index2, date2 = data_pair[0]
    index1, date1 = data_pair[1]
    diff = index2 - index1
    # Map [-255, 255] onto [0, 1]
    diff = diff + 255
    diff = diff / 510

    """Difference may be negativ in the first place. Negative values imply
    decreased vegetation health. By mapping onto [0, 1] to apply the colormap
    the subinterval [0, .5] resembles these negative values with worsened
    vegetation."""

    """Apply colormap and mask"""
    cmap = LinearSegmentedColormap.from_list("", ['red', "lightgray", 'green'])
    cmap_diff = cmap(diff)
    # Replace alpha channel by mask to visually remove patches outside area of interest
    mask = np.load('./shapes_and_masks/munich/munich-bbox.npy')
    cmap_diff[:, :, 3] = mask

    ax = axs[i]
    ax.axis('off')
    ax.set_title(f"From {date1} to {date2}")
    # ax.imshow(cmap_diff) doesn't work because geographical information is lost
    # Rasterio preserves them.
    # => Adding further geo information like boundary with geopandas possible
    show(cmap_diff.transpose(2, 0, 1),
         transform=meta['transform'],
         ax=ax)
    # TODO: Add condition <08-09-2023>
    if True:
        geom_file = './shapes_and_masks/munich/munich-ds.shp'
        embed_geometry(geom_file, ax)


"""Add a common colorbar for both matrices in the second row (horizontal)"""
# Add an additional subplot in the second row and span entire row
ax3 = fig.add_subplot(gs[1, :])
ax3.axis('off')

# ChatGPT did the next two line
divider = make_axes_locatable(ax3)
cax = divider.append_axes("bottom",
                          size="100%",
                          pad=0.1)
cbar = fig.colorbar(ScalarMappable(cmap=cmap),
                    cax=cax,
                    orientation='horizontal')
# Label according to NDVI difference. NDVI is in [0, 1],
# hence difference in [-1, 1]
cbar.ax.set_xticks((.0, .25, .5, .75, 1.))
cbar.ax.set_xticklabels((-1., -.5, .0, .5, 1.))

plt.tight_layout()
# plt.show()

out_dir = './USGS/image_working_dir/ndvi_difference'
try:
    os.mkdir(out_dir)
    print(f"Created:\n\t{out_dir}")
except FileExistsError:
    pass
dates_str = '_'.join(reversed(dates))
path_to_image = os.path.join(out_dir, f'ndvi_difference_bbox_{dates_str}.png')
plt.savefig(path_to_image)


# """Save as GeoTIFF to preserve geographical metadata"""
# # Apply mask to reestablish nodata areas
# masked_diff = np.where(mask, diff, 0)
# path_to_image = './USGS/image_working_dir/diff.TIF'
# with rasterio.open(path_to_image, 'w', **may15_img.meta) as img:
#     img.write((masked_diff * 255).astype(np.int8), 1)
