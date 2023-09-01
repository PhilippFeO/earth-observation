import os
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.axes_grid1 import make_axes_locatable
from itertools import pairwise


may15_img = rasterio.open(
    './USGS/image_working_dir/ndvi_2022-05-15/out/sc_NDVI.geotiff')
# Due to difference negative values may15 emerge => unsigned ints are necessary
may15 = may15_img.read(1).astype('uint16')

may31_img = rasterio.open(
    './USGS/image_working_dir/ndvi_2022-05-31/out/sc_NDVI.geotiff')
# Due to difference negative values may31 emerge => unsigned ints are necessary
may31 = may31_img.read(1).astype('uint16')

july_img = rasterio.open(
    './USGS/image_working_dir/ndvi_2022-07-18/out/sc_NDVI.geotiff')
# Due to difference negative values may15 emerge => unsigned ints are necessary
july = july_img.read(1).astype('uint16')

dates = ('2022-05-15',  '2022-05-31',  '2022-07-18')
ndvis = (may15, may31, july)
data = zip(ndvis, dates)

# Set the same font size for tick labels and titles
font_size = 15  # Adjust this to your desired font size
plt.rcParams.update({'font.size': font_size})
# Create a figure with gridspec to control subplot sizes
fig = plt.figure(figsize=(15, 8))
fig.suptitle('NDVI differences')

# 2 rows (1 for matrices, 1 for colorbar),
# 3 columns (2 for matrices, 1 for spacing)
gs = fig.add_gridspec(2, 3, width_ratios=[6, 1, 6], height_ratios=[4, 1])

# Create subplots for matrices
ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 2])
axs = (ax1, ax2)

"""Plot difference"""
for i, months in enumerate(pairwise(data)):
    """Calculate ndvi difference"""
    index1, date1 = months[0]
    index2, date2 = months[1]
    diff = index1 - index2
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
    mask = np.load('./shapes_and_masks/munich/munich-ds.npy')
    cmap_diff[:, :, 3] = mask

    ax = axs[i]
    ax.imshow(cmap_diff)
    ax.axis('off')
    ax.set_title(f"Between {date1} and {date2}")


"""Add a common colorbar for both matrices in the second row (horizontal)"""
# Add an additional subplot in the second row and span entire row
ax3 = fig.add_subplot(gs[1, :])
ax3.axis('off')

# Some ChatGPT stuff
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
cbar.ax.set_xticklabels((-1., .5, .0, .5, 1.))
# cbar.ax.tick_params(labelsize=20)

plt.tight_layout()
# plt.show()

out_dir = './USGS/image_working_dir/ndvi_differences'
try:
    os.mkdir(out_dir)
    print(f"Created:\n\t{out_dir}")
except FileExistsError:
    pass
path_to_image = os.path.join(out_dir, 'ndvi_difference.png')
plt.savefig(path_to_image)


# """Save as GeoTIFF to preserve geographical metadata"""
# # Apply mask to reestablish nodata areas
# masked_diff = np.where(mask, diff, 0)
# path_to_image = './USGS/image_working_dir/diff.TIF'
# with rasterio.open(path_to_image, 'w', **may15_img.meta) as img:
#     img.write((masked_diff * 255).astype(np.int8), 1)
