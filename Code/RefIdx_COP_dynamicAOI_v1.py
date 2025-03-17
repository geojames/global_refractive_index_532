#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
__author__ = 'James T. Dietrich'
__contact__ = 'geojamesdietrich@gmail.com'
__copyright__ = '(c) James Dietrich 2025'
__license__ = 'MIT'
__date__ = '2025 MAR 16'
__version__ = '0.0.1'
__status__ = "inital release"
__url__ = "https://github.com/..."

"""
Name:           RefIdx_COP_dynamicAOI_v1.py
Compatibility:  Python 3.12
Description:    Converts Copernicus Marine Environment Monitoring Service (CMEMS) 
                ARMOR3D L4 - Multi Observation Global Ocean 3D Salinity and
                Temperature data to refractive index based on wavelength.
                
                Creates dynamic subsets via Copernicus python api
                
Requires:       pandas, numpy, matplotlib,
                copernicusmarine, rioxarray, cmcrameri

Dev ToDo:       1) make a callable function

AUTHOR:         James T. Dietrich
ORGANIZATION:   Washington State Department of Ecology
Contact:        geojamesdietrich@gmail.com
Copyright:      (c) James Dietrich 2025

Licence:        MIT
"""

# IMPORTS
import os
import re
import copernicusmarine
import pandas as pd
import numpy as np
import rioxarray
from cmcrameri import cm
from matplotlib import pyplot as plt

# Copernicus Marine Login - 
# - should only need to run once, will save a credentials file
if copernicusmarine.login(check_credentials_valid = True) == False:
    copernicusmarine.login()
else:
    pass

# MAIN
#%% Refractive index
#   Quan and Fry (1994) - Convertes temp (°C) and Salinity (PSU or ‰) to 
#          
def quanfry_ri(wl,S,T):
    '''
    Parameters
    ----------
    wl : float
        Wavelength (nm) for the refractive index calculation
    S : Array - Salinity
        Array (1-D or 2-D) of salinity values (PSU or ‰).
    T : Array - Water Temperature
        Array (1-D or 2-D) of water temperature values (°C) <Must match the 
        dimentions of salinity>

    Returns
    -------
    ri : Array
        Array for refrative index values mathching the dimentions of the inputs.

    '''

    ri = (1.31405 + ( 0.0001779 + -0.00000105 * T + 0.000000016 * T**2 ) *
          S + -0.00000202 * T**2 + (( 15.868 + 0.01155*S + -0.00423 *T)/wl) +
          (-4382/wl**2) + (1145500/wl**3))

    return ri

#%%
# SETUP (Change these values)
weekly = True       # weekly values (True - Default), monthly values (False) 
rep = False         # Reprocessed data (True), Near Real Time data (False - Default)
plot = True         # create basic plot of the data (False - Default)
export = True       # create GeoTiff files, one for each date in the query (True - Default)
wl = 532.0          # target wavelength for the refractive index conversion (532 (green) - Default)

project_name = 'carrib'
out_path = 'E:/RefractiveIndex_copy/dynam_ri'

# Area of interest
#   [min longitude, max longitude, 
#    min latitude, max latitude]    (negaitves for west and south)
aoi = [-99,-58,
       7,33]

# Date range: "yyyy-mm-dd"
#   for single dataset make start and end the same
start_date = "2025-1-1"
end_date = "2025-3-1"

# END SETUP


# ---------------------------
# create an output path string
#   create new folder if none exists, fix periods, space, dash in project name
project_name_fix = re.sub(r'(\. )|( )|(-)','_',project_name)
out_path_proj = "%s/%s"%(out_path, project_name_fix)

if os.path.exists(out_path_proj) == False:
    os.mkdir(out_path_proj)

# set datatype based on inputs
if weekly == True:
    if rep == True:
        dataset = "dataset-armor-3d-rep-weekly"
    else:
        dataset = "dataset-armor-3d-nrt-weekly"
else:
    if rep == True:
        dataset = "dataset-armor-3d-rep-monthly"
    else:
        dataset = "dataset-armor-3d-nrt-monthly"

