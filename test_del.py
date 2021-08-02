import os
import time 
import subprocess

eeUser = "omegazhangpzh"
imgCol_name = "Sentinel1"

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
            if date <= "20210727T000000":
                print(f"{filename} [deleted!]")
                # os.system(f"earthengine rm {asset_id}")

        if 'S1' in filename: 
            date = filename.split("_")[4]
            if date <= "20210727T000000":
                print(f"{filename} [deleted!]")
                os.system(f"earthengine rm {asset_id}")

        if 'VNP09GA_NRT' in filename: 
            date = filename.split("_")[2][-3:] # VNP09GA_NRT_A2021199_h10v03_001
            if date <= "205":
                print(f"{filename} [deleted!]")
                os.system(f"earthengine rm {asset_id}")

