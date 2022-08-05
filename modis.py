
# %%

from ast import In
import os, gdal
from pathlib import Path

import earthpy as ep
import xarray as xr
import rioxarray as rxr

url = Path('\\61\\MOD09GA\\2022\\213\\MOD09GA.A2022213.h08v03.061.2022215042622.hdf')



def convert_MODIS_hdf_to_geotiff(inDir, outDir):
    # fileList = [file for file in os.listdir(inDir) if file.endswith(SOURCE.format) and file.startswith(SOURCE.products_id)] # Search for .h5 files in current directory
    fileList = [file for file in os.listdir(inDir) if file.endswith('.hdf') and file.startswith('MOD09GA')] # Search for .h5 files in current directory
    for file in fileList[:2]:
        filename = file[:-4]
        print(filename)

        # Open just the bands that you want to process
        desired_bands = ["sur_refl_b01_1",
                        "sur_refl_b02_1",
                        "sur_refl_b03_1",
                        "sur_refl_b04_1",
                        "sur_refl_b07_1",
                        ]
        # Notice that here, you get a single xarray object with just the bands that
        # you want to work with
        modis_bands = rxr.open_rasterio(inDir / f"{filename}.hdf",
                                masked=True,
                                variable=desired_bands
                        ).squeeze()

        outDir.mkdir(exist_ok=True)
        modis_bands.rio.to_raster(outDir / f"{filename}.tif")



if __name__ == "__main__":

    rootDir = Path("C:\\eo4wildfire\\data\\MODIS_NRT")
    inDir = rootDir / "61/MOD09GA/2022/213"
    outDir = rootDir / "COG"

    convert_MODIS_hdf_to_geotiff(inDir, outDir)


# print(modis_pre_bands)
# %%
# gdal_translate -of GTiff 'HDF4_EOS:EOS_GRID:"MOD09GA.A2022213.h08v03.061.2022215042622.hdf":MODIS_Grid_500m_2D:sur_refl_b03_1' 'SR1.tiff'