
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
filename = "VNP09GA.A2022207.h08v03.001.2022209142935"



print(filename)
# viirs bands https://lpdaac.usgs.gov/data/get-started-data/collection-overview/missions/s-npp-nasa-viirs-overview/
viirs_bands = [ 
    "//HDFEOS/GRIDS/VNP_Grid_500m_2D/Data_Fields/SurfReflect_I2_1"
                # "SurfReflect_M2_1", # Blue
                # "SurfReflect_M3_1", # green
                # "SurfReflect_M4_1", # red
                # "SurfReflect_I2_1", # NIR: M5 or I2
                # "SurfReflect_I3_1", # SWIR1: M10 or I3
                # "SurfReflect_M11_1", # SWIR2
                # # "SurfReflect_QF2_1"
                ]

# Open just the bands that you want to process
modis_bands = ["sur_refl_b01_1",
                "sur_refl_b02_1",
                "sur_refl_b03_1",
                "sur_refl_b04_1",
                "sur_refl_b07_1",
                ]

desired_bands = viirs_bands
# Notice that here, you get a single xarray object with just the bands that
# you want to work with
print(str(inDir / f"{filename}.h5"))
modis_bands = rxr.open_rasterio(inDir / f"{filename}.h5",
                        masked=True,
                        variable=desired_bands
                ).squeeze()

outDir.mkdir(exist_ok=True)
modis_bands.rio \
            .write_crs("EPSG:4326").rio \
            .to_raster(outDir / f"{filename}.tif")
            

src_url = outDir / f"{filename}.tif"
dst_url = outDir / f"COG_{filename}.tif"
os.system(f"gdal_translate {src_url} {dst_url} -co TILED=YES -co COPY_SRC_OVERVIEWS=YES -co COMPRESS=LZW")
 

# if __name__ == "__main__":

#     rootDir = Path("C:\\eo4wildfire\\data\\MODIS_NRT")
#     inDir = rootDir / "61/MOD09GA/2022/213"
#     outDir = rootDir / "COG"

#     convert_MODIS_hdf_to_geotiff(inDir, outDir)


# print(modis_pre_bands)
# %%
# gdal_translate -of GTiff 'HDF4_EOS:EOS_GRID:"MOD09GA.A2022213.h08v03.061.2022215042622.hdf":MODIS_Grid_500m_2D:sur_refl_b03_1' 'SR1.tiff'