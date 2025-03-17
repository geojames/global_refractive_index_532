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
__url__ = "https://github.com/geojames/global_refractive_index_532"

"""
Name:           cop_dynamic_V2_func_test.py
Compatibility:  Python 3.12
Description:    function calling example for dynamic date/AOI refractive index processing
Requires:       

Dev ToDo:       

AUTHOR:         James T. Dietrich
ORGANIZATION:   Washington State Department of Ecology
Contact:        geojamesdietrich@gmail.com
Copyright:      (c) James Dietrich 2025

Licence:        MIT
"""

# IMPORTS
from RefIdx_COP_dynamicAOI_v2 import cop_ref_idx



#wl = 532.0
wavelength = [470,532,630]
project_name = 'carrib'
out_path = 'E:/RefractiveIndex_copy/dynam_ri'

# Area of interest
#   [min longitude, max longitude, min latitude, max latitude] (negaitves for west and south)
aoi = [-99,-58, 7,33]

# Date range: "yyyy-mm-dd"
start_date = "2025-1-1"
end_date = "2025-2-1"

# with outputs - returns xarray and output_path
ri_xarr,op = cop_ref_idx(start_date, end_date, aoi, wavelength, 
                         "carrib_multi", out_path, plot=True)

#no outputs - return xarray only
ri_xarr = cop_ref_idx(start_date, end_date, aoi, wavelength,
                      "carrib_multi", out_path, plot=False, export_tiff=False)