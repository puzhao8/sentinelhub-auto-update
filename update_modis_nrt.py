# https://git.earthdata.nasa.gov/projects/LPDUR
# wavelength: https://ladsweb.modaps.eosdis.nasa.gov/missions-and-measurements/viirs/
# viirs ftp: https://e4ftl01.cr.usgs.gov/VIIRS/VNP09GA.001/2021.07.05/
# https://ladsweb.modaps.eosdis.nasa.gov/missions-and-measurements/products/VNP09GA/

# GRID
# (check hHHvVV) https://ladsweb.modaps.eosdis.nasa.gov/search/order/3/MOD09GA--61/2022-08-04..2022-08-06/DB/Tile:H10V3
# hHHvVV GRID: https://modis-land.gsfc.nasa.gov/MODLAND_grid.html

# MODIS
# https://www.earthdatascience.org/courses/use-data-open-source-python/hierarchical-data-formats-hdf/open-MODIS-hdf4-files-python/
# LAADS DATA SOURCE: https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/
# check in APP: https://eo4wildfire.users.earthengine.app/view/wildfire-monitor-eu

# MODIS NRT Products
# https://nrt3.modaps.eosdis.nasa.gov/
# https://search.earthdata.nasa.gov/portal/idn/search/granules?p=C1426416980-LANCEMODIS&pg[0][v]=f&pg[0][qt]=2022-08-30T00%3A00%3A00.000Z%2C2022-08-30T23%3A59%3A59.999Z&pg[0][gsk]=-start_date&q=MOD02QKM_6.1NRT&tl=1661864157.365!3!!&lat=-82.0249693470098&long=-129.234375&zoom=0
# https://www.earthdata.nasa.gov/learn/find-data/near-real-time/viirs
# https://www.earthdata.nasa.gov/learn/find-data/near-real-time/modis

import os
import datetime as dt
import time, subprocess
from datetime import datetime, timedelta

from genericpath import isfile
from pathlib import Path
import shutil
from pandas import date_range

from easydict import EasyDict as edict
import numpy as np
from LaadsDataHandler.laads_client import LaadsClient

import xarray as xr
import rioxarray as rxr
from prettyprinter import pprint

import ee
ee.Initialize()

def download_data_by_hhvv(julian_day, year, hh_list=['10', '11'], vv_list =['03']):
    url_part = f"{collection_id}/{products_id}/{year}/{julian_day}/"
    for hh in hh_list:
        for vv in vv_list:
            print(f"\njulian_day: {julian_day}， h{hh}v{vv}")
            print("-----------------------------------------------------------")

            if products_id in ['VNP09GA_NRT']:
                # VNP09GA_NRT
                command = "wget -e robots=off -m -np -R .html,.tmp -nH --cut-dirs=5 " + \
                    f"\"https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/{url_part}\" \
                        -A \"VNP09GA_NRT.A"+str(year)+f"{julian_day}.h{hh}v{vv}.001.*.h5\" --header \"Authorization: Bearer emhhb3l1dGltOmVtaGhiM2wxZEdsdFFHZHRZV2xzTG1OdmJRPT06MTYyNjQ0MTQyMTphMzhkYTcwMzc5NTg1M2NhY2QzYjY2NTU0ZWFkNzFjMGEwMTljMmJj\" \
                        -P {dataPath}"

            if products_id in ['MOD09GA']:
                # MOD09GA NRT from LANCE
                # MOD09GA.A2022246.h00v08.061.2022247021401.NRT.hdf
                command = "wget -e robots=off -m -np -R .html,.tmp -nH --cut-dirs=5 " + \
                    f"\"https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/{url_part}\" \
                        -A \"{products_id}.A"+str(year)+f"{julian_day}.h{hh}v{vv}.061.*.NRT.hdf\" --header \"Authorization: Bearer emhhb3l1dGltOmVtaGhiM2wxZEdsdFFHZHRZV2xzTG1OdmJRPT06MTYyNjQ0MTQyMTphMzhkYTcwMzc5NTg1M2NhY2QzYjY2NTU0ZWFkNzFjMGEwMTljMmJj\" \
                        -P {dataPath}"

            print(command)
            save_url = f"{dataPath}/{url_part}"
            print(f"\nsaved to: {save_url}")
            # if not os.path.exists(save_url):
            os.system(command)

def convert_hdf_to_geotiff(inDir, outDir, SOURCE):
    fileList = [file for file in os.listdir(inDir) if file.endswith(SOURCE.format) and file.startswith(SOURCE.products_id)] # Search for .h5 files in current directory
    # fileList = [file for file in os.listdir(inDir) if file.endswith('.hdf') and file.startswith('MOD09GA')] # Search for .h5 files in current directory
    pprint(fileList)

    for file in fileList:
        filename = file[:-4]
        print(filename)

        # Open just the bands that you want to process
        desired_bands = SOURCE.BANDS
        modis_bands = rxr.open_rasterio(inDir / f"{filename}.hdf",
                                masked=True,
                                variable=desired_bands
                        ).squeeze()

        outDir.mkdir(exist_ok=True)
        modis_bands.rio.reproject("EPSG:4326").rio.to_raster(outDir / f"{filename}.tif")


