# https://git.earthdata.nasa.gov/projects/LPDUR
# wavelength: https://ladsweb.modaps.eosdis.nasa.gov/missions-and-measurements/viirs/
# viirs ftp: https://e4ftl01.cr.usgs.gov/VIIRS/VNP09GA.001/2021.07.05/
# https://ladsweb.modaps.eosdis.nasa.gov/missions-and-measurements/products/VNP09GA/
# hHHvVV GRID: https://modis-land.gsfc.nasa.gov/MODLAND_grid.html
# DoY (Day of Year): https://asd.gsfc.nasa.gov/Craig.Markwardt/doy2021.html

from itertools import product
import os
import datetime as dt
from genericpath import isfile
from glob import glob
import numbers
from pathlib import Path
import shutil
import ee
# ee.Initialize()

# from ee import data
# from numpy.char import startswith

import h5py
import numpy as np
from osgeo import gdal, gdal_array

from LaadsDataHandler.laads_client import LaadsClient


def get_geoInfo_and_projection(f):
    
    fileMetadata = f['HDFEOS INFORMATION']['StructMetadata.0'][()].split()   # Read file metadata
    fileMetadata = [m.decode('utf-8') for m in fileMetadata]                 # Clean up file metadata
    # fileMetadata[0:33]                                                       # Print a subset of the entire file metadata record

    ulc = [i for i in fileMetadata if 'UpperLeftPointMtrs' in i][0]    # Search file metadata for the upper left corner of the file
    ulcLon = float(ulc.split('=(')[-1].replace(')', '').split(',')[0]) # Parse metadata string for upper left corner lon value
    ulcLat = float(ulc.split('=(')[-1].replace(')', '').split(',')[1]) # Parse metadata string for upper left corner lat value

    yRes, xRes = -926.6254330555555,  926.6254330555555 # Define the x and y resolution
    # yRes, xRes = -500,  500 # Define the x and y resolution

    '''Currently, VIIRS HDF-EOS5 files do not contain information regarding the spatial resolution of the dataset within.'''
    # if nRow == 1200:                      # VIIRS A1 - 1km or 1000m
    #     yRes = -926.6254330555555    
    #     xRes = 926.6254330555555
    # elif nRow == 2400:                    # VIIRS H1 - 500m
    #     yRes = -463.31271652777775
    #     xRes = 463.31271652777775
    # elif nRow == 3600 and nCol == 7200:    # VIIRS CMG
    #     yRes = -0.05
    #     xRes = 0.05
    #     # Re-set upper left dims for CMG product                
    #     ulcLon = -180.00
    #     ulcLat = 90.00

    geoInfo = (ulcLon, xRes, 0, ulcLat, 0, yRes)        # Define geotransform parameters

    prj = 'PROJCS["Sphere_Sinusoidal",\
        GEOGCS["GCS_Sphere",\
            DATUM["Not_specified_based_on_Authalic_Sphere",\
                SPHEROID["Sphere",6371000,0]],\
            PRIMEM["Greenwich",0],\
            UNIT["Degree",0.017453292519943295]],\
        PROJECTION["Sinusoidal"],\
        PARAMETER["False_Easting",0],\
        PARAMETER["False_Northing",0],\
        PARAMETER["Central_Meridian",0],\
        UNIT["Meter",1],\
        AUTHORITY["EPSG","53008"]]'

    projInfo = {'SINU':'PROJCS["unnamed",GEOGCS["Unknown datum based upon the custom spheroid", DATUM["Not specified (based on custom spheroid)", SPHEROID["Custom spheroid",6371007.181,0]],PRIMEM["Greenwich",0], UNIT["degree",0.0174532925199433]], PROJECTION["Sinusoidal"],PARAMETER["longitude_of_center",0],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["Meter",1]]',
            'GEO':'GEOGCS["Unknown datum based upon the Clarke 1866 ellipsoid", DATUM["Not specified (based on Clarke 1866 spheroid)", SPHEROID["Clarke 1866",6378206.4,294.9786982139006]], PRIMEM["Greenwich",0], UNIT["degree",0.0174532925199433]]'}

    return geoInfo, prj

