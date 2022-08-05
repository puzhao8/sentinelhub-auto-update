import os
import time 
import datetime as dt
from datetime import datetime, timedelta
import subprocess
import ee 
ee.Initialize()

eeUser = "omegazhangpzh"
# imgCol_name = "Sentinel1"


def del_sentinel_from_asset():
    today = datetime.today()
    date_th = (today - timedelta(days=4)).strftime("%Y%m%dT%H%M%S")
    julian_today_th = (today - datetime(2021, 1, 1)).days - 3

    print(date_th, julian_today_th)

    for imgCol_name in ["Sentinel1", "Sentinel2", "VIIRS_NRT"]:
        imgCol = f"users/{eeUser}/{imgCol_name}"
        print("---------------------------------------------------")
        print(imgCol)

        response = subprocess.getstatusoutput(f"earthengine ls users/{eeUser}/{imgCol_name}")
        asset_list = response[1].replace("projects/earthengine-legacy/assets/", "").split("\n")

        for asset_id in asset_list:
            filename = os.path.split(asset_id)[-1]

            if 'S2' in filename: 
                date = filename.split("_")[2] # S2A_MSIL1C_20210725T183921_N0301_R070_T11UNS_20210725T220603
                num = ee.ImageCollection("COPERNICUS/S2").filter(ee.Filter.eq("PRODUCT_ID", filename)).size().getInfo()

                if (date <= date_th) and (num > 0):
                    print(f"{filename} {num} [deleted!]")
                    os.system(f"earthengine rm {asset_id}")

            if 'S1' in filename: 
                date = filename.split("_")[4]
                num = ee.ImageCollection("COPERNICUS/S1_GRD").filter(ee.Filter.eq("system:index", filename)).size().getInfo()

                if (date <= date_th) and (num > 0):
                    print(f"{filename} {num} [deleted!]")
                    os.system(f"earthengine rm {asset_id}")

            if 'VNP09GA_NRT' in filename: 
                date = filename.split("_")[2][-3:] # VNP09GA_NRT_A2021199_h10v03_001
                if date <= str(julian_today_th):
                    print(f"{filename} {num} [deleted!]")
                    os.system(f"earthengine rm {asset_id}")

if __name__ == "__main__":

    while(True): 
        now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        hour = now.split("T")[-1]
        # print(hour)

        if "10:00:00" == hour:
            print(now)
            del_sentinel_from_asset()

        