def viirs_preprocessing_and_upload(dataPath, FOLDER, SOURCE):
    # CRS optimization and cloud optimization

    if os.path.exists(dataPath / "COG"):
        shutil.rmtree(dataPath / 'COG')

    if not os.path.exists(dataPath / "COG"):
        os.makedirs(dataPath / 'COG')
    
    inDir = dataPath / FOLDER
    print(inDir)

    if True:
        julianDay_list = [folder for folder in os.listdir(str(inDir)) if folder != ".DS_Store"]
        for date in julianDay_list:
            outDir = dataPath / 'COG'
            print(f"outDir: {outDir}")

            if SOURCE.products_id == "VNP09GA":
                # convert_h5_to_cog(inDir=inDir / date, outDir=outDir, SOURCE=SOURCE)
                convert_hdf_to_geotiff(inDir=inDir / date, outDir=outDir, SOURCE=SOURCE)
            
            if SOURCE.products_id == "MOD09GA":
                convert_hdf_to_geotiff(inDir=inDir / date, outDir=outDir, SOURCE=SOURCE)
    
    # upload to Gcloud
    fileList = [file for file in os.listdir(dataPath / "COG") if file[-4:] == ".tif"]
    pprint(fileList)

    dstList = []
    for file in fileList:
        # crs_cloud_optimization(url)
        url = dataPath / "COG" / file
        print(url)
        filename = file[:-4].replace(".", "_")

        # if is not available in gee, then upload 
        if(ee.ImageCollection(f"users/{USER}/{SOURCE.eeImgColName}")
                .filter(ee.Filter.eq("system:index", filename)).size().getInfo() == 0):

            rprjDir = Path(f"{os.path.split(url)[0]}_rprj")
            if not os.path.exists(rprjDir): os.makedirs(rprjDir)

            dst_url = rprjDir / f"{filename}.tif"
            tmp_url = rprjDir / f"{filename}_tmp.tif"

            # os.system(f"gdalwarp {url} {tmp_url} -t_srs EPSG:4326 -r bilinear -ts 1200 1200 -dstnodata 0")
            # os.system(f"gdal_translate {tmp_url} {dst_url} -co TILED=YES -co COPY_SRC_OVERVIEWS=YES -co COMPRESS=LZW")

            os.system(f"gdal_translate {url} {dst_url} -co TILED=YES -co COPY_SRC_OVERVIEWS=YES -co COMPRESS=LZW")
            
            if isfile(tmp_url): os.remove(tmp_url)
            
            os.system(f"gsutil -m cp -r {dst_url} {gs_dir}/")
            os.system(f"earthengine upload image --force --asset_id={VIIRS_NRT_ImgCol}/{filename} {gs_dir}/{filename}.tif")

            dstList.append(filename)

        else:
            print(f"{filename}: [already in GEE!]")

    return dstList


def update_modis_in_gee_for(julian_day):
    # Download from Lance

    if True:
        # North America
        if not os.path.exists(tmpPath / str(julian_day)):
            os.mkdir(tmpPath / str(julian_day))
        download_data_by_hhvv(julian_day, year, hh_list=hh_list_na, vv_list =vv_list_na)

        # Europe
        download_data_by_hhvv(julian_day, year, hh_list=hh_list_eu, vv_list =vv_list_eu)

    if False: # Download or Not
        date_ndays = (dt.datetime.strptime(date, '%Y-%m-%d') - dt.datetime.strptime(date[:4] + '-01-01', '%Y-%m-%d')).days + 1
        julian_today=date_ndays
        print(f"julian_today: {julian_today}\n")

        laads_client = LaadsClient()
        laads_client.query_filelist_with_date_range_and_area_of_interest(date, products_id=[products_id], collection_id=collection_id, data_path=f'{dataPath}/{FOLDER}', julian_day=str(date_ndays))
        laads_client.download_files_to_local_based_on_filelist(date, products_id=[products_id], collection_id=collection_id, data_path=f'{dataPath}/{FOLDER}', julian_day=str(date_ndays))

    fileList = viirs_preprocessing_and_upload(dataPath, FOLDER, SOURCE)
    pprint(fileList)
    
    # fileList = [
    #     "VNP09GA_NRT_A2021200_h10v03_001",
    #     "VNP09GA_NRT_A2021200_h11v03_001",
    # ]

    ''' set time_start property after being uploaded '''
    time.sleep(60*10) # wait 10-min for all data uploading finished. 
    response = subprocess.getstatusoutput(f"earthengine ls users/{USER}/{eeImgColName}")
    asset_list = response[1].replace("projects/earthengine-legacy/assets/", "").split("\n")

    # delete older data if julian_day < julian_today - 5)
    lance_date = dt.date.today() - dt.date(year, 1, 1)
    julian_today = lance_date.days + 1

    for asset_id in asset_list:
        filename = os.path.split(asset_id)[-1]
        julian_day = eval(filename.split("_")[1][-3:]) # may need to be changed for different products
        if julian_day < julian_today - 5: # if julian date is smaller than (julian_today - 5)
            os.system(f"earthengine rm {asset_id}")
            print(f"{filename} {date} [deleted!]")

    # set time_start property after being uploaded
    for filename in fileList:
        asset_id = f"users/{USER}/{eeImgColName}/{filename}"

        julian_day = eval(filename.split("_")[1][5:]) 
        standard_date = datetime(year, 1, 1) + timedelta(days=julian_day-1)
        standard_date = standard_date.strftime("%Y-%m-%d")

        if asset_id in asset_list:
            print(filename, standard_date)
            os.system(f'earthengine asset set --time_start {standard_date} {asset_id}')


