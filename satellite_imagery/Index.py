import os
import rasterio
import numpy as np
import numpy.typing as npt
import matplotlib.image
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
from matplotlib.colors import LinearSegmentedColormap
from rasterio.plot import show
from embed_geometry import embed_geometry


class Index:
    def __init__(self,
                 band_order: tuple[str, ...],
                 img_dir: str):
        self.band_order = band_order
        self.img_dir = img_dir
        self.index_name = type(self).__name__
        bands, self.geotiff_meta = self.__read_bands()
        # Dict with K=Band & V=NPArray
        self.bands = {band: bands[i] for i, band in enumerate(self.band_order)}
        # Array holding the values of the index
        self.index: npt.NDArray = None  # Set in calculate()

    def __read_bands(self):
        """Reads the bands specified in :band_order: into an array (keeping the order).

        :band_order: The order of bands to fill the output array. Since the function iterates over all files in :bands_dir: and the order is not arbitrary, it is necessary to define the order in which the bands are red into the output array.
        :returns: Tuple containing an array containing all bands as they were defined in :band_order: and the corresponding meta data

        """
        out_meta = None
        nmb_bands = len(self.band_order)
        bands = None  # image dimensions have to be red from metadata
        files = (os.path.join(self.img_dir, file)
                 for file in os.listdir(self.img_dir))
        for file in files:
            # Skip <out>-directory, ie. only iterate over TIFF-files
            if file.endswith(('.tif', '.TIF')):
                band = rasterio.open(file)
                # Initialize band array (especially with image dimensions)
                if bands is None:
                    out_meta = band.meta.copy()
                    bands = np.empty((nmb_bands,
                                      out_meta['height'],
                                      out_meta['width']))
                # Fill band array with band values
                for i, b in enumerate(self.band_order):
                    if b in file:
                        bands[i] = band.read(1)
                        break
                band.close()
        # Update meta data
        out_meta.update(count=nmb_bands,
                        dtype=rasterio.uint8,
                        nodata=0)
        return bands, out_meta

    def __create_out_dir(self) -> str:
        """Create the output directory':bands_dir:/out' for the produced image.

        :bands_dir: The directory to create an 'out' dir in. Usually, the image for processing are suited in :bands_dir:.

        :returns: Path of the created directory"""
        out_dir = f'{self.img_dir}/out'
        try:
            os.mkdir(out_dir)
            print(f'Created:\n\t{out_dir}')
        except FileExistsError:  # Error occurs when <out_dir> exists; this is nothing to worry about
            pass
        return out_dir

    def generate_plots(self,
                       colors: list[str, ...],
                       shape_mask_dir: str,
                       shape_mask_name: str,
                       boundary: bool = False,
                       embedded_geom: str = None) -> None:
        """Superlevel function to create all plots.

        :colors: List of colors defining a Colormap.
        :boundary: Embed the boundary of the area of interest into the plot.
        :shape_mask_dir: Directory containing the shape (.shp) and and mask ('.npy') of the area of interest.
        :shape_mask_name: Name of the shapefile and mask without their extension (because they differ, .shp & .npy respectively).
        :embedded_geom: TODO
        :returns: None

        """
        # Apply colormap; Result is a RGBA array
        color_map = LinearSegmentedColormap.from_list("", colors)
        cmap_index = color_map(self.index)

        # Replace alpha channel by mask
        mask_name = f"{shape_mask_name}.npy"
        mask = np.load(os.path.join(shape_mask_dir, mask_name))
        cmap_index[:, :, 3] = mask

        """Save images."""
        # Create output directory for produced images
        out_dir = self.__create_out_dir()

        """Save different configurations and formats"""
        fig, ax = plt.subplots()
        x, y = cmap_index.shape[0], cmap_index.shape[1]
        # Set the desired figure size in inches
        x, y = y / 100 * 2, x / 100 * 2
        fig.set_size_inches(x, y)
        fig.tight_layout()
        ax.axis('off')
        # Place raster on axes
        # rasterio needs (height, width, bands) order
        show(cmap_index.transpose(2, 0, 1),
             transform=self.geotiff_meta['transform'],
             ax=ax)
        # Embed boundary (if wished)
        if boundary:
            geom_file = os.path.join(shape_mask_dir, f"{embedded_geom}.shp")
            embed_geometry(geom_file, ax)
        # Save without transparencs
        path_to_image = os.path.join(out_dir, f"{self.index_name}")
        # TODO: Kann nicht invertiert werden und sieht mit Ferblegende blöd aus :(. Aber ohne tight_layout() habe ich kein SCHÖNES Bild mit transparentem Hintergrund, da ich die Matrix später per matplot.image speichere und die Matrix die Geometrie nicht enthält. <01-09-2023>
        #   Idee: Rand hinzufügen
        fig.savefig(path_to_image, facecolor='none')

        # Save with colorbar legend
        # Add colorbar
        cbar = plt.colorbar(ScalarMappable(cmap=color_map), ax=ax)
        cbar.ax.tick_params(labelsize=30)
        # Save legend
        path_to_image = os.path.join(out_dir, f"legend_{self.index_name}.png")
        fig.savefig(path_to_image)

        # Saving with transparency outside area of interest
        path_to_image = os.path.join(out_dir, f"cmap_{self.index_name}.png")
        matplotlib.image.imsave(path_to_image, cmap_index)

        # One channel index image as geotiff
        path_to_image = os.path.join(out_dir, f"sc_{self.index_name}.geotiff")
        meta = self.geotiff_meta.copy()
        meta.update(count=1)
        with rasterio.open(path_to_image, 'w', **meta) as img:
            sc_index = (self.index * 255).astype('uint8')
            img.write(sc_index, 1)
        # save_sc_geotiff(self.index, self.geotiff_meta, path_to_image)


class NDVI(Index):

    """Class for calculating the NDVI."""

    def __init__(self,
                 band_order: tuple[str, ...],
                 img_dir: str):
        Index.__init__(self, band_order, img_dir)

    def calculate(self, min: float = 0., max: float = 1.):
        b4red = self.bands[self.band_order[0]]
        b5nearID = self.bands[self.band_order[1]]
        ndvi = np.divide(b5nearID - b4red,
                         b5nearID + b4red + np.finfo(float).eps)
        self.index = np.clip(ndvi, min, max)


class NDWI(Index):

    """Calculate the NDWI"""

    def __init__(self,
                 band_order: tuple[str, ...],
                 img_dir: str):
        Index.__init__(self, band_order, img_dir)

    def calculate(self, min: float = 0., max: float = 1.):
        b3green = self.bands[self.band_order[0]]
        b5nearIR = self.bands[self.band_order[1]]
        ndwi = np.divide(b3green - b5nearIR,
                         b3green + b5nearIR + np.finfo(float).eps)
        self.index = np.clip(ndwi, min, ndwi.max()) / ndwi.max() * 10