def convert_h5_to_cog(inDir, outDir, BANDS=["M3", "M4", "M5", "M7", "M10", "M11", "QF2"], band_scale_flag=False):
    # os.chdir(inDir)   
    # VNP = Path(os.path.split(inDir)[0])                                                      # Change to working directory
    
    # outDir = Path(os.path.split(VNP)[0]) / 'COG' # Set output directory
    
    print("BADNS: ", BANDS)
    if not os.path.exists(outDir): os.makedirs(outDir)                      # Create output directory


    fileList = [file for file in os.listdir(inDir) if file.endswith('.h5') and file.startswith('VNP09GA')] # Search for .h5 files in current directory
    
    print("------------------------------------")
    for f in fileList: print(f)       
    print("------------------------------------")                                                                # Print files in list

    date = [] # Create empty list to store dates of each file
    i = 0     # Set up iterator for automation in cell block below

    for t in fileList:
        print(f"\n----> {t} <----")

        yeardoy = t.split('.')[1][1:]                                                                  # Split name,retrieve ob date
        outName = t.rsplit('.', 1)[0]                                                                  # Keep filename for outname
        date1 = dt.datetime.strptime(yeardoy,'%Y%j').strftime('%m/%d/%Y')                              # Convert date
        date.append(date1)                                                                             # Append to list of dates
        f = h5py.File(os.path.normpath(Path(inDir) / t), "r")                                                             # Read in VIIRS HDF-EOS5 file
        
        # geoInfo and Projection
        geoInfo, prj = get_geoInfo_and_projection(f)

        h5_objs = []                                                                                   # Create empty list
        f.visit(h5_objs.append)                                                                        # Retrieve obj append to list
        
        # Search for SDS with 1km or 500m grid
        grids = list(f['HDFEOS']['GRIDS']) # List contents of GRIDS directory                                      # Clean up file metadata
    

        allSDS = [o for grid in grids for o in h5_objs if isinstance(f[o],h5py.Dataset) and grid in o] # Create list of SDS in file
        
        r = f[[a for a in allSDS if 'M5' in a][0]] 
        scaleFactor = r.attrs['Scale'][0]    # Set scale factor to a variable
        fillValue = r.attrs['_FillValue'][0] # Set fill value to a variable  

        print(f"scaleFactor: {scaleFactor}")

        band_dict = {}
        for band_name in BANDS:
            # print(band_name)
            band = f[[a for a in allSDS if band_name in a][0]][()]   
                                                             # Open SDS M5 = Red
            if band_scale_flag and ('QF' not in band_name):
                band = band * scaleFactor

            band_dict[band_name] = band                                                   

        data = np.dstack(tuple(band_dict.values()))
        print(data.shape)

        data[data == fillValue * scaleFactor] = 0 # Set fill value equal to nan
        
        # qf = f[[a for a in allSDS if 'QF5' in a][0]][()]                                               # Import QF5 SDS
        # qf2 = f[[a for a in allSDS if 'QF2' in a][0]][()]                                              # Import QF2 SDS                                                                  # Append to list
        
        params = {
                'all':{'data':data, 'band': 'all'}
            }
        for p in params:
            try: 
                data = params[p]['data']                                                               # Define array to be exported
                data[data.mask == True] = fillValue                                                    # Masked values = fill value
            except: AttributeError

            # outputName = os.path.normpath('{}{}.tif'.format(outDir, outName))    # Generate output filename
            outputName = str(outDir / f"{outName}.tif")   # Generate output filename

            nRow, nCol = data.shape[0], data.shape[1]                                                  # Define row/col from array
            dataType = gdal_array.NumericTypeCodeToGDALTypeCode(data.dtype)                            # Define output data type
            driver = gdal.GetDriverByName('GTiff')                                                     # Select GDAL GeoTIFF driver
                                                                        # Diff for exporting RGBs
            data = params[p]['data']                                                               # Define the array to export
            dataType = gdal_array.NumericTypeCodeToGDALTypeCode(data.dtype)                        # Define output data type
            options = [
                        # 'PHOTOMETRIC=RGB', 
                        # 'PROFILE=GeoTIFF'
                        "TILED=YES",
                        "COMPRESS=LZW",
                        "INTERLEAVE=BAND"]                                       # Set options to RGB TIFF
            outFile = driver.Create(outputName, nCol, nRow, len(BANDS), dataType, options=options)          # Specify parameters of GTIFF
            
            for idx, band in enumerate(BANDS):  
                print(idx, band)                                                       # loop through each band (3)
                rb = outFile.GetRasterBand(idx+1)
                rb.WriteArray(data[..., idx])                                  # Write to output bands 1-3
                # rb.SetNoDataValue(1.1)                                       # Set fill val for each band
                # rb.SetDescription(band)
                rb = None
                
            outFile.SetGeoTransform(geoInfo)                                                           # Set Geotransform
            outFile.SetProjection(prj)                                                                 # Set projection
            outFile = None                                                                             # Close file

        print('Processed file: {} of {}'.format(i+1, len(fileList)))                                    # Print the progress
        i += 1

