import os, time, subprocess
from datetime import datetime, timedelta
from prettyprinter import PrettyPrinter as pprint


# filename = "MOD09GA_A2022214_h11v04_061_2022216032650"
# MOD09GA.A2022245.h01v08.061.2022246012115.NRT.hdf




def set_property_for_eeImgCol(eeImgColName, julian_day_list=[1], year=2022):
    eeUser = "omegazhangpzh"
    response = subprocess.getstatusoutput(f"earthengine ls users/{eeUser}/{eeImgColName}")
    asset_list = response[1].replace("projects/earthengine-legacy/assets/", "").split("\n")

    print(len(asset_list))

    for asset_id in asset_list:
        filename = os.path.split(asset_id)[-1]
        julian_day = eval(filename.split("_")[1][5:]) 

        if julian_day in julian_day_list:
            standard_date = datetime(year, 1, 1) + timedelta(days=julian_day-1)
            standard_date = standard_date.strftime("%Y-%m-%d")

            print(filename, standard_date)
            os.system(f'earthengine asset set --time_start {standard_date} {asset_id}')

        else:
            print(filename, julian_day)


if __name__ == "__main__":
    year = 2022
    eeImgColName = "MODIS_NRT"
    julian_day_list = [246]

    set_property_for_eeImgCol(eeImgColName, julian_day_list, year)