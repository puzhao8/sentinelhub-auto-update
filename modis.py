# %%

from ast import In
import os, gdal
from pathlib import Path

import earthpy as ep
import xarray as xr
import rioxarray as rxr

# # MODIS
# rootDir = Path("C:\\eo4wildfire\\data\\MODIS_NRT")
# inDir = rootDir / "61/MOD09GA/2022/214"
# outDir = rootDir / "COG_test"

# filename = "MOD09GA.A2022214.h17v04.061.2022216033241"

# VIIRS
rootDir = Path("C:\\eo4wildfire")
inDir = rootDir
outDir = rootDir / "COG_test"

url_ = "G:\PyProjects\sentinelhub-auto-update\outputs\MOD02HKM.A2022243.0000.061.2022243005534.NRT.hdf"
url = "G:\PyProjects\sentinelhub-auto-update\outputs\MOD09GA.A2022243.h03v09.061.2022245050724.hdf"
# url = "G:\PyProjects\sentinelhub-auto-update\outputs\VNP09_NRT.A2022243.0042.001.2022243040102.hdf"
filename = os.path.split(url)[-1][:-4]

print(filename)
# viirs bands https://lpdaac.usgs.gov/data/get-started-data/collection-overview/missions/s-npp-nasa-viirs-overview/
viirs_bands = [ 
    # "//HDFEOS/GRIDS/VNP_Grid_500m_2D/Data_Fields/SurfReflect_I2_1"
                # "SurfReflect_M2_1", # Blue
                # "SurfReflect_M3_1", # green
                # "SurfReflect_M4_1", # red
                # "SurfReflect_I2_1", # NIR: M5 or I2
                # "SurfReflect_I3_1", # SWIR1: M10 or I3
                # "SurfReflect_M11_1", # SWIR2
                # # "SurfReflect_QF2_1"
                
                "375m Surface Reflectance Band I1",
                "375m Surface Reflectance Band I2",
                "375m Surface Reflectance Band I3"  
            ]

# Open just the bands that you want to process
modis_bands = ["sur_refl_b01_1",
                "sur_refl_b02_1",
                # "sur_refl_b03_1",
                # "sur_refl_b04_1",
                "sur_refl_b07_1",
            ]

desired_bands = viirs_bands
# Notice that here, you get a single xarray object with just the bands that
# you want to work with
# print(str(inDir / f"{filename}.h5"))

# %%
url_ = "G:\PyProjects\sentinelhub-auto-update\outputs\MOD02HKM.A2022246.1015.061.2022246111842.NRT.hdf"
url_MOD021KM = "G:\PyProjects\sentinelhub-auto-update\outputs\MOD021KM.A2022247.0025.061.2022247013902.NRT.hdf"
MOD02HKM = rxr.open_rasterio(url_,
                        masked=False,
                        variable=[
                            "EV_500_RefSB",
                            "EV_250_Aggr500_RefSB"]
                )#.squeeze()

# %%
MOD02HKM_ = MOD02HKM['EV_250_Aggr500_RefSB'][:1,].to_dataset()
MOD02HKM_ = MOD02HKM_.update({
    "sur_refl_b01": MOD02HKM['EV_250_Aggr500_RefSB'][:1,],
    "sur_refl_b02": MOD02HKM['EV_250_Aggr500_RefSB'][1:2,],
    # "sur_refl_b03": MOD02HKM['EV_500_RefSB'][0],
    # "sur_refl_b04": MOD02HKM['EV_500_RefSB'][1],
    # "sur_refl_b05": MOD02HKM['EV_500_RefSB'][2],
    # "sur_refl_b06": MOD02HKM['EV_500_RefSB'][3],
    "sur_refl_b07": MOD02HKM['EV_500_RefSB'][4:5],
    })
MOD02HKM_ = MOD02HKM_.drop(labels=['EV_250_Aggr500_RefSB'])
# MOD02HKM_ = MOD02HKM_.drop(labels='band')
MOD02HKM_ = MOD02HKM_.assign_attrs(MOD02HKM.attrs).squeeze()

