import os
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from rasterio.plot import show
from matplotlib.cm import ScalarMappable
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.axes_grid1 import make_axes_locatable
from itertools import pairwise
from embed_geometry import embed_geometry


may15_img = rasterio.open(
    './USGS/image_working_dir/ndvi_2022-05-15_bbox/out/sc_NDVI.geotiff')
# Due to difference negative values may15 emerge => unsigned ints are necessary
may15 = may15_img.read(1).astype('uint16')

may31_img = rasterio.open(
    './USGS/image_working_dir/ndvi_2022-05-31_bbox/out/sc_NDVI.geotiff')
# Due to difference negative values may31 emerge => unsigned ints are necessary
may31 = may31_img.read(1).astype('uint16')

july_img = rasterio.open(
    './USGS/image_working_dir/ndvi_2022-07-18_bbox/out/sc_NDVI.geotiff')
# Due to difference negative values may15 emerge => unsigned ints are necessary
july = july_img.read(1).astype('uint16')

"""Configure plot in general"""
# Set the same font size for tick labels and titles
font_size = 20  # Adjust this to your desired font size
plt.rcParams.update({'font.size': font_size})
# Create a figure with gridspec to control subplot sizes
fig = plt.figure(figsize=(25, 14))
fig.suptitle('NDVI over time')

# 2 rows (1 for matrices, 1 for colorbar),
# 3 columns (2 for matrices, 1 for spacing)
gs = fig.add_gridspec(2, 3, width_ratios=[6, 1, 6], height_ratios=[4, 1])

# Create subplots for matrices
ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 2])
# Reversed order because iterating pairwise and
# substracting "the latter from the former" is done
# first. This guarantees consistency with enumerate().
axs = (ax2, ax1)

# Same
dates = ('2022-07-18', '2022-05-31', '2022-05-15')
ndvis = (july, may31, may15)

"""Plot difference"""
for i, data_pair in enumerate(pairwise(zip(ndvis, dates))):
    """Calculate ndvi difference"""
    # numbering reflects chronologic order of the data
    index2, date2 = data_pair[0]
    index1, date1 = data_pair[1]
    diff = index2 - index1
    # Map [-255, 255] onto [0, 1]
    diff = diff + 255
    diff = diff / 510

    """Difference may15 be negativ in the first place. Negative values imply
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
         transform=may15_img.meta['transform'],
         ax=ax)
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
path_to_image = os.path.join(out_dir, 'ndvi_difference_bbox.png')
plt.savefig(path_to_image)


# """Save as GeoTIFF to preserve geographical metadata"""
# # Apply mask to reestablish nodata areas
# masked_diff = np.where(mask, diff, 0)
# path_to_image = './USGS/image_working_dir/diff.TIF'
# with rasterio.open(path_to_image, 'w', **may15_img.meta) as img:
#     img.write((masked_diff * 255).astype(np.int8), 1)