# Check for dataset extent limitations, fix if values are outside the map
if aoi[0] <= -180:
    aoi[0] = -179.875
if aoi[1] >= 180:
    aoi[1] = 179.875
if aoi[2] <= -90:
    aoi[2] = -82.125
if aoi[3] >= 90:
    aoi[3] = 89.875

# query the Copernicus Marine database with input datatype, aoi, and dates
#   output is a multi-dim xarray
armor = copernicusmarine.open_dataset(
  dataset_id="dataset-armor-3d-nrt-weekly",
  minimum_longitude = aoi[0],
  maximum_longitude = aoi[1],
  minimum_latitude = aoi[2],
  maximum_latitude = aoi[3],
  start_datetime="%sT00:00:00"%(start_date),
  end_datetime="%sT00:00:00"%(end_date),
  minimum_depth=0,
  maximum_depth=0,
)

# write CRS value to the xarray (EPSG:4326 = WGS84/ITRF2014)
armor.rio.write_crs("EPSG:4326", inplace=True)

# create an dataframe with the dates of the queried subset
ncf_dates = pd.DataFrame(armor.time.data, columns = ['date'])
ncf_dates['date_end'] = ncf_dates['date'] + pd.Timedelta(days = 6)
ncf_dates['start_doy'] = ncf_dates['date'].dt.dayofyear
ncf_dates['end_doy'] = ncf_dates['date_end'].dt.dayofyear

# user feedback on how many dates were included
print('Downloaded subset with %i dates'%(ncf_dates.shape[0]))

# perform the conversion to refractive index from the ARMOR data
#   calculates a new dataset int eh xarray for ref idx
armor = armor.assign(ri = lambda x: quanfry_ri(wl,x.so,x.to))

# rename the output based on the input wavelength
ri_wl_name = "ref_idx_%i"%(int(wl))
armor = armor.rename({'ri': ri_wl_name})

# for each date in the availible date:
#   PLOT (if true) with matplotlib, save PNG file
#   Export (if true) to GeoTiff
for i,r in enumerate(armor[ri_wl_name]):
    print("  %i:%i -- %s"%(i+1,ncf_dates.shape[0],ncf_dates['date'][i].strftime("%Y %b %d")))
    
    date_string = "%s_%s"%(ncf_dates['date'][i].strftime("%Y%m%d"),
                           ncf_dates['date_end'][i].strftime("%Y%m%d"))
    
    if plot == True:
        
        ratio = (np.absolute(r.coords['longitude'].data.max() -
                             r.coords['longitude'].data.min()) /
                 np.absolute(r.coords['latitude'].data.max() -
                             r.coords['latitude'].data.min()))
        
        plt.figure(figsize=[5*ratio+1,5])
        plt.pcolor(r[0].coords['longitude'].data, 
                   r[0].coords['latitude'].data,r[0].data, cmap = cm.roma_r,
                   vmin=np.round(armor[ri_wl_name].min().data.item(),4),
                   vmax=np.round(armor[ri_wl_name].max().data.item(),4))
        title_str = "Refractive Index @ %0.1f nm\n%s - %s"%(wl,ncf_dates['date'][i].strftime("%Y %b %d"),
                               ncf_dates['date_end'][i].strftime("%Y %b %d"))
        
        plt.xlim(r[0].coords['longitude'].data.min(),r[0].coords['longitude'].data.max())
        plt.ylim(r[0].coords['latitude'].data.min(),r[0].coords['latitude'].data.max())
        
        plt.colorbar()
        plt.title(title_str)
        plt.tight_layout()
        
        out_file = '%s/armor3d_nw532_%s_%s.png'%(out_path_proj,
                                                project_name_fix,
                                                date_string)
        
        plt.savefig(out_file,dpi=300)
        plt.close()
        
    if export == True:
                
        out_file = '%s/armor3d_nw532_%s_%s.tif'%(out_path_proj,
                                                project_name_fix,
                                                date_string)
        r.rio.to_raster(out_file)

print('** OUTPUTS > %s'%out_path_proj)