if __name__ == "__main__":
    # # 1km vs. 500m --> "M5", "M7", "M10" vs. "I1", "I2", "I3"
    # # 500m: "M3",     "M4",  "I1",  "I2",   "I3",    "M11",  "QF2"
    # # 1km:  "M3",     "M4",  "M5",  "M7",   "M10",    "M11",  "QF2"
    # # "Blue",         "Green", "Red", "NIR", "SWIR1", "SWIR2", "BitMask"
    # BANDS = ["M3",     "M4",  "M5",  "M7",   "M10",    "M11",  "QF2"]

    # North America
    hh_list_na = ['08', '09', '10', '11', '12', '13', '14']
    vv_list_na = ['02', '03', '04', '05']

    # European Union
    hh_list_eu = ['17', '18', '19', '20', '21', '22', '23']
    vv_list_eu = ['02', '03', '04', '05']

    ''' Configuration '''
    CFG = {
        'VNP09GA': {
            "products_id": "VNP09GA",
            "collection_id": '5000',
            "eeImgColName": "VIIRS_NRT",
            "format": '.h5',
            "BANDS": ["M3", "M4", "M5", "M7", "M10", "M11", "QF2"]
        },

        'VNP09_NRT': {
            "products_id": "VNP09_NRT",
            "collection_id": '5000',
            "eeImgColName": "VIIRS_NRT",
            "format": '.hdf',
            "BANDS": [
                "375m Surface Reflectance Band I1",
                "375m Surface Reflectance Band I2",
                "375m Surface Reflectance Band I1"
            ]
        },

        'MOD09GA': {
            "products_id": "MOD09GA",
            "collection_id": '61',
            "eeImgColName": "MODIS_NRT",
            "format": '.hdf',
            "BANDS": [
                "sur_refl_b01_1",
                "sur_refl_b02_1", 
                # "sur_refl_b03_1",
                # "sur_refl_b04_1", 
                "sur_refl_b07_1"
            ]
        },

        'MOD02HKM': {
            "products_id": "MOD02HKM",
            "collection_id": '61',
            "eeImgColName": "MODIS_NRT",
            "format": '.hdf',
            "BANDS": ["sur_refl_b01_1", "sur_refl_b02_1", "sur_refl_b03_1", "sur_refl_b04_1", "sur_refl_b07_1"]
        },
    }

    # Configuration 
    USER = "omegazhangpzh"
    SOURCE = edict(CFG['MOD09GA'])
    year = 2022

    products_id = SOURCE.products_id
    collection_id = SOURCE.collection_id
    eeImgColName = SOURCE.eeImgColName
    BANDS=SOURCE.BANDS
    
    # local path
    # workspace = Path(os.getcwd())
    workspace = Path("C:\eo4wildfire")
    dataPath = workspace / eeImgColName
    FOLDER = f"{collection_id}/{products_id}/{year}"

    # cloud path
    gs_dir = f"gs://sar4wildfire/{eeImgColName}" # GCP
    VIIRS_NRT_ImgCol = f"users/{USER}/{eeImgColName}" # GEE

    # remove downloaded data in the last run
    # if True and os.path.exists(dataPath):
    try: 
        shutil.rmtree(f"{str(dataPath)}/")
        os.rmdir(dataPath)
    except: 
        print("---------- failed to delete historical data !!! ---------------")

    tmpPath = dataPath / FOLDER
    if not os.path.exists(tmpPath): os.makedirs(tmpPath)


    today = dt.date.today()
    day_start = today + timedelta(days=-1)

    while (True):
        current_time =  datetime.now().strftime("%H:%M:%S")
        print(current_time)

        if current_time[:2] == "09": # update at 04:00 AM
            
            for date_time in date_range(day_start, today):
                date = str(date_time)[:10]

                lance_date = dt.datetime.strptime(date, "%Y-%m-%d").date() - dt.date(year, 1, 1)
                julian_day = lance_date.days + 1

                print("----------------------------------------------")
                print(date, julian_day)
                update_modis_in_gee_for(julian_day)

        else:
            time.sleep(60*60) # sleep 1h





