# %%
import rasterio
import numpy as np
import glob
import geopandas as gpd
from shapely.geometry import Polygon
from shapely.geometry import box
from skimage.measure import label, regionprops
import matplotlib.pyplot as plt

# %%
# Events
events = ['010', '050', '100', '500']

# Path to your rasters
# for event in events:
    # raster_files = glob.glob(f'./data/{event}yr/*.tif')
# raster_files = glob.glob('./data/{events}/*.tif')
raster_files = glob.glob('./data/010yr/*.tif')

raster_files

# %%
# Create a mapping from origin values to raster filenames
# get the tail of the filepaths in raster_files and exclude the extension
value_to_filename = {i + 1: raster_file.split('/')[-1].split('\\')[-1].split('.')[0] for i, raster_file in enumerate(raster_files)}

# value_to_filename = {i + 1: raster_files[i] for i in range(len(raster_files))}
value_to_filename
# %%
# Open the first raster to get metadata
with rasterio.open(raster_files[0]) as src:
    meta = src.meta
    height, width = src.shape  # Get dimensions
    transform = src.transform

meta

# %%
epsg = meta['crs'].to_epsg()

# %%
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

# %%
# Apply NoData mask for the origin_array
origin_array[max_array == -9999] = -9999  # Set origin to NoData where max_array is NoData
meta.update(dtype='int16', nodata=-9999)  # Set NoData to -1 (or any other preferred value)
# %%
# Save the max raster to disk
with rasterio.open('./out/010yr_Franken_MaxWSE.tif', 'w', **meta) as dst:
    dst.write(max_array.astype('float32'), 1)

# %%
# Save the origin raster to disk
with rasterio.open('./out/010yr_Franken_Origin.tif', 'w', **meta) as dst:
    dst.write(origin_array.astype('int16'), 1)

# %%
# Plotting the max_array
# Create a masked array where NoData values are set to np.nan
masked_max = np.ma.masked_where(max_array == -9999, max_array)
# Create a colormap
cmap = plt.cm.viridis  # Choose your colormap
cmap.set_bad(color='lightgray')  # Set the color for NoData values
# Plot the masked array
plt.imshow(masked_max, cmap=cmap, interpolation='nearest')
plt.colorbar(label='Max Values')
plt.title('Max Raster Visualization')
plt.show()

# %%
# plot origin_array
plt.figure(figsize=(12, 8))  # Increase figure size for more space
# Create a masked array where NoData values are set to np.nan
masked_origin = np.ma.masked_where(origin_array == -9999, origin_array)

# %%
import matplotlib.colors as mcolors
# Create a colormap
# Define a custom colormap with 4 distinct colors
custom_colors = ['#FF0000', '#FFFF00', '#FFA500', '#008000']  # Red, Yellow, Orange, Green
cmap = mcolors.ListedColormap(custom_colors)
# cmap = plt.cm.Set1 # Choose your colormap
cmap.set_bad(color='lightgray')  # Set the color for NoData values

# Plot the masked array
plt.imshow(masked_origin, cmap=cmap, interpolation='nearest')
cbar = plt.colorbar(label='Raster Origin', ticks=[1, 2, 3, 4])

# Set colorbar tick labels using the raster filenames
cbar.ax.set_yticklabels([value_to_filename[i] for i in range(1, 5)])
# plt.colorbar(label='Raster Origin', ticks=[1, 2, 3, 4], 
#              format=plt.FuncFormatter(lambda x, _: value_to_filename[int(x)-1]))

# Create a legend with colors matching the custom colormap
handles = []
for i, (value, filename) in enumerate(value_to_filename.items()):
    handle_color = custom_colors[i]  # Corresponding color for the legend
    handles.append(plt.Line2D([0], [0], marker='o', color='w', label=filename,
                               markersize=10, markerfacecolor=handle_color))  # Use the custom colors

# Position the legend outside of the plot area
# plt.legend(title='Raster Origins', handles=handles, loc='upper left', bbox_to_anchor=(1.3, 1))

plt.title('Origin Raster Visualization')
plt.tight_layout()  # Adjust layout to make room for legend
plt.show()


# %%
# Efficient GeoDataFrame creation by labeling contiguous regions
label_image = label(origin_array != -9999)  # Label contiguous areas with valid origin values
geometries = []
origins = []

# Use regionprops to extract bounding boxes for regions
for region in regionprops(label_image):
    # Get the bounding box and convert it to a Polygon
    min_row, min_col, max_row, max_col = region.bbox
    minx = min_col * transform[0] + transform[2]
    miny = max_row * transform[4] + transform[5]
    maxx = max_col * transform[0] + transform[2]
    maxy = min_row * transform[4] + transform[5]

    # Create the bounding box polygon and store origin
    geometries.append(box(minx, miny, maxx, maxy))
    origins.append(origin_array[min_row, min_col])  # Use any pixel in the region

# Create GeoDataFrame with geometries and origins
gdf = gpd.GeoDataFrame({'origin': origins}, geometry=geometries)
# gdf.set_crs(epsg=meta['crs'].to_epsg(), inplace=True, allow_override=True)

# %%
gdf.plot(column='origin', cmap='tab20', legend=True)

# %%
# drop the -9999 values
gdf = gdf[gdf['origin'] != -9999]
gdf.plot(column='origin', cmap='tab20', legend=True)
# %% 
# Dissolve polygons by origin value to merge neighboring cells
gdf_dissolved = gdf.dissolve(by='origin', as_index=False)

# %%
gdf_dissolved

# %%
# %% Plot dissolved GeoDataFrame
plt.figure(figsize=(12, 8))

# Reuse the same colormap and legend styling from origin raster plot
gdf_dissolved.plot(column='origin', cmap=cmap, legend=False, ax=plt.gca())

# Add the same custom legend
handles = [plt.Line2D([0], [0], marker='o', color='w', label=value_to_filename[i+1],
                      markersize=10, markerfacecolor=custom_colors[i]) for i in range(4)]
plt.legend(handles=handles, title="Precip Event Origins", loc='upper left', bbox_to_anchor=(1.05, 1))

plt.title("Dissolved Origins Vector Plot")
plt.tight_layout()
plt.show()
# %%
# Save to a shapefile or other vector format
# Save to a shapefile with the origin as an attribute
gdf_dissolved.to_file('./out/010yr_origin_maxWSE.shp')

# %%
gdf_dissolved
# %%