def crs_cloud_optimization(url):
    input_raster = gdal.Open(url)
    raster_name = os.path.split(url)[-1][:-4].replace(".", "_")

    input_dir = Path(os.path.split(url)[0])
    output_dir = input_dir / "reprojected" 
    if not os.path.exists(output_dir): os.makedirs(output_dir)

    output_url = output_dir / f"{raster_name}.tif" 

    print(output_url)

    gdal.WarpOptions(dstSRS='EPSG:4326')
    warp = gdal.Warp(output_url, input_raster, dstNodata=0)
    warp.GetRasterBand(1).SetNoDataValue(0)
    warp = None

    # cloud optimized tif
    dst_url = input_dir / "COG" / raster_name
    os.system(f"gdal_translate {output_url} {dst_url} -co TILED=YES -co COPY_SRC_OVERVIEWS=YES -co COMPRESS=LZW")



def download_viirs_on(julian_day, year, hh_list=['10', '11'], vv_list =['03']):
    for hh in hh_list:
        for vv in vv_list:

            print(f"\njulian_day: {julian_day}， h{hh}v{vv}")
            print("-----------------------------------------------------------")

            url_part = f"5000/{PRODUCT}/2021/{julian_day}/{PRODUCT}.A2021{julian_day}.h{hh}v{vv}.001.h5"
            command = "c:/wget/wget.exe -e robots=off -m -np -R .html,.tmp -nH --cut-dirs=5 " + \
                f"\"https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/\"{url_part} \
                    --header \"Authorization: Bearer emhhb3l1dGltOmVtaGhiM2wxZEdsdFFHZHRZV2xzTG1OdmJRPT06MTYyNjQ0MTQyMTphMzhkYTcwMzc5NTg1M2NhY2QzYjY2NTU0ZWFkNzFjMGEwMTljMmJj\" \
                    -P {dataPath}"

            print(command)
            save_url = f"{dataPath}/{url_part}"
            print(save_url)
            if not os.path.exists(save_url):
                os.system(command)


def viirs_preprocessing_and_upload(dataPath):
    # CRS optimization and cloud optimization

    if os.path.exists(dataPath / "COG"):
        shutil.rmtree(dataPath / 'COG')

    if not os.path.exists(dataPath / "COG"):
        os.makedirs(dataPath / 'COG')
    

    inDir = dataPath / "5000" / "VNP09_NRT" / "2022"
    print(inDir)

    julianDay_list = [folder for folder in os.listdir(str(inDir)) if folder != ".DS_Store"]
    for date in julianDay_list:
        outDir = dataPath / 'COG'
        print(f"outDir: {outDir}")
        convert_h5_to_cog(inDir=inDir / date, outDir=outDir, BANDS=["M3", "M4", "M5", "M7", "M10", "M11", "QF2"])
        
    # upload to Gcloud
    fileList = [file for file in os.listdir(dataPath / "COG") if file[-4:] == ".tif"]
    # pprint(fileList)

    dstList = []
    for file in fileList:
        # crs_cloud_optimization(url)
        url = dataPath / "COG" / file
        print(url)
        filename = file[:-4].replace(".", "_")

        # if is not available in gee, then upload 
        if(ee.ImageCollection("users/omegazhangpzh/VIIRS_NRT")
                .filter(ee.Filter.eq("system:index", filename)).size().getInfo() == 0):

            rprjDir = Path(f"{os.path.split(url)[0]}_rprj")
            if not os.path.exists(rprjDir): os.makedirs(rprjDir)

            dst_url = rprjDir / f"{filename}.tif"
            tmp_url = rprjDir / f"{filename}_tmp.tif"
            os.system(f"gdalwarp {url} {tmp_url} -t_srs EPSG:4326 -r bilinear -ts 1200 1200 -dstnodata 0")
            os.system(f"gdal_translate {tmp_url} {dst_url} -co TILED=YES -co COPY_SRC_OVERVIEWS=YES -co COMPRESS=LZW")
            
            if isfile(tmp_url): os.remove(tmp_url)
            
            os.system(f"gsutil -m cp -r {dst_url} {gs_dir}/")
            os.system(f"earthengine upload image --force --asset_id={VIIRS_NRT_ImgCol}/{filename} {gs_dir}/{filename}.tif")

            dstList.append(filename)

        else:
            print(f"{filename}: [already in GEE!]")

    return dstList


from prettyprinter import pprint

