cfg = {
        # query parameters

        # "roi_url": "inputs/BC_ALB_ROI.geojson",
        # "start_date": None, # None for the day before today
        # "end_date": None, # None for the day after today

        "roi_url": "inputs/S1_vSplit_BC_ROI1.geojson",
        "start_date": "2021-07-30", # None for the day before today
        "end_date": "2021-07-31", # None for the day after today

        "platformname": "Sentinel-1", # Sentinel-2
        "producttype": 'GRD', # S2MSI1C, S2MSI2A

        # download parameters
        "download_flag": True,
        "datafolder": "D:/Sentinel_Hub", # where to save data

        "user": 'ahui0911', # ahui0911
        "password": '19940911', # 19940911
   
        # upload parameters
        "eeUser": "omegazhangpzh",
        "gs_dir": "gs://sar4wildfire/Sentinel1",
        "graph_url": "graphs/S1_GRD_preprocessing_GEE.xml"
    }