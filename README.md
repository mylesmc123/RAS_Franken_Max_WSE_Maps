# HEC-RAS Frankenstein Max WSE Map Maker

![image](https://github.com/user-attachments/assets/8c2341c2-c1e3-46ed-acd7-e2ba5edf68b6)


This repo consists of a Python script that will take output geotiff Max WSE rasters that have been exported from HEC-RAS, and for a set of rasters, compute the max for each cell for the given set of rasters. This is primarily being done for the GLO project for The Water Institute to compare input rainfall sources for various frequency events. For example, for each frequency event return interval (10yr, 25yr, 50yr, 100yr, 200yr, 500yr) there are rainfall inputs of:

- Atlas 14
- Bivariare Right (Surge Dominate)
- Bivariate (Most Likely)
- Bivariate Left (Precip Dominate)

## Outputs

##### This script outputs 3 products:
- **Frankenstein Max WSE Raster** - Represents the max value for each cell across the 4 precip inputs for a given frequency event.

  
    ![image](https://github.com/user-attachments/assets/172d5ed3-0779-49b2-b723-7957ecfe7e4a)

- **Origin Raster** - Represents the origin precip input that is used to create the Frankenstein Max WSE Raster. This is used to understand from which precip input do the max WSE values come from.

  
    ![image](https://github.com/user-attachments/assets/c3e451d2-429b-4597-a45d-9414a610c7ec)

- **Origin Vector** - A vectorized representation of the Origin Raster that is dissolved to simplify the visualization of showing for what areas the max WSE is originating from a particular precip input. This output if actually being produced in ArcPro because the speed of the rasterize function is just so much faster than geopandas without multithreading. The ArcPro project is here for TWI folks: "V:\projects\p00659_dec_glo_phase3\01_processing\GIS\GIS_for_Figures"

![Franken Max WSE Origin 100yr](https://github.com/user-attachments/assets/b401c765-5b43-43df-810c-8d4addff96f7)


