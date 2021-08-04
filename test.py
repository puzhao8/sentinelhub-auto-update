
import os, json
import time
from pathlib import Path
from easydict import EasyDict as edict
from prettyprinter import pprint

input_folder = Path("D:\Sentinel_Hub\data\S1_GRD")
fileList = [
            'S1B_IW_GRDH_1SDV_20210730T014710_20210730T014735_028017_03579F_DF69',
            'S1B_IW_GRDH_1SDV_20210730T014620_20210730T014645_028017_03579F_3D26',
            'S1B_IW_GRDH_1SDV_20210730T014735_20210730T014811_028017_03579F_7775'
        ]

def load_json(url) -> edict:
    with open(url, 'r') as fp:
        data = edict(json.load(fp))
    return data

task_dict_url =  "G:\PyProjects\sentinelhub-auto-update\logs\TASK_DICT_TEST.json"
if os.path.exists(task_dict_url): 
    History_TASK_DICT = load_json(task_dict_url)
else:
    History_TASK_DICT = {}
    
TASK_DICT = {}
fileListCopy = fileList.copy()

cnt = 0
max_time = 100 # 3*60*60 in seconds
start = time.time()
end = time.time()
while (len(fileListCopy) > 0):
    print(f"\n------------------- while {cnt}: {(end-start)/3600:.4f}h ---------------------")  

    fileList = fileListCopy.copy()
    for filename in fileList:            
        input_url = input_folder / f"{filename}.zip"

        # pprint(fileListCopy)

        # print(filename)
        # print(f"(filename in History_TASK_DICT.keys()): {(filename in History_TASK_DICT.keys())}")
        # print(f"filename in fileListCopy: {filename in fileListCopy}")
        # print(f"os.path.exists(input_url): {(os.path.exists(input_url))}")

        if (filename in History_TASK_DICT.keys()) and (filename in fileListCopy):
            fileListCopy.remove(filename)
            print(f"{filename} [uploaded already!]")

        if (filename not in History_TASK_DICT.keys()) and \
            (os.path.exists(input_url)) and \
                (filename in fileListCopy):

            print(f"{filename}: [uploaded!]")
            fileListCopy.remove(filename) # remove item from list after finishing uploading

            History_TASK_DICT.update({filename: filename})
            # save TASK_DICT
            with open(str(task_dict_url), 'w') as fp:
                json.dump(edict(History_TASK_DICT), fp, ensure_ascii=False, indent=4)

        if (filename not in History_TASK_DICT.keys()) and \
            (not os.path.exists(input_url)):
            print(f"{filename}: [not existed!]") 

    time.sleep(10)

    cnt = cnt + 1
    end = time.time()
    if end - start > max_time: break
    # time.sleep(10)
    




# dataPath = Path("D:\Sentinel_Hub\data\Tim")
# src_url = dataPath / "S2_L2A_20210728_Mosaic.tif"
# dst_url = dataPath / "S2_L2A_20210728_Mosaic_COG.tif"
# os.system(f"gdal_translate {src_url} {dst_url} -co TILED=YES -co COPY_SRC_OVERVIEWS=YES -co COMPRESS=LZW")