# %%
filename = "V1_MOD02HKM"
outDir.mkdir(exist_ok=True)
MOD02HKM_.rio \
    .write_crs("EPSG:4326").rio \
            .to_raster(outDir / f"{filename}.tif")

# .reproject("EPSG:4326") \
# .write_crs("EPSG:4326").rio \
src_url = outDir / f"{filename}.tif"
dst_url = outDir / f"COG_{filename}.tif"
os.system(f"gdal_translate {src_url} {dst_url} -co TILED=YES -co COPY_SRC_OVERVIEWS=YES -co COMPRESS=LZW")


# %% MOD09GA
url = "G:\PyProjects\sentinelhub-auto-update\outputs\MOD09GA.A2022243.h03v09.061.2022245050724.hdf"
MOD09GA = rxr.open_rasterio(url,
                        masked=False,
                        variable=["sur_refl_b01_1",
                                "sur_refl_b02_1",
                                "sur_refl_b07_1",
                            ]
                ).squeeze()

filename = "MOD09GA"
outDir.mkdir(exist_ok=True)
MOD09GA.rio.reproject("EPSG:4326").rio.to_raster(outDir / f"{filename}.tif")

src_url = outDir / f"{filename}.tif"
dst_url = outDir / f"COG_{filename}.tif"
os.system(f"gdal_translate {src_url} {dst_url} -co TILED=YES -co COPY_SRC_OVERVIEWS=YES -co COMPRESS=LZW")

# %%

# https://gis.stackexchange.com/questions/360777/convert-modis-mod021km-hdf-file-to-geotif-using-specific-band
folder = "G:\PyProjects\sentinelhub-auto-update\outputs"

hdf_ds = gdal.Open(url_MOD021KM, gdal.GA_ReadOnly)
subdatasets = hdf_ds.GetSubDatasets()

# for i in range(0, len(subdatasets)+1):
for i in range(0, 1):
    subdataset_name = subdatasets[i][0]
    band_ds = gdal.Open(subdataset_name, gdal.GA_ReadOnly)
    print(band_ds.GetProjection())

    band_path = os.path.join(folder, 'MOD021KM_band{0}.tif'.format(i))
    if band_ds.RasterCount > 1:
        for j in range(1,band_ds.RasterCount + 1):
            band = band_ds.GetRasterBand(j)
            band_array = band.ReadAsArray()

    else:
        band_array = band_ds.ReadAsArray()
    out_ds = gdal.GetDriverByName('GTiff').Create(band_path,
                                                  band_ds.RasterXSize,
                                                  band_ds.RasterYSize,
                                                  1,
                                                  gdal.GDT_Int16,
                                                  ['COMPRESS=LZW', 'TILED=YES'])
    
    out_ds.SetGeoTransform(band_ds.GetGeoTransform())
    out_ds.SetProjection(band_ds.GetProjection())
    out_ds.GetRasterBand(1).WriteArray(band_array)
    out_ds.GetRasterBand(1).SetNoDataValue(-32768)

    

out_ds = None  #close dataset to write to disc

# %%

url_MOD021KM = "G:\PyProjects\sentinelhub-auto-update\outputs\MOD021KM.A2022247.0025.061.2022247013902.NRT.hdf"
MOD021KM = rxr.open_rasterio(url_MOD021KM,
                        masked=False,
                        variable=[
                            "EV_1KM_RefSB",
                            # "EV_250_Aggr500_RefSB"
                        ]
                )#.squeeze()

# %%
from satpy import Scene, MultiScene
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt



# print(modis_pre_bands)
# %%
# gdal_translate -of GTiff 'HDF4_EOS:EOS_GRID:"MOD09GA.A2022213.h08v03.061.2022215042622.hdf":MODIS_Grid_500m_2D:sur_refl_b03_1' 'SR1.tiff'