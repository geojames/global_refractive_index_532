# Welcome to the Global Refractive Index Data Page

This folder contains the raster data files for the refractive index of water at 532 nanometers (green lasers) for use in correcting airborne and spaceborne bathymetric lidar datasets.

The refractive index is notated as $n$ and the refractive index od water as $n_w$, so we adopt a convension of $n_w (532)$ for the refractive index of water at 532 nm.

The raster data have a resolution of 0.25° and are projected in Lat/Long (WGS84, EPSG:4326)

**Each full year (2016 - 2023) contains 14 raster bands:**
- Bands 1-12 = Months of the year (1=Jan, 2=Feb, ..., 12 = Dec)
- Band 13 = Annual Average

**Each partial year (2024):**
- Bands 1-x = Months of the year (1=Jan, 2=Feb, ..., 12 = Dec)

#### File nameing convension:
> armor3d_nw532_[year]\_monthly\_[processing_level].tif
- armor3d = Source dataset [ARMOR3D L4](https://data.marine.copernicus.eu/product/MULTIOBS_GLO_PHY_TSUV_3D_MYNRT_015_012/description)
  - MULTIOBS\_GLO\_PHY\_TSUV\_3D\_MYNRT\_015\_012 
- nw532 = refractive index of water at 532 nm
- year = year covered by the file
- monthly = band temporal frequency (1 per month)
- processing level = from ARMOR3D L4: REP
  - NRT: Near-Real Time, ~1 month lag before present
  - REP: Reprocessed, 12 to 24 months lag before present - "The REP datasets benefit from the highest quality ocean observations input."
  