if __name__ == "__main__":
    # # 1km vs. 500m --> "M5", "M7", "M10" vs. "I1", "I2", "I3"
    # # 500m: "M3",     "M4",  "I1",  "I2",   "I3",    "M11",  "QF2"
    # # 1km:  "M3",     "M4",  "M5",  "M7",   "M10",    "M11",  "QF2"
    # # "Blue",         "Green", "Red", "NIR", "SWIR1", "SWIR2", "BitMask"
    # BANDS = ["M3",     "M4",  "M5",  "M7",   "M10",    "M11",  "QF2"]
    hh_list_na = ['08', '09', '10', '11', '12', '13']
    vv_list_na = ['02', '03', '04', '05']

    hh_list_eu = ['08', '09', '10', '11', '12', '13']
    vv_list_eu = ['02', '03', '04', '05']

    # workspace = Path(os.getcwd())
    eeImgColName = "VIIRS_NRT"
    products_id = "VNP09_NRT"
    date = '2022-08-31'

    year=2022
    workspace = Path("data")
    dataPath = workspace / 'data' / eeImgColName
    download = True
    if download:
        if os.path.exists(dataPath): shutil.rmtree(f"{str(dataPath)}/")

    tmpPath = dataPath / f"5000/{products_id}" / str(year) # VNP09GA_NRT
    if not os.path.exists(tmpPath): os.makedirs(tmpPath)

    gs_dir = f"gs://ai4wildfire/{eeImgColName}"
    VIIRS_NRT_ImgCol = f"users/eo4wildfire/{eeImgColName}"

    # Download from Lance
    # lance_date = datetime.date.today() - datetime.date(year, 1, 3)
    # julian_today = lance_date.days

    # if download:
    #     for julian_day in range(julian_today, julian_today+1):
    #         # North America
    #         if not os.path.exists(tmpPath / str(julian_day)):
    #             os.mkdir(tmpPath / str(julian_day))
    #         download_viirs_on(julian_day, year, hh_list=hh_list_na, vv_list =vv_list_na)
    #         # Europe
    #         download_viirs_on(julian_day, year, hh_list=hh_list_eu, vv_list =vv_list_eu)
    
    date_ndays = (dt.datetime.strptime(date, '%Y-%m-%d') - dt.datetime.strptime(date[:4] + '-01-01', '%Y-%m-%d')).days + 1
    julian_today=date_ndays
    print(f"julian_today: {julian_today}")
    laads_client = LaadsClient()
    laads_client.query_filelist_with_date_range_and_area_of_interest(date, products_id=[products_id], collection_id='5000', data_path=f'../data/data/VIIRS_NRT/5000/{products_id}/2022', julian_day=str(date_ndays))
    laads_client.download_files_to_local_based_on_filelist(date, products_id=[products_id], collection_id='5000', data_path=f'../data/data/VIIRS_NRT/5000/{products_id}/2022', julian_day=str(date_ndays))

    fileList = viirs_preprocessing_and_upload(dataPath)
    pprint(fileList)
    
    # fileList = [
    #     "VNP09GA_NRT_A2021200_h10v03_001",
    #     "VNP09GA_NRT_A2021200_h11v03_001",
    # ]

    """ set property """
    import time, subprocess
    from datetime import datetime, timedelta

    fileListCopy = fileList.copy()
    imgCol_name = os.path.split(gs_dir)[-1]
    while(len(fileListCopy) > 0):
        print()
        pprint(fileListCopy)
        print("-------------------------------------------------------------------")
    
        response = subprocess.getstatusoutput(f"earthengine ls {VIIRS_NRT_ImgCol}")
        asset_list = response[1].replace("projects/earthengine-legacy/assets/", "").split("\n")

        for filename in fileList:
            asset_id = f"{VIIRS_NRT_ImgCol}/{filename}"  # VNP09GA_NRT_A2021198_h10v03_001
            julian_day = eval(filename.split("_")[2][5:])
            standard_date = datetime(year, 1, 1) + timedelta(days=julian_day)
            standard_date = standard_date.strftime("%Y-%m-%d")

            if asset_id in asset_list:
                # set_image_property(asset_id, query_info)
                os.system(f'earthengine asset set --time_start {standard_date} {asset_id}')
                # os.system(f'earthengine asset set --index {standard_date.replace("-","_")} {asset_id}')
                
                try:
                    fileListCopy.remove(filename)
                    print(f"{asset_id} [set time_start!]")
                except:
                    print(f"{asset_id} [failed to remove!]")
            else:
                print(f"{asset_id} [Not Ready in GEE!]")

        if(len(fileListCopy) > 0):
            time.sleep(60) # wait?