import rasterio
import numpy as np
import glob
import geopandas as gpd
from shapely.geometry import Polygon
from shapely.geometry import box
from skimage.measure import label, regionprops
import matplotlib.pyplot as plt

# Events
events = ['010', '050', '100', '500']

# Path to your rasters
for event in events:
    print (f'Processing {event}yr')
    raster_files = glob.glob(f'./data/{event}yr/*.tif')
    
    # Create a mapping from origin values to raster filenames
    # get the tail of the filepaths in raster_files and exclude the extension
    value_to_filename = {i + 1: raster_file.split('/')[-1].split('\\')[-1].split('.')[0] for i, raster_file in enumerate(raster_files)}

    # value_to_filename = {i + 1: raster_files[i] for i in range(len(raster_files))}
    value_to_filename
    
    # Open the first raster to get metadata
    with rasterio.open(raster_files[0]) as src:
        meta = src.meta
        height, width = src.shape  # Get dimensions
        transform = src.transform
    
    epsg = meta['crs'].to_epsg()

    
    # Initialize an empty array for max values and origins
    max_array = None
    # Change shape to match the raster dimensions  
    origin_array = np.full((height, width), -9999, dtype='int16')  # Default to -1 for no origin

    # Loop through each raster
    for idx, raster_file in enumerate(raster_files):
        with rasterio.open(raster_file) as src:
            data = src.read(1)

            if max_array is None:
                max_array = data.copy()
                origin_array[:] = idx  + 1  # Set origin to idx + 1 to avoid 0
            else:
                # Update max values and track origins
                mask = data > max_array
                max_array = np.where(mask, data, max_array)
                origin_array[mask] = idx + 1  # Set origin to idx + 1 to avoid 0

    
    # Apply NoData mask for the origin_array
    origin_array[max_array == -9999] = -9999  # Set origin to NoData where max_array is NoData
    meta.update(dtype='int16', nodata=-9999)  # Set NoData to -1 (or any other preferred value)
    
    # Save the max raster to disk
    with rasterio.open(f'./out/{event}yr_Franken_MaxWSE.tif', 'w', **meta) as dst:
        dst.write(max_array.astype('float32'), 1)
    print (f'{event}yr Max WSE saved to disk.')

    
    # Save the origin raster to disk
    with rasterio.open(f'./out/{event}yr_Franken_Origin.tif', 'w', **meta) as dst:
        dst.write(origin_array.astype('int16'), 1)
    print (f'{event}yr Origin saved to disk.')