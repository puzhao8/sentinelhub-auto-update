import os, time, subprocess
from datetime import datetime, timedelta
from prettyprinter import PrettyPrinter as pprint

year = 2022
# filename = "MOD09GA_A2022214_h11v04_061_2022216032650"

eeUser = "omegazhangpzh"
eeImgColName = "MODIS_NRT"
response = subprocess.getstatusoutput(f"earthengine ls users/{eeUser}/{eeImgColName}")
asset_list = response[1].replace("projects/earthengine-legacy/assets/", "").split("\n")

print(asset_list)

for asset_id in asset_list:
    filename = os.path.split(asset_id)[-1]

    julian_day = eval(filename.split("_")[1][5:]) 
    standard_date = datetime(year, 1, 1) + timedelta(days=julian_day-1)
    standard_date = standard_date.strftime("%Y-%m-%d")

    print(filename, standard_date)
    os.system(f'earthengine asset set --time_start {standard_date} {asset_id}')