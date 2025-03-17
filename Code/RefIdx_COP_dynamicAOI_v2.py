#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
__author__ = 'James T. Dietrich'
__contact__ = 'geojamesdietrich@gmail.com'
__copyright__ = '(c) James Dietrich 2025'
__license__ = 'MIT'
__date__ = 'JAN 2025'
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
def cop_ref_idx(start_date, end_date, aoi, wave_len, 
                project_name, out_path, 
                weekly = True, nrt = True, plot = False, export_tiff = True):
    
    """
    Copernicus ARMOR3D Refractive Index Creation

    Parameters
    ----------
    start_date : string
        Text for start date, format = "yyyy-mm-dd".
    end_date : string
        Text for end date, format = "yyyy-mm-dd".
    aoi : list/array
        list/array of the geographic coords for the area of interest\n
        [min longitude, max longitude, min latitude, max latitude] <negative vals for west and south>.
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
    """  
    
    # ---------------------------
    
    # check wavelength input - if single value create a single value list
    if type(wave_len) == float:
        wave_len = [wave_len]
        
    # Check for dataset extent limitations, fix if values are outside the map
    #   rasie exception if long or lat values are not in the right order
    if aoi[0] <= -180:
        aoi[0] = -179.875
    if aoi[1] >= 180:
        aoi[1] = 179.875
    if aoi[2] <= -90:
        aoi[2] = -82.125
    if aoi[3] >= 90:
        aoi[3] = 89.875
    
    if aoi[0] >= aoi [1]:
        raise Exception("Longitude values made invalid or reversed - FORMAT: [min long, max long, min lat, max lat] <neg vals for west and south>")
    if aoi[2] >= aoi [3]:
        raise Exception("Latitude values made invalid or reversed - FORMAT: [min long, max long, min lat, max lat] <neg vals for west and south>")
    
    # create an output path string
    #   create new folder if none exists, fix periods, space, dash in project name
    out_path = os.path.abspath(out_path)
    project_name_fix = re.sub(r'(\. )|( )|(-)','_',project_name)
    out_path_proj = "%s/%s"%(out_path, project_name_fix)
    
    if os.path.exists(out_path_proj) == False:
        os.mkdir(out_path_proj)
    
    # set datatype based on inputs
    if weekly == True:
        if nrt == False:
            dataset = "dataset-armor-3d-rep-weekly"
        else:
            dataset = "dataset-armor-3d-nrt-weekly"
    else:
        if nrt == False:
            dataset = "dataset-armor-3d-rep-monthly"
        else:
            dataset = "dataset-armor-3d-nrt-monthly"
    
    # query the Copernicus Marine database with input datatype, aoi, and dates
    #   output is a multi-dim xarray
    armor = copernicusmarine.open_dataset(
      dataset_id = dataset,
      minimum_longitude = aoi[0],
      maximum_longitude = aoi[1],
      minimum_latitude = aoi[2],
      maximum_latitude = aoi[3],
      start_datetime = "%sT00:00:00"%(start_date),
      end_datetime = "%sT00:00:00"%(end_date),
      minimum_depth = 0,
      maximum_depth = 0,
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
    print('Processing %i wavelength(s) | '%(len(wave_len)), wave_len)
    
    for wl in wave_len:
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
            print("%0.1f | %i:%i -- %s"%(wl,i+1,ncf_dates.shape[0],
                                   ncf_dates['date'][i].strftime("%Y %b %d")))
            
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
                
                title_str = "Refractive Index @ %0.1f nm\n%s - %s"%(wl,
                                                                    ncf_dates['date'][i].strftime("%Y %b %d"),
                                                                    ncf_dates['date_end'][i].strftime("%Y %b %d"))
                
                plt.xlim(r[0].coords['longitude'].data.min(),r[0].coords['longitude'].data.max())
                plt.ylim(r[0].coords['latitude'].data.min(),r[0].coords['latitude'].data.max())
                
                plt.colorbar()
                plt.title(title_str)
                plt.tight_layout()
                
                out_file = '%s/armor3d_nw%i_%s_%s.png'%(out_path_proj,
                                                        wl,
                                                        project_name_fix,
                                                        date_string)
                
                plt.savefig(out_file,dpi=300)
                plt.close()
                
            if export_tiff == True:
                        
                out_file = '%s/armor3d_nw%i_%s_%s.tif'%(out_path_proj,
                                                        wl,
                                                        project_name_fix,
                                                        date_string)
                r.rio.to_raster(out_file)
    
    print('** OUTPUTS > %s'%out_path_proj)
    
    ref_idx_xarray = armor.drop_vars(['mlotst', 'so', 'to', 'ugo', 'vgo', 'zo'])
    
    if (plot == True) or (export_tiff == True):
        return ref_idx_xarray, out_path_proj
    else:
        return ref_idx_xarray
