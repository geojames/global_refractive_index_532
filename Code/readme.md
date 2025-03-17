# Welcome to the Global Refractive Index Code Page

The code presented here was used to create the data layers in the **Data** folder.

Converts Copernicus Marine Environment Monitoring Service (CMEMS) ARMOR3D L4 - Multi Observation Global Ocean 3D Salinity and Temperature netCDF files
to annual GeoTIFF raster stacks (one band per month).

#### Changelog:
2025 Mar 16 - added dynamic date and AOI processing iva Copernicus Marine python API. 

## for
RefIdx_COP_dynamicAOI_v1.py: Standalone code for processing dynamic date and AOI
RefIdx_COP_dynamicAOI_v2.py: dynamic date and AOI processing as a callable function (see cop_dynamic_V2_func_test.py for example)

## for RefIdx_COP_weekly_netcdf_to_raster.py & RefIdx_COP_monlthly_netcdf_to_raster.py3.

### Data Download
1. Use the Monthly data access forms (monthly or weekly datasets:
   - [ARMOR3D data Form](https://data.marine.copernicus.eu/product/MULTIOBS_GLO_PHY_TSUV_3D_MYNRT_015_012/download?dataset=dataset-armor-3d-nrt-monthly_202012)
2. Variables: Sea water salinity, Sea water temperature
3. Area of Interest: Global or specific area
4. Date Range: Start and End Dates
   - If using whole years: Raster bands will be months (1=Jan...)
   - If using partial years: Raster band 1 will be the first month in the date range
5. Depth Range: 0 : 0 (for surface layer only)

### Data Processing
0. Create a python environment with the required libraries (environment.txt for required libraries)
1. Edit the nc_files list variable
   - For 1 file  : nc_files = [filepath_1]
   - For 2+ files: nc_files = [filepath_1, filepath_2, ...]
2. Run this script
3. Outputs will be in the same folder an the input files, subflder "monthly\_rasters"
