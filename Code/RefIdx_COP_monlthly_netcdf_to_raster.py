#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
__author__ = 'James T. Dietrich'
__contact__ = 'geojamesdietrich@gmail.com'
__copyright__ = '(c) James Dietrich 2024'
__license__ = 'MIT'
__date__ = 'Oct 2024'
__version__ = '0.0.1'
__status__ = "inital release"
__url__ = "https://github.com/global_refractive_index_532"

"""
Name:           RefIdx_COP_netcdf_to_raster.py
Compatibility:  Python 3.7
Description:    Converts Copernicus Marine Environment Monitoring Service (CMEMS) 
                ARMOR3D L4 - Multi Observation Global Ocean 3D Salinity and
                Temperature netCDF files to annual raster stacks  
                
                Use the data access FORM to request data:
                    Works with MONTHLY REP and NRT datasets
                    1. Variables: Sea water salinity, Sea water temperature
                    2. Area of Interest: Global or specific area
                    3. Date Range: Start and End Dates
                        ** If using whole years: Raster Bands will be months (1=Jan...)
                        ** If using partial years: Raster band 1 will be the
                            first month in the date range
                    4. Depth Range: 0 > 0 (for surface layer only)
                https://data.marine.copernicus.eu/product/MULTIOBS_GLO_PHY_TSUV_3D_MYNRT_015_012/services
                
                To Run:
                    0. Create a python environment with the required libraries
                    1. Edit the nc_files list below
                        For 1 file  : nc_files = [filepath_1]
                        For 2+ files: nc_files = [filepath_1, filepath_2, ...]
                    2. Run this script
                    3. Outputs will be in the same folder an the input files

Requires:       netCDF4, rasterio, numpy, pandas, os

Dev ToDo:       

AUTHOR:         James T. Dietrich
ORGANIZATION:   Washington State Department of Ecology
Contact:        geojamesdietrich@gmail.com
Copyright:      (c) James Dietrich 2024

Licence:        MIT
"""

# IMPORTS
from netCDF4 import Dataset
import numpy as np
import pandas as pd
import os
import rasterio as rio

# EDIT THIS SECION
#-----
# Paths to Copernicus netCDF download(s)

# 1 file example
#nc_files = ['F:/RefractiveIndex_copy/Copernicus/Copernicus_NRT_2023_2024/dataset-armor-3d-nrt-monthly_1726674866365.nc']

# 2+ files example
nc_files = ['F:/RefractiveIndex_copy/Copernicus/Copernicus_REP_2016_2022/dataset-armor-3d-rep-monthly_1726674866365.nc',
            'F:/RefractiveIndex_copy/Copernicus/Copernicus_NRT_2023_2024/dataset-armor-3d-nrt-monthly_1726674866365.nc']

#-----

# main processing loop
# For each file in the input nc_files list
for ncf in nc_files:
    
    # load the netcdf file, extract the data type prefix, print the filename
    data = Dataset(ncf)
    prefix = ncf.split("-")[-2]
    print(ncf)
    
    # extract the lat, long limits of the dataset
    lat = np.array([data.variables['latitude'][:].data]).T
    long = np.array([data.variables['longitude'][:].data])
    E,N = np.meshgrid(long,lat)
    
    # calculate the dates of the different layers in the netCDF file
    #   convert seconds from 1070-1-1 to datetime
    ncf_dates = pd.DataFrame(np.array(data.variables['time'][:].data),columns = ['secs'])
    ncf_dates.secs = pd.to_timedelta(ncf_dates.secs,'s')
    ncf_dates['date'] = pd.to_datetime('1970/01/01 0:0:0') + ncf_dates.secs
    
    # for each unique year contained in the netCDF file...
    for year in ncf_dates.date.dt.year.unique():
        
        # starter variables: months processed, refractive index stats arrays
        months_in_year = 0
        ri_avg = np.full([long.shape[0],lat.shape[0]],np.nan)
        ri_min = np.full([long.shape[0],lat.shape[0]],np.nan)
        ri_max = np.full([long.shape[0],lat.shape[0]],np.nan)
        
        # determine output path from input netcdf file, create output filder if
        #   it does not exist
        out_path = "%s/monthly_rasters"%(os.path.split(ncf)[0])

        if os.path.exists(out_path) == False:
            os.makedirs(out_path)
        
        # output raster parameters: resolution (0.25 degrees), rasterio generic
        #   lat/long transformation
        res = 0.25
        transform = rio.Affine.translation(-180,lat[0,0]-0.125) * rio.Affine.scale(res, res)
        
        # calculate the number of layers for the output raster
        #   < 12 months: number of layers present
        #   ==12 months: all 12 months, +2 bands for annual average and annual range
        month_in_ncf = ncf_dates.date[ncf_dates.date.dt.year == year].dt.month.shape[0]
        if month_in_ncf == 12:
            month_in_ncf = 14
        
        # create and open output raster file
        dst = rio.open('%s/armor3d_nw532_%s_monthly_%s.tif'%(out_path,year,prefix),
                      'w', driver='GTiff', height=lat.shape[0], 
                      width=long.shape[1], count=month_in_ncf, dtype=np.dtype('float32'), 
                      crs=rio.CRS.from_string("EPSG:4326"), transform=transform, compress='lzw')
        
        # for each unique date(month) in the selected year...
        for i,date in enumerate(ncf_dates.date[ncf_dates.date.dt.year == year]):
            
            #add 1 to months processed counter, print feedback
            months_in_year += 1
            print('%s - Months: %i of %i'%(date.strftime('%Y_%b'),
                                              months_in_year,month_in_ncf))
            
            # read salinity and temperature data from netCDF, convert to
            #   refractinve index at 532 nm 
            s = data.variables['so'][i].data[0]
            t = data.variables['to'][i].data[0]
            ri = s *(1.6*10**-8 * t**2 - 1.05*10**-6 * t + 0.000199611) - 2.02*10**-6 * t**2 - 7.95113*10**-6 * t + 1.336
            
            # debug
            # print('\t\t %0.4f - %0.4f'%(np.nanmin(ri),np.nanmax(ri)))
            print('\t\t Loop: %i'%(i))
            
            # if first time through loop, initiate stats layers
            #   subsiquent loops, add to stats layers
            if months_in_year == 1:
                ri_avg = ri
                ri_min = ri
                ri_max = ri
            else:
                ri_avg = np.nansum(np.dstack((ri_avg,ri)),2)
                ri_min = np.fmin(ri_min, ri)
                ri_max = np.fmax(ri_max, ri)
            
            # write raster band, set band description to the year and month
            dst.write_band(months_in_year, ri)
            dst.set_band_description(months_in_year,date.strftime('%Y_%b'))
            
            # if 12 months are present - add stats layers
            #   band 13 = annual average
            #   band 14 = annual range
            if months_in_year == 12:
                dst.write_band(13,ri_avg/12.0)
                dst.set_band_description(13,"%i_AVG"%year)
                dst.write_band(14,ri_max - ri_min)
                dst.set_band_description(14,"%i_RANGE"%year)
        
        # when year concludes, close raster layer, start next year if availible
        dst.close()