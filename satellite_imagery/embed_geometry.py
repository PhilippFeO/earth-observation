import geopandas as gpd


def embed_geometry(geometry_file: str,
                   ax=None):
    """Embed a geometry geographically correct on a cropped satellite image using rasterio and geopandas.

    :geometry_file: Path to the file holding the geometry, fi. the boundary of a city
    :ax: Ax to plot the boundary on
    :returns: The axis of the plot (used for additional configurations like adding a colorbar)

    """
    # Read/Calculate geometry
    mgdf = gpd.read_file(geometry_file)
    mgdf['geometry'] = mgdf.boundary
    # Add geometry, fi. boundary via GeoPandas
    mgdf.plot(ax=ax, color='black', linewidth=2)
    return ax
