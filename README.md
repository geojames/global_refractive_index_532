# Welcome to the Global Refractive Index Code Page Dynamic AOIs and multiple wavelengths

Converts Copernicus Marine Environment Monitoring Service (CMEMS) ARMOR3D L4 - Multi Observation Global Ocean 3D Salinity and Temperature netCDF files
to GeoTIFF rasters.

> #### The methodology for these data are published - (click the Watch and Star button above for updates)
> **Dietrich, J. T., & Parrish, C. E. (2025). Development and Analysis of a Global Refractive Index of Water Data Layer for Spaceborne and Airborne Bathymetric Lidar. Earth and Space Science, 12(3), e2024EA004106. https://doi.org/10.1029/2024EA004106**
#### Data Citation
[![DOI](https://zenodo.org/badge/872811345.svg)](https://doi.org/10.5281/zenodo.13968330)
> **Dietrich, J.T. and C. Parrish. 2024. Github: global_refractive_index_532: Version 1.1. Zenodo, DOI: [10.5281/zenodo.13968330](https://doi.org/10.5281/zenodo.13968330)**

### _Authors_

> #### James T. Deitrich
> Applied Coastal Research and Engineering Section, Washington Department of Ecology
> #### Christopher Parrish
> Civil and Construction Engineering, Oregon State University


#### Changelog:
2025 Mar 16 - added dynamic date and AOI processing via Copernicus Marine python API. 
2025 Jun 3 - cleaned up, added notebook version of dynamic AOI code
## Files
RefIdx_COP_dynamicAOI_v1.py: Standalone code for processing dynamic date and AOI (testing, clunky)
RefIdx_COP_dynamicAOI_v2.py: dynamic date and AOI processing as a callable function (see RefIdx_COP_dynamicAOI_v2_demo.py for example)
RefIdx_COP_dynamicAOI_v2.ipynb: contains all of the fuctions + demo at the bottom

#### Requirements
**You must have a Copernicus Marine Login - https://data.marine.copernicus.eu/register**

scipy, numpy, pandas, matplotlib, geopandas, rasterio, netCDF4, cmcrameri, copernicusmarine, rioxarray
```
conda create -n geo-env python=3.11 scipy numpy pandas matplotlib
conda activate geo-env
pip install 'geopandas[all]' rasterio netCDF4 cmcrameri copernicusmarine rioxarray
```
##### Main Fuction
See RefIdx_COP_dynamicAOI_v2_demo.py or RefIdx_COP_dynamicAOI_v2.ipynb for example calling the core funtion

```python
cop_ref_idx(start_date, end_date, aoi, wave_len, project_name, out_path, 
            weekly = True, nrt = True, plot = False, export_tiff = True)
Parameters
----------
start_date : string
    Text for start date, format = "yyyy-mm-dd".
end_date : string
    Text for end date, format = "yyyy-mm-dd".
aoi : list/array
    list/array of the geographic coords for the area of interest\n
    [min longitude, max longitude, min latitude, max latitude] <negative vals for west and south>.
    0.25 degree incurments are best
wave_len : float / array
    target wavelength(s) for the refractive index conversion.
    If array is used for multiple wavelengths, outputs will be for each wavelength
project_name : string
    a text string for the project/site name (used for file outputs).
out_path : path
    string for the file path for the outputs (if any) [forward slash, /, for folder separator].
weekly : bool, optional
    Use ARMOR3D weekly datasets (The default is True), False = use ARMOR3D monthly values.
nrt : bool, optional
    Use ARMOR3D Near-Real-Time (NRT) data (Default = True). False = use ARMOR3D Reprocessed (REP) data.
plot : bool, optional
    Export basic time-series graphics (PNG @ 300 dpi). The default is False.
export_tiff : bool, optional
    Export a geotiff file for each date in the input date range. (Default = True).

Returns
-------
xarray: xarray of converted refractive index values with associated spatial Coordinates and CRS (WGS84).

(Optional - if plot or export_geotiff == True)
output_path: text string of the output path for image and tiff files
```